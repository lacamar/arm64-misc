// SPDX-License-Identifier: MIT
// OpenGL ES renderer for Wayland surfaces.

#include "gpu_gles.hpp"

#include "log.hpp"

#include <EGL/eglext.h>

#include <algorithm>
#include <cmath>
#include <cstring>

namespace {

constexpr size_t BLUR_DOWNSCALE = 4;
constexpr size_t TEXTURE_BUDGET = 1024UL * 1024 * 1024;

constexpr Matrix3 SRGB_TO_BT2020 = { 0.6274040F, 0.3292820F, 0.0433136F,
                                     0.0690970F, 0.9195400F, 0.0113612F,
                                     0.0163916F, 0.0880132F, 0.8955950F };

constexpr const char* VERTEX = R"(#version 300 es
uniform vec2 viewport;
uniform vec4 dst;
uniform vec4 src;
layout(location = 0) in vec2 vertex;
out vec2 uv;
void main() {
    uv = mix(src.xy, src.zw, vertex);
    vec2 pos = (dst.xy + vertex * dst.zw) / viewport;
    gl_Position = vec4(pos * 2.0 - 1.0, 0.0, 1.0);
})";

// encoded pixels to premultiplied linear working space
constexpr const char* FRAG_DECODE = R"(#version 300 es
precision highp float;
uniform sampler2D tex;
uniform sampler2D table;
uniform int transfer;
uniform float gamma;
uniform mat3 matrix;
uniform vec3 luma;
in vec2 uv;
out vec4 color;
const float TABLE_SIZE = 4096.0;
vec3 eotf(vec3 v) {
    if (transfer == 0) {
        vec3 a = abs(v);
        return sign(v) * mix(a / 12.92, pow((a + 0.055) / 1.055, vec3(2.4)),
                             step(0.04045, a));
    }
    if (transfer == 2) {
        return sign(v) * pow(abs(v), vec3(gamma));
    }
    if (transfer == 3) {
        vec3 p = pow(clamp(v, 0.0, 1.0), vec3(1.0 / 78.84375));
        vec3 l = pow(max(p - 0.8359375, 0.0) / (18.8515625 - 18.6875 * p),
                     vec3(1.0 / 0.1593017578125));
        return l * (10000.0 / 203.0);
    }
    if (transfer == 4) {
        vec3 e = clamp(v, 0.0, 1.0);
        vec3 s = mix(e * e / 3.0,
                     (exp((e - 0.55991073) / 0.17883277) + 0.28466892) / 12.0,
                     step(0.5, e));
        return s * (1000.0 / 203.0) * pow(max(dot(luma, s), 1e-6), 0.2);
    }
    if (transfer == 5) {
        vec3 x = clamp(v, 0.0, 1.0) * ((TABLE_SIZE - 1.0) / TABLE_SIZE) +
            0.5 / TABLE_SIZE;
        return vec3(texture(table, vec2(x.r, 0.5 / 3.0)).r,
                    texture(table, vec2(x.g, 1.5 / 3.0)).r,
                    texture(table, vec2(x.b, 2.5 / 3.0)).r);
    }
    return v;
}
void main() {
    vec4 c = texture(tex, uv);
    color = vec4(matrix * eotf(c.rgb) * c.a, c.a);
})";

constexpr const char* FRAG_TEXTURE = R"(#version 300 es
precision highp float;
uniform sampler2D tex;
uniform mat3 matrix;
uniform bool premultiplied;
uniform float peak;
uniform float headroom;
in vec2 uv;
out vec4 color;
void main() {
    vec4 c = texture(tex, uv);
    vec3 rgb = c.rgb;
    if (premultiplied) {
        rgb = c.a > 0.0 ? rgb / c.a : vec3(0.0);
    }
    rgb = matrix * rgb;
    if (peak > headroom) {
        float knee = 0.75 * headroom;
        float m = max(rgb.r, max(rgb.g, rgb.b));
        if (m > knee) {
            float range = headroom - knee;
            float s = (m - knee) / range;
            float sp = (peak - knee) / range;
            rgb *= (knee + range * s * (1.0 + s / (sp * sp)) / (1.0 + s)) / m;
        }
    }
    color = vec4(rgb * c.a, c.a);
})";

constexpr const char* FRAG_SOLID = R"(#version 300 es
precision highp float;
uniform vec4 fill;
out vec4 color;
void main() {
    color = fill;
})";

constexpr const char* FRAG_MASK = R"(#version 300 es
precision highp float;
uniform sampler2D tex;
uniform vec4 fill;
in vec2 uv;
out vec4 color;
void main() {
    float a = min(texture(tex, uv).r, fill.a);
    color = vec4(fill.rgb * a, a);
})";

constexpr const char* FRAG_GRID = R"(#version 300 es
precision highp float;
uniform vec2 origin;
uniform float size;
uniform vec4 clr0;
uniform vec4 clr1;
out vec4 color;
void main() {
    vec2 cell = floor((gl_FragCoord.xy - origin) / size);
    color = mod(cell.x + cell.y, 2.0) >= 1.0 ? clr0 : clr1;
})";

constexpr const char* FRAG_BLUR = R"(#version 300 es
precision highp float;
uniform sampler2D tex;
uniform vec2 texel;
in vec2 uv;
out vec4 color;
const int RADIUS = 12;
const float SIGMA = 4.0;
void main() {
    vec4 sum = vec4(0.0);
    float total = 0.0;
    for (int i = -RADIUS; i <= RADIUS; ++i) {
        float w = exp(-float(i * i) / (2.0 * SIGMA * SIGMA));
        sum += texture(tex, uv + texel * float(i)) * w;
        total += w;
    }
    color = sum / total;
})";

// working space to output encoding
constexpr const char* FRAG_PRESENT = R"(#version 300 es
precision highp float;
uniform sampler2D tex;
uniform bool pq;
uniform mat3 matrix;
uniform float headroom;
uniform float dither;
in vec2 uv;
out vec4 color;
float noise(vec2 p) {
    return fract(52.9829189 * fract(dot(p, vec2(0.06711056, 0.00583715))));
}
void main() {
    vec4 c = texture(tex, uv);
    vec3 rgb = c.a > 0.0 ? c.rgb / c.a : vec3(0.0);
    rgb = clamp(matrix * rgb, 0.0, headroom);
    vec3 enc;
    if (pq) {
        vec3 p = pow(rgb * (203.0 / 10000.0), vec3(0.1593017578125));
        enc = pow((0.8359375 + 18.8515625 * p) / (1.0 + 18.6875 * p),
                  vec3(78.84375));
    } else {
        enc = mix(rgb * 12.92, 1.055 * pow(rgb, vec3(1.0 / 2.4)) - 0.055,
                  step(0.0031308, rgb));
    }
    float n = noise(gl_FragCoord.xy) +
        noise(gl_FragCoord.xy + vec2(47.0, 17.0)) - 1.0;
    enc = clamp(enc + n * dither, 0.0, 1.0);
    color = vec4(enc * c.a, c.a);
})";

GLuint compile_shader(const GLenum type, const char* source)
{
    const GLuint shader = glCreateShader(type);
    glShaderSource(shader, 1, &source, nullptr);
    glCompileShader(shader);
    GLint status = 0;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &status);
    if (!status) {
        char info[1024] = {};
        glGetShaderInfoLog(shader, sizeof(info), nullptr, info);
        Log::error("Failed to compile shader: {}", info);
        glDeleteShader(shader);
        return 0;
    }
    return shader;
}

GLuint compile(const char* fragment)
{
    const GLuint vs = compile_shader(GL_VERTEX_SHADER, VERTEX);
    const GLuint fs = compile_shader(GL_FRAGMENT_SHADER, fragment);
    GLuint program = 0;
    if (vs && fs) {
        program = glCreateProgram();
        glAttachShader(program, vs);
        glAttachShader(program, fs);
        glLinkProgram(program);
        GLint status = 0;
        glGetProgramiv(program, GL_LINK_STATUS, &status);
        if (!status) {
            Log::error("Failed to link shader program");
            glDeleteProgram(program);
            program = 0;
        }
    }
    glDeleteShader(vs);
    glDeleteShader(fs);
    return program;
}

bool has_extension(const char* name)
{
    GLint num = 0;
    glGetIntegerv(GL_NUM_EXTENSIONS, &num);
    for (GLint i = 0; i < num; ++i) {
        const auto* ext = reinterpret_cast<const char*>(
            glGetStringi(GL_EXTENSIONS, static_cast<GLuint>(i)));
        if (ext && std::strcmp(ext, name) == 0) {
            return true;
        }
    }
    return false;
}

float srgb_to_linear(const uint8_t value)
{
    const float v = value / 255.0F;
    return v <= 0.04045F ? v / 12.92F : std::pow((v + 0.055F) / 1.055F, 2.4F);
}

void set_filter(const GLint min, const GLint mag)
{
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, min);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, mag);
}

void set_wrap(const GLint wrap)
{
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, wrap);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, wrap);
}

void set_bgra_swizzle(const bool opaque)
{
    // pixmap is BGRA in memory
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_SWIZZLE_R, GL_BLUE);
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_SWIZZLE_B, GL_RED);
    if (opaque) {
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_SWIZZLE_A, GL_ONE);
    }
}

} // namespace

GpuGles::~GpuGles()
{
    if (egl_display != EGL_NO_DISPLAY) {
        eglMakeCurrent(egl_display, EGL_NO_SURFACE, EGL_NO_SURFACE,
                       EGL_NO_CONTEXT);
        if (egl_surface != EGL_NO_SURFACE) {
            eglDestroySurface(egl_display, egl_surface);
        }
        if (egl_context != EGL_NO_CONTEXT) {
            eglDestroyContext(egl_display, egl_context);
        }
        eglTerminate(egl_display);
    }
    if (egl_window) {
        wl_egl_window_destroy(egl_window);
    }
}

bool GpuGles::initialize(wl_display* display, wl_surface* surface,
                         const bool hdr)
{
    egl_display =
        eglGetPlatformDisplay(EGL_PLATFORM_WAYLAND_KHR, display, nullptr);
    if (egl_display == EGL_NO_DISPLAY ||
        !eglInitialize(egl_display, nullptr, nullptr)) {
        Log::error("Failed to initialize EGL display");
        return false;
    }
    if (!eglBindAPI(EGL_OPENGL_ES_API)) {
        Log::error("Failed to bind OpenGL ES API");
        return false;
    }

    deep_color = hdr && choose_config(true);
    if (!deep_color && !choose_config(false)) {
        Log::error("No suitable EGL config found");
        return false;
    }

    const EGLint context_attrs[] = { EGL_CONTEXT_MAJOR_VERSION, 3, EGL_NONE };
    egl_context = eglCreateContext(egl_display, egl_config, EGL_NO_CONTEXT,
                                   context_attrs);
    if (egl_context == EGL_NO_CONTEXT) {
        Log::error("Failed to create OpenGL ES 3 context");
        return false;
    }
    if (!eglMakeCurrent(egl_display, EGL_NO_SURFACE, EGL_NO_SURFACE,
                        egl_context)) {
        Log::error("Failed to activate OpenGL ES context");
        return false;
    }

    const bool rc = init_gl();
    // rendering may happen on another thread
    eglMakeCurrent(egl_display, EGL_NO_SURFACE, EGL_NO_SURFACE,
                   EGL_NO_CONTEXT);

    wl_surf = surface;

    return rc;
}

bool GpuGles::choose_config(const bool hdr)
{
    const EGLint bits = hdr ? 10 : 8;
    const EGLint alpha = hdr ? 2 : 8;
    const EGLint attrs[] = {
        EGL_SURFACE_TYPE,
        EGL_WINDOW_BIT,
        EGL_RENDERABLE_TYPE,
        EGL_OPENGL_ES3_BIT,
        EGL_RED_SIZE,
        bits,
        EGL_GREEN_SIZE,
        bits,
        EGL_BLUE_SIZE,
        bits,
        EGL_ALPHA_SIZE,
        alpha,
        EGL_NONE,
    };
    EGLint num = 0;
    eglChooseConfig(egl_display, attrs, nullptr, 0, &num);
    std::vector<EGLConfig> configs(num);
    eglChooseConfig(egl_display, attrs, configs.data(), num, &num);
    for (EGLConfig cfg : configs) {
        EGLint r = 0;
        EGLint g = 0;
        EGLint b = 0;
        EGLint a = 0;
        eglGetConfigAttrib(egl_display, cfg, EGL_RED_SIZE, &r);
        eglGetConfigAttrib(egl_display, cfg, EGL_GREEN_SIZE, &g);
        eglGetConfigAttrib(egl_display, cfg, EGL_BLUE_SIZE, &b);
        eglGetConfigAttrib(egl_display, cfg, EGL_ALPHA_SIZE, &a);
        if (r == bits && g == bits && b == bits && a == alpha) {
            egl_config = cfg;
            return true;
        }
    }
    return false;
}

bool GpuGles::init_gl()
{
    if (!has_extension("GL_EXT_color_buffer_half_float") &&
        !has_extension("GL_EXT_color_buffer_float")) {
        Log::error("Floating point render targets not supported");
        return false;
    }

    prog_texture = compile(FRAG_TEXTURE);
    prog_decode = compile(FRAG_DECODE);
    prog_solid = compile(FRAG_SOLID);
    prog_mask = compile(FRAG_MASK);
    prog_grid = compile(FRAG_GRID);
    prog_blur = compile(FRAG_BLUR);
    prog_present = compile(FRAG_PRESENT);
    if (!prog_texture || !prog_decode || !prog_solid || !prog_mask ||
        !prog_grid || !prog_blur || !prog_present) {
        return false;
    }

    use(prog_decode);
    glUniform1i(uniform("table"), 1);

    const float vertices[] = { 0, 0, 1, 0, 0, 1, 1, 1 };
    glGenVertexArrays(1, &vao);
    glBindVertexArray(vao);
    glGenBuffers(1, &vbo);
    glBindBuffer(GL_ARRAY_BUFFER, vbo);
    glBufferData(GL_ARRAY_BUFFER, sizeof(vertices), vertices, GL_STATIC_DRAW);
    glEnableVertexAttribArray(0);
    glVertexAttribPointer(0, 2, GL_FLOAT, GL_FALSE, 0, nullptr);

    glGetIntegerv(GL_MAX_TEXTURE_SIZE, &max_texture);
    glGenFramebuffers(1, &work_fbo);
    glBlendFunc(GL_ONE, GL_ONE_MINUS_SRC_ALPHA);
    glActiveTexture(GL_TEXTURE0);

    return glGetError() == GL_NO_ERROR;
}

void GpuGles::begin(const size_t width, const size_t height)
{
    if (!egl_window) {
        egl_window = wl_egl_window_create(wl_surf, static_cast<int>(width),
                                          static_cast<int>(height));
        egl_surface = eglCreatePlatformWindowSurface(egl_display, egl_config,
                                                     egl_window, nullptr);
        if (egl_surface == EGL_NO_SURFACE) {
            Log::error("Failed to create EGL surface");
        }
        eglMakeCurrent(egl_display, egl_surface, egl_surface, egl_context);
        eglSwapInterval(egl_display, 0);
    } else {
        if (width != frame_target.width || height != frame_target.height) {
            wl_egl_window_resize(egl_window, static_cast<int>(width),
                                 static_cast<int>(height), 0, 0);
        }
        eglMakeCurrent(egl_display, egl_surface, egl_surface, egl_context);
    }

    if (request_pq != output_pq) {
        output_pq = request_pq;
        if (on_encoding) {
            on_encoding(output_pq);
        }
    }

    resize(frame_target, width, height);
    glBindFramebuffer(GL_FRAMEBUFFER, frame_target.fbo);
    glViewport(0, 0, static_cast<GLsizei>(width), static_cast<GLsizei>(height));
    glDisable(GL_SCISSOR_TEST);
    glClearColor(0, 0, 0, 0);
    glClear(GL_COLOR_BUFFER_BIT);

    ++frame;
}

void GpuGles::set_output(const bool hdr, const float value)
{
    headroom = hdr ? std::max(value, 1.0F) : 1.0F;
    request_pq = hdr && deep_color;
}

void GpuGles::end()
{
    const auto width = static_cast<float>(frame_target.width);
    const auto height = static_cast<float>(frame_target.height);

    glBindFramebuffer(GL_FRAMEBUFFER, 0);
    glViewport(0, 0, static_cast<GLsizei>(width),
               static_cast<GLsizei>(height));
    glDisable(GL_SCISSOR_TEST);
    glDisable(GL_BLEND);

    use(prog_present);
    glBindTexture(GL_TEXTURE_2D, frame_target.tex);
    set_filter(GL_NEAREST, GL_NEAREST);
    glUniform1i(uniform("pq"), output_pq);
    glUniformMatrix3fv(uniform("matrix"), 1, GL_TRUE,
                       output_pq ? SRGB_TO_BT2020.data()
                                 : ColorSpace::IDENTITY.data());
    glUniform1f(uniform("headroom"), output_pq ? headroom.load() : 1.0F);
    glUniform1f(uniform("dither"), deep_color ? 1.0F / 1023 : 1.0F / 255);
    // offscreen frame is stored top-down
    quad(0, 0, width, height, 0, 1, 1, 0);

    if (!eglSwapBuffers(egl_display, egl_surface)) {
        Log::error("Failed to swap EGL buffers");
    }

    evict();
}

void GpuGles::fill(const Pixmap& dst, const Rectangle& rect,
                   const argb_t& color, const bool blend)
{
    if (!rect) {
        return;
    }

    bind(dst);
    use(prog_solid);
    if (blend) {
        glEnable(GL_BLEND);
    } else {
        glDisable(GL_BLEND);
    }
    set_color("fill", color, true);

    const Point org = dst.origin();
    quad(org.x + rect.x, org.y + rect.y, rect.width, rect.height);
}

void GpuGles::grid(const Pixmap& dst, const Rectangle& rect, const size_t size,
                   const argb_t& clr0, const argb_t& clr1)
{
    const Rectangle visible = rect.intersect({ 0, 0, dst.width(), dst.height() });
    if (!visible) {
        return;
    }

    bind(dst);
    use(prog_grid);
    glDisable(GL_BLEND);

    const Point org = dst.origin();
    const float x = org.x + visible.x;
    const float y = org.y + visible.y;
    glUniform2f(uniform("origin"), x, y);
    glUniform1f(uniform("size"), static_cast<float>(std::max(size, 1UL)));
    set_color("clr0", clr0, true);
    set_color("clr1", clr1, true);

    quad(x, y, visible.width, visible.height);
}

void GpuGles::mask(const Pixmap& dst, const Pixmap& src, const Point& pos,
                   const argb_t& color)
{
    if (!src) {
        return;
    }

    const Texture& texture = upload(src);

    bind(dst);
    use(prog_mask);
    glEnable(GL_BLEND);
    set_color("fill", color, false);

    const Point org = dst.origin();
    for (const Tile& tile : texture.tiles) {
        glBindTexture(GL_TEXTURE_2D, tile.tex);
        set_filter(GL_NEAREST, GL_NEAREST);
        quad(org.x + pos.x + tile.rect.x, org.y + pos.y + tile.rect.y,
             tile.rect.width, tile.rect.height);
    }
}

void GpuGles::draw(const Pixmap& dst, const Pixmap& src, const Point& pos,
                   const double scale, const bool antialiasing)
{
    if (!src || scale <= 0) {
        return;
    }

    Texture& texture = upload(src);

    const bool mipmap = antialiasing && scale < 1.0;
    if (mipmap && !texture.mipmaps) {
        for (const Tile& tile : texture.tiles) {
            glBindTexture(GL_TEXTURE_2D, tile.tex);
            glGenerateMipmap(GL_TEXTURE_2D);
        }
        texture.mipmaps = true;
        texture.bytes += texture.bytes / 3;
    }

    GLint min_filter = GL_NEAREST;
    GLint mag_filter = GL_NEAREST;
    if (antialiasing) {
        min_filter = mipmap ? GL_LINEAR_MIPMAP_LINEAR : GL_LINEAR;
        mag_filter = GL_LINEAR;
    }

    bind(dst);
    use(prog_texture);
    glUniformMatrix3fv(uniform("matrix"), 1, GL_TRUE, texture.matrix.data());
    glUniform1i(uniform("premultiplied"), texture.premultiplied);
    glUniform1f(uniform("peak"), texture.peak);
    glUniform1f(uniform("headroom"), output_pq ? headroom.load() : 1.0F);
    glEnable(GL_BLEND);

    const Point org = dst.origin();
    for (const Tile& tile : texture.tiles) {
        glBindTexture(GL_TEXTURE_2D, tile.tex);
        set_filter(min_filter, mag_filter);
        quad(org.x + pos.x + tile.rect.x * scale,
             org.y + pos.y + tile.rect.y * scale, tile.rect.width * scale,
             tile.rect.height * scale);
    }
}

void GpuGles::background(const Pixmap& dst, const Rectangle& preserve,
                         const bool mirror)
{
    const size_t width = dst.width();
    const size_t height = dst.height();
    const Rectangle full { 0, 0, width, height };
    const Rectangle exclude = full.intersect(preserve);
    if (!exclude) {
        return;
    }
    const Point org = dst.origin();

    resize(snapshot, exclude.width, exclude.height);
    glDisable(GL_SCISSOR_TEST);
    glBindFramebuffer(GL_READ_FRAMEBUFFER, frame_target.fbo);
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, snapshot.fbo);
    const auto sx = static_cast<GLint>(org.x + exclude.x);
    const auto sy = static_cast<GLint>(org.y + exclude.y);
    glBlitFramebuffer(sx, sy, sx + static_cast<GLint>(exclude.width),
                      sy + static_cast<GLint>(exclude.height), 0, 0,
                      static_cast<GLint>(exclude.width),
                      static_cast<GLint>(exclude.height), GL_COLOR_BUFFER_BIT,
                      GL_NEAREST);
    glBindTexture(GL_TEXTURE_2D, snapshot.tex);
    glGenerateMipmap(GL_TEXTURE_2D);
    set_filter(GL_LINEAR_MIPMAP_LINEAR, GL_LINEAR);
    set_wrap(mirror ? GL_MIRRORED_REPEAT : GL_CLAMP_TO_EDGE);

    const size_t bw = std::max(width / BLUR_DOWNSCALE, 1UL);
    const size_t bh = std::max(height / BLUR_DOWNSCALE, 1UL);
    resize(blur_target[0], bw, bh);
    resize(blur_target[1], bw, bh);

    glDisable(GL_BLEND);
    glBindFramebuffer(GL_FRAMEBUFFER, blur_target[0].fbo);
    glViewport(0, 0, static_cast<GLsizei>(bw), static_cast<GLsizei>(bh));
    use(prog_texture);
    glUniform2f(uniform("viewport"), width, height);
    glUniformMatrix3fv(uniform("matrix"), 1, GL_TRUE,
                       ColorSpace::IDENTITY.data());
    glUniform1i(uniform("premultiplied"), 1);
    glUniform1f(uniform("peak"), 1);
    glUniform1f(uniform("headroom"), 1);
    glBindTexture(GL_TEXTURE_2D, snapshot.tex);

    const float fw = width;
    const float fh = height;
    if (mirror) {
        const float ew = exclude.width;
        const float eh = exclude.height;
        quad(0, 0, fw, fh, -exclude.x / ew, -exclude.y / eh,
             (fw - exclude.x) / ew, (fh - exclude.y) / eh);
    } else {
        const float scale = std::max(fw / preserve.width, fh / preserve.height);
        const float sw = exclude.width * scale;
        const float sh = exclude.height * scale;
        const float x = fw / 2 - sw / 2;
        const float y = fh / 2 - sh / 2;
        quad(0, 0, fw, fh, -x / sw, -y / sh, (fw - x) / sw, (fh - y) / sh);
    }

    use(prog_blur);
    glUniform2f(uniform("viewport"), width, height);
    glBindFramebuffer(GL_FRAMEBUFFER, blur_target[1].fbo);
    glBindTexture(GL_TEXTURE_2D, blur_target[0].tex);
    glUniform2f(uniform("texel"), 1.0F / bw, 0);
    quad(0, 0, fw, fh);
    glBindFramebuffer(GL_FRAMEBUFFER, blur_target[0].fbo);
    glBindTexture(GL_TEXTURE_2D, blur_target[1].tex);
    glUniform2f(uniform("texel"), 0, 1.0F / bh);
    quad(0, 0, fw, fh);

    bind(dst);
    use(prog_texture);
    glUniformMatrix3fv(uniform("matrix"), 1, GL_TRUE,
                       ColorSpace::IDENTITY.data());
    glUniform1i(uniform("premultiplied"), 1);
    glUniform1f(uniform("peak"), 1);
    glUniform1f(uniform("headroom"), 1);
    glBindTexture(GL_TEXTURE_2D, blur_target[0].tex);
    const auto [top, bottom, left, right] = full.cutout(exclude);
    for (const Rectangle& r : { top, bottom, left, right }) {
        if (r) {
            quad(org.x + r.x, org.y + r.y, r.width, r.height, r.x / fw,
                 r.y / fh, (r.x + r.width) / fw, (r.y + r.height) / fh);
        }
    }
}

GpuGles::Texture& GpuGles::upload(const Pixmap& pm)
{
    const auto [it, inserted] = textures.try_emplace(pm.id());
    Texture& texture = it->second;
    texture.frame = frame;
    if (!inserted) {
        return texture;
    }

    static const ColorSpace srgb;
    const ColorSpace& cs = pm.color() ? *pm.color() : srgb;
    const bool gs = pm.format() == Pixmap::GS;
    const bool f16 = pm.format() == Pixmap::F16;
    const bool direct =
        gs || (!f16 && cs.transfer == ColorSpace::Transfer::SRGB);

    texture.peak = cs.peak;
    texture.matrix = direct ? cs.matrix : ColorSpace::IDENTITY;
    texture.premultiplied = !direct;

    GLuint table = 0;
    if (!direct && cs.transfer == ColorSpace::Transfer::Table) {
        glGenTextures(1, &table);
        glBindTexture(GL_TEXTURE_2D, table);
        glTexImage2D(GL_TEXTURE_2D, 0, GL_R16F, ColorSpace::TABLE_SIZE, 3, 0,
                     GL_RED, GL_FLOAT, cs.table.data());
        set_filter(GL_LINEAR, GL_LINEAR);
        set_wrap(GL_CLAMP_TO_EDGE);
    }

    const size_t bpp = gs ? 1 : (f16 ? 4 * sizeof(uint16_t) : sizeof(argb_t));
    const auto max = static_cast<size_t>(max_texture);

    for (size_t y = 0; y < pm.height(); y += max) {
        for (size_t x = 0; x < pm.width(); x += max) {
            const size_t w = std::min(max, pm.width() - x);
            const size_t h = std::min(max, pm.height() - y);
            const Rectangle rect(static_cast<ssize_t>(x),
                                 static_cast<ssize_t>(y), w, h);
            glPixelStorei(GL_UNPACK_ALIGNMENT, 1);
            glPixelStorei(GL_UNPACK_ROW_LENGTH,
                          static_cast<GLint>(pm.stride() / bpp));
            Tile tile { .tex = 0, .rect = rect };
            if (!direct) {
                tile.tex = decode(pm, rect, cs, table);
                texture.bytes += w * h * 8;
            } else {
                glGenTextures(1, &tile.tex);
                glBindTexture(GL_TEXTURE_2D, tile.tex);
                if (gs) {
                    glTexImage2D(GL_TEXTURE_2D, 0, GL_R8, w, h, 0, GL_RED,
                                 GL_UNSIGNED_BYTE, pm.ptr(x, y));
                    texture.bytes += w * h;
                } else {
                    glTexImage2D(GL_TEXTURE_2D, 0, GL_SRGB8_ALPHA8, w, h, 0,
                                 GL_RGBA, GL_UNSIGNED_BYTE, pm.ptr(x, y));
                    set_bgra_swizzle(pm.format() == Pixmap::RGB);
                    texture.bytes += w * h * 4;
                }
                set_wrap(GL_CLAMP_TO_EDGE);
            }
            texture.tiles.push_back(tile);
        }
    }

    glPixelStorei(GL_UNPACK_ROW_LENGTH, 0);
    if (table) {
        glDeleteTextures(1, &table);
    }

    return texture;
}

GLuint GpuGles::decode(const Pixmap& pm, const Rectangle& rect,
                       const ColorSpace& cs, const GLuint table)
{
    const auto w = static_cast<GLsizei>(rect.width);
    const auto h = static_cast<GLsizei>(rect.height);

    GLuint src = 0;
    glGenTextures(1, &src);
    glBindTexture(GL_TEXTURE_2D, src);
    if (pm.format() == Pixmap::F16) {
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, w, h, 0, GL_RGBA,
                     GL_HALF_FLOAT, pm.ptr(rect.x, rect.y));
    } else {
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA8, w, h, 0, GL_RGBA,
                     GL_UNSIGNED_BYTE, pm.ptr(rect.x, rect.y));
        set_bgra_swizzle(pm.format() == Pixmap::RGB);
    }
    set_filter(GL_NEAREST, GL_NEAREST);
    set_wrap(GL_CLAMP_TO_EDGE);

    GLuint dst = 0;
    glGenTextures(1, &dst);
    glBindTexture(GL_TEXTURE_2D, dst);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, w, h, 0, GL_RGBA, GL_HALF_FLOAT,
                 nullptr);
    set_filter(GL_LINEAR, GL_LINEAR);
    set_wrap(GL_CLAMP_TO_EDGE);

    glBindFramebuffer(GL_FRAMEBUFFER, work_fbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D,
                           dst, 0);
    glViewport(0, 0, w, h);
    glDisable(GL_SCISSOR_TEST);
    glDisable(GL_BLEND);

    use(prog_decode);
    glUniform2f(uniform("viewport"), rect.width, rect.height);
    glUniform1i(uniform("transfer"), static_cast<GLint>(cs.transfer));
    glUniform1f(uniform("gamma"), cs.gamma);
    glUniformMatrix3fv(uniform("matrix"), 1, GL_TRUE, cs.matrix.data());
    glUniform3f(uniform("luma"), cs.luma[0], cs.luma[1], cs.luma[2]);
    if (table) {
        glActiveTexture(GL_TEXTURE1);
        glBindTexture(GL_TEXTURE_2D, table);
        glActiveTexture(GL_TEXTURE0);
    }
    glBindTexture(GL_TEXTURE_2D, src);
    quad(0, 0, rect.width, rect.height);

    glDeleteTextures(1, &src);

    return dst;
}

void GpuGles::evict()
{
    size_t total = 0;
    std::vector<decltype(textures)::iterator> unused;
    for (auto it = textures.begin(); it != textures.end(); ++it) {
        total += it->second.bytes;
        if (it->second.frame != frame) {
            unused.push_back(it);
        }
    }

    std::ranges::sort(unused, [](const auto& a, const auto& b) {
        return a->second.frame < b->second.frame;
    });

    for (const auto& it : unused) {
        if (total <= TEXTURE_BUDGET) {
            break;
        }
        total -= it->second.bytes;
        for (const Tile& tile : it->second.tiles) {
            glDeleteTextures(1, &tile.tex);
        }
        textures.erase(it);
    }
}

void GpuGles::resize(Target& target, const size_t width, const size_t height)
{
    if (target.fbo && target.width == width && target.height == height) {
        return;
    }
    if (!target.fbo) {
        glGenFramebuffers(1, &target.fbo);
        glGenTextures(1, &target.tex);
    }

    glBindTexture(GL_TEXTURE_2D, target.tex);
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA16F, static_cast<GLsizei>(width),
                 static_cast<GLsizei>(height), 0, GL_RGBA, GL_HALF_FLOAT,
                 nullptr);
    set_filter(GL_LINEAR, GL_LINEAR);
    set_wrap(GL_CLAMP_TO_EDGE);

    glBindFramebuffer(GL_FRAMEBUFFER, target.fbo);
    glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D,
                           target.tex, 0);

    target.width = width;
    target.height = height;
}

void GpuGles::bind(const Pixmap& dst)
{
    const Point org = dst.origin();
    glBindFramebuffer(GL_FRAMEBUFFER, frame_target.fbo);
    glViewport(0, 0, static_cast<GLsizei>(frame_target.width),
               static_cast<GLsizei>(frame_target.height));
    glEnable(GL_SCISSOR_TEST);
    glScissor(static_cast<GLint>(org.x), static_cast<GLint>(org.y),
              static_cast<GLsizei>(dst.width()),
              static_cast<GLsizei>(dst.height()));
}

void GpuGles::use(const GLuint program)
{
    glUseProgram(program);
    current = program;
    glUniform2f(uniform("viewport"), frame_target.width, frame_target.height);
}

void GpuGles::set_color(const char* name, const argb_t& color,
                        const bool premultiply)
{
    const float a = color.a / 255.0F;
    const float k = premultiply ? a : 1.0F;
    glUniform4f(uniform(name), srgb_to_linear(color.r) * k,
                srgb_to_linear(color.g) * k, srgb_to_linear(color.b) * k, a);
}

void GpuGles::quad(const float x, const float y, const float w, const float h,
                   const float u0, const float v0, const float u1,
                   const float v1)
{
    glUniform4f(uniform("dst"), x, y, w, h);
    glUniform4f(uniform("src"), u0, v0, u1, v1);
    glDrawArrays(GL_TRIANGLE_STRIP, 0, 4);
}

GLint GpuGles::uniform(const char* name) const
{
    return glGetUniformLocation(current, name);
}
