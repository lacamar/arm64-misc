// SPDX-License-Identifier: MIT
// OpenGL ES renderer for Wayland surfaces.

#pragma once

#include "pixmap.hpp"

#include <EGL/egl.h>
#include <GLES3/gl3.h>
#include <wayland-egl.h>

#include <atomic>
#include <functional>
#include <unordered_map>
#include <vector>

class GpuGles : public Gpu {
public:
    ~GpuGles() override;

    bool initialize(wl_display* display, wl_surface* surface, bool hdr);
    void begin(size_t width, size_t height);
    void end();

    [[nodiscard]] bool hdr_capable() const { return deep_color; }
    void set_output(bool hdr, float value);

    std::function<void(bool)> on_encoding;

    void fill(const Pixmap& dst, const Rectangle& rect, const argb_t& color,
              bool blend) override;
    void grid(const Pixmap& dst, const Rectangle& rect, size_t size,
              const argb_t& clr0, const argb_t& clr1) override;
    void mask(const Pixmap& dst, const Pixmap& src, const Point& pos,
              const argb_t& color) override;
    void draw(const Pixmap& dst, const Pixmap& src, const Point& pos,
              double scale, bool antialiasing) override;
    void background(const Pixmap& dst, const Rectangle& preserve,
                    bool mirror) override;

private:
    struct Tile {
        GLuint tex;
        Rectangle rect;
    };
    struct Texture {
        std::vector<Tile> tiles;
        Matrix3 matrix = ColorSpace::IDENTITY;
        float peak = 1.0F;
        bool premultiplied = false;
        bool mipmaps = false;
        size_t bytes = 0;
        uint64_t frame = 0;
    };
    struct Target {
        GLuint fbo = 0;
        GLuint tex = 0;
        size_t width = 0;
        size_t height = 0;
    };

    bool choose_config(bool hdr);
    bool init_gl();
    Texture& upload(const Pixmap& pm);
    GLuint decode(const Pixmap& pm, const Rectangle& rect,
                  const ColorSpace& cs, GLuint table);
    void evict();
    void resize(Target& target, size_t width, size_t height);
    void bind(const Pixmap& dst);
    void use(GLuint program);
    void set_color(const char* name, const argb_t& color, bool premultiply);
    void quad(float x, float y, float w, float h, float u0 = 0, float v0 = 0,
              float u1 = 1, float v1 = 1);
    GLint uniform(const char* name) const;

    EGLDisplay egl_display = EGL_NO_DISPLAY;
    EGLConfig egl_config = nullptr;
    EGLContext egl_context = EGL_NO_CONTEXT;
    EGLSurface egl_surface = EGL_NO_SURFACE;
    wl_surface* wl_surf = nullptr;
    wl_egl_window* egl_window = nullptr;

    bool deep_color = false;
    bool output_pq = false;
    std::atomic<bool> request_pq = false;
    std::atomic<float> headroom = 1.0F;

    GLuint prog_texture = 0;
    GLuint prog_decode = 0;
    GLuint prog_solid = 0;
    GLuint prog_mask = 0;
    GLuint prog_grid = 0;
    GLuint prog_blur = 0;
    GLuint prog_present = 0;
    GLuint current = 0;
    GLuint vao = 0;
    GLuint vbo = 0;
    GLuint work_fbo = 0;
    GLint max_texture = 0;

    Target frame_target;
    Target snapshot;
    Target blur_target[2];

    std::unordered_map<uint64_t, Texture> textures;
    uint64_t frame = 0;
};
