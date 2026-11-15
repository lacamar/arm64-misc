// SPDX-License-Identifier: MIT
// Color spaces and color management.

#include "colorspace.hpp"

#include "pixmap.hpp"

#include <lcms2.h>

#include <algorithm>
#include <cmath>
#include <cstring>
#include <thread>

bool ColorSpace::native = false;

namespace {

using Mat = std::array<double, 9>;
using Vec = std::array<double, 3>;

constexpr std::array<float, 8> SRGB_XY = { 0.640F, 0.330F, 0.300F, 0.600F,
                                           0.150F, 0.060F, 0.3127F, 0.3290F };
constexpr Vec D50 = { 0.9642, 1.0, 0.8249 };

constexpr double PQ_M1 = 0.1593017578125;
constexpr double PQ_M2 = 78.84375;
constexpr double PQ_C1 = 0.8359375;
constexpr double PQ_C2 = 18.8515625;
constexpr double PQ_C3 = 18.6875;
constexpr double HLG_A = 0.17883277;
constexpr double HLG_B = 0.28466892;
constexpr double HLG_C = 0.55991073;

Mat mul(const Mat& a, const Mat& b)
{
    Mat r {};
    for (size_t i = 0; i < 3; ++i) {
        for (size_t j = 0; j < 3; ++j) {
            for (size_t k = 0; k < 3; ++k) {
                r[i * 3 + j] += a[i * 3 + k] * b[k * 3 + j];
            }
        }
    }
    return r;
}

Vec mul(const Mat& m, const Vec& v)
{
    return { m[0] * v[0] + m[1] * v[1] + m[2] * v[2],
             m[3] * v[0] + m[4] * v[1] + m[5] * v[2],
             m[6] * v[0] + m[7] * v[1] + m[8] * v[2] };
}

Mat inverse(const Mat& m)
{
    const double det = m[0] * (m[4] * m[8] - m[5] * m[7]) -
        m[1] * (m[3] * m[8] - m[5] * m[6]) + m[2] * (m[3] * m[7] - m[4] * m[6]);
    const double k = 1.0 / det;
    return { (m[4] * m[8] - m[5] * m[7]) * k, (m[2] * m[7] - m[1] * m[8]) * k,
             (m[1] * m[5] - m[2] * m[4]) * k, (m[5] * m[6] - m[3] * m[8]) * k,
             (m[0] * m[8] - m[2] * m[6]) * k, (m[2] * m[3] - m[0] * m[5]) * k,
             (m[3] * m[7] - m[4] * m[6]) * k, (m[1] * m[6] - m[0] * m[7]) * k,
             (m[0] * m[4] - m[1] * m[3]) * k };
}

Vec xy_to_xyz(const double x, const double y)
{
    return { x / y, 1.0, (1.0 - x - y) / y };
}

Mat rgb_to_xyz(const std::array<float, 8>& xy)
{
    const Vec r = xy_to_xyz(xy[0], xy[1]);
    const Vec g = xy_to_xyz(xy[2], xy[3]);
    const Vec b = xy_to_xyz(xy[4], xy[5]);
    const Mat p = { r[0], g[0], b[0], r[1], g[1], b[1], r[2], g[2], b[2] };
    const Vec s = mul(inverse(p), xy_to_xyz(xy[6], xy[7]));
    return { p[0] * s[0], p[1] * s[1], p[2] * s[2], p[3] * s[0], p[4] * s[1],
             p[5] * s[2], p[6] * s[0], p[7] * s[1], p[8] * s[2] };
}

Mat bradford(const Vec& src, const Vec& dst)
{
    constexpr Mat BFD = { 0.8951,  0.2664, -0.1614, -0.7502, 1.7135,
                          0.0367,  0.0389, -0.0685, 1.0296 };
    const Vec s = mul(BFD, src);
    const Vec d = mul(BFD, dst);
    const Mat scale = { d[0] / s[0], 0, 0, 0, d[1] / s[1], 0, 0, 0,
                        d[2] / s[2] };
    return mul(inverse(BFD), mul(scale, BFD));
}

const Mat& srgb_to_xyz()
{
    static const Mat m = rgb_to_xyz(SRGB_XY);
    return m;
}

const Mat& xyz_to_srgb()
{
    static const Mat m = inverse(srgb_to_xyz());
    return m;
}

void set_matrix(ColorSpace& cs, const Mat& m)
{
    double dev = 0;
    for (size_t i = 0; i < 9; ++i) {
        dev = std::max(dev, std::abs(m[i] - ColorSpace::IDENTITY[i]));
    }
    for (size_t i = 0; i < 9; ++i) {
        cs.matrix[i] = dev < 2e-3 ? ColorSpace::IDENTITY[i]
                                  : static_cast<float>(m[i]);
    }
    const Mat& xyz = srgb_to_xyz();
    for (size_t i = 0; i < 3; ++i) {
        cs.luma[i] = static_cast<float>(xyz[3] * cs.matrix[i] +
                                        xyz[4] * cs.matrix[3 + i] +
                                        xyz[5] * cs.matrix[6 + i]);
    }
}

double srgb_eotf(const double v)
{
    const double a = std::abs(v);
    return std::copysign(
        a <= 0.04045 ? a / 12.92 : std::pow((a + 0.055) / 1.055, 2.4), v);
}

double srgb_oetf(const double v)
{
    return v <= 0.0031308 ? v * 12.92
                          : 1.055 * std::pow(v, 1.0 / 2.4) - 0.055;
}

double pq_eotf(const double v)
{
    const double p = std::pow(std::clamp(v, 0.0, 1.0), 1.0 / PQ_M2);
    const double l =
        std::pow(std::max(p - PQ_C1, 0.0) / (PQ_C2 - PQ_C3 * p), 1.0 / PQ_M1);
    return l * 10000.0 / ColorSpace::REFERENCE_WHITE;
}

double hlg_inverse_oetf(double v)
{
    v = std::clamp(v, 0.0, 1.0);
    return v <= 0.5 ? v * v / 3.0 : (std::exp((v - HLG_C) / HLG_A) + HLG_B) / 12.0;
}

using Profile = std::unique_ptr<void, decltype(&cmsCloseProfile)>;

} // namespace

std::shared_ptr<ColorSpace> ColorSpace::from_cicp(const uint16_t primaries,
                                                  const uint16_t transfer)
{
    std::array<float, 8> xy = SRGB_XY;
    switch (primaries) {
        case 4: // BT.470M
            xy = { 0.67F, 0.33F, 0.21F, 0.71F, 0.14F, 0.08F, 0.310F, 0.316F };
            break;
        case 5: // BT.601 625
            xy = { 0.64F, 0.33F, 0.29F, 0.60F, 0.15F, 0.06F, 0.3127F, 0.3290F };
            break;
        case 6: // BT.601 525
        case 7: // SMPTE 240M
            xy = { 0.630F, 0.340F, 0.310F, 0.595F,
                   0.155F, 0.070F, 0.3127F, 0.3290F };
            break;
        case 9: // BT.2020
            xy = { 0.708F, 0.292F, 0.170F, 0.797F,
                   0.131F, 0.046F, 0.3127F, 0.3290F };
            break;
        case 11: // DCI-P3
            xy = { 0.680F, 0.320F, 0.265F, 0.690F,
                   0.150F, 0.060F, 0.314F,  0.351F };
            break;
        case 12: // Display P3
            xy = { 0.680F, 0.320F, 0.265F, 0.690F,
                   0.150F, 0.060F, 0.3127F, 0.3290F };
            break;
        case 22: // EBU 3213
            xy = { 0.630F, 0.340F, 0.295F, 0.605F,
                   0.155F, 0.077F, 0.3127F, 0.3290F };
            break;
        default:
            break;
    }

    switch (transfer) {
        case 1:
        case 6:
        case 14:
        case 15: // BT.709/BT.2020 camera curve, displayed with BT.1886
            return from_chromaticities(xy, Transfer::Gamma, 2.4F);
        case 4:
            return from_chromaticities(xy, Transfer::Gamma, 2.2F);
        case 5:
            return from_chromaticities(xy, Transfer::Gamma, 2.8F);
        case 8:
            return from_chromaticities(xy, Transfer::Linear);
        case 16:
            return from_chromaticities(xy, Transfer::PQ);
        case 18:
            return from_chromaticities(xy, Transfer::HLG);
        default:
            return from_chromaticities(xy, Transfer::SRGB);
    }
}

std::shared_ptr<ColorSpace>
ColorSpace::from_chromaticities(const std::array<float, 8>& xy,
                                const Transfer transfer, const float gamma)
{
    auto cs = std::make_shared<ColorSpace>();
    cs->transfer = transfer;
    cs->gamma = gamma;
    const Vec d65 = xy_to_xyz(SRGB_XY[6], SRGB_XY[7]);
    const Mat adapt = bradford(xy_to_xyz(xy[6], xy[7]), d65);
    set_matrix(*cs, mul(xyz_to_srgb(), mul(adapt, rgb_to_xyz(xy))));
    if (transfer == Transfer::PQ || transfer == Transfer::HLG) {
        cs->set_peak_nits(HDR_PEAK);
    }
    return cs;
}

std::shared_ptr<ColorSpace> ColorSpace::from_icc(const void* data,
                                                 const size_t size)
{
    if (!data || !size) {
        return nullptr;
    }
    const Profile profile(
        cmsOpenProfileFromMem(data, static_cast<cmsUInt32Number>(size)),
        &cmsCloseProfile);
    if (!profile || !cmsIsMatrixShaper(profile.get())) {
        return nullptr;
    }

    const cmsColorSpaceSignature sig = cmsGetColorSpace(profile.get());
    std::array<cmsTagSignature, 3> trc;
    auto cs = std::make_shared<ColorSpace>();
    if (sig == cmsSigRgbData) {
        trc = { cmsSigRedTRCTag, cmsSigGreenTRCTag, cmsSigBlueTRCTag };
        const auto* r = static_cast<const cmsCIEXYZ*>(
            cmsReadTag(profile.get(), cmsSigRedColorantTag));
        const auto* g = static_cast<const cmsCIEXYZ*>(
            cmsReadTag(profile.get(), cmsSigGreenColorantTag));
        const auto* b = static_cast<const cmsCIEXYZ*>(
            cmsReadTag(profile.get(), cmsSigBlueColorantTag));
        if (!r || !g || !b) {
            return nullptr;
        }
        const Mat d50 = { r->X, g->X, b->X, r->Y, g->Y, b->Y, r->Z, g->Z, b->Z };
        const Mat adapt = bradford(D50, xy_to_xyz(SRGB_XY[6], SRGB_XY[7]));
        set_matrix(*cs, mul(xyz_to_srgb(), mul(adapt, d50)));
    } else if (sig == cmsSigGrayData) {
        trc = { cmsSigGrayTRCTag, cmsSigGrayTRCTag, cmsSigGrayTRCTag };
    } else {
        return nullptr;
    }

    cs->table.resize(TABLE_SIZE * 3);
    for (size_t c = 0; c < 3; ++c) {
        const auto* curve =
            static_cast<const cmsToneCurve*>(cmsReadTag(profile.get(), trc[c]));
        if (!curve) {
            return nullptr;
        }
        for (size_t i = 0; i < TABLE_SIZE; ++i) {
            cs->table[c * TABLE_SIZE + i] = cmsEvalToneCurveFloat(
                curve, static_cast<float>(i) / (TABLE_SIZE - 1));
        }
    }

    const auto deviation = [&cs](auto&& fn) {
        double dev = 0;
        for (size_t c = 0; c < 3; ++c) {
            for (size_t i = 0; i < TABLE_SIZE; ++i) {
                const double x = static_cast<double>(i) / (TABLE_SIZE - 1);
                dev = std::max(dev,
                               std::abs(cs->table[c * TABLE_SIZE + i] - fn(x)));
            }
        }
        return dev;
    };
    const double mid = cs->table[TABLE_SIZE / 2];
    const double gamma =
        std::log(std::max(mid, 1e-6)) / std::log(0.5 * TABLE_SIZE / (TABLE_SIZE - 1));

    if (deviation(srgb_eotf) < 2e-3) {
        cs->transfer = Transfer::SRGB;
    } else if (deviation([](double x) { return x; }) < 1e-3) {
        cs->transfer = Transfer::Linear;
    } else if (deviation([gamma](double x) { return std::pow(x, gamma); }) <
               2e-3) {
        cs->transfer = Transfer::Gamma;
        cs->gamma = static_cast<float>(gamma);
    } else {
        cs->transfer = Transfer::Table;
        return cs;
    }
    cs->table.clear();
    return cs;
}

void ColorSpace::apply_icc(Pixmap& pm, const void* data, const size_t size)
{
    if (const auto cs = from_icc(data, size)) {
        if (!cs->is_srgb()) {
            pm.set_color(cs);
        }
        return;
    }

    const Profile in(
        cmsOpenProfileFromMem(data, static_cast<cmsUInt32Number>(size)),
        &cmsCloseProfile);
    if (!in || cmsGetColorSpace(in.get()) != cmsSigRgbData) {
        return;
    }
    const Profile out(cmsCreate_sRGBProfile(), &cmsCloseProfile);
    const cmsUInt32Number fmt =
        pm.format() == Pixmap::F16 ? TYPE_RGBA_HALF_FLT : TYPE_BGRA_8;
    cmsHTRANSFORM transform =
        cmsCreateTransform(in.get(), fmt, out.get(), fmt, INTENT_PERCEPTUAL,
                           cmsFLAGS_COPY_ALPHA);
    if (!transform) {
        return;
    }
    std::vector<uint8_t> buffer(pm.width() * (pm.stride() / pm.width()));
    for (size_t y = 0; y < pm.height(); ++y) {
        void* line = pm.ptr(0, y);
        std::memcpy(buffer.data(), line, buffer.size());
        cmsDoTransform(transform, buffer.data(), line,
                       static_cast<cmsUInt32Number>(pm.width()));
    }
    cmsDeleteTransform(transform);
}

bool ColorSpace::needs_conversion(const Pixmap& pm)
{
    return pm.format() == Pixmap::F16 || (pm.color() && !pm.color()->is_srgb());
}

Pixmap ColorSpace::to_srgb(const Pixmap& pm)
{
    static const ColorSpace srgb;
    const ColorSpace& cs = pm.color() ? *pm.color() : srgb;
    const bool f16 = pm.format() == Pixmap::F16;

    Pixmap out;
    out.create(pm.format() == Pixmap::RGB ? Pixmap::RGB : Pixmap::ARGB,
               pm.width(), pm.height());

    std::vector<float> dec8;
    if (!f16) {
        dec8.resize(256 * 3);
        for (size_t c = 0; c < 3; ++c) {
            for (size_t i = 0; i < 256; ++i) {
                dec8[c * 256 + i] = cs.decode(i / 255.0F, c);
            }
        }
    }
    static const std::vector<uint8_t> enc = [] {
        std::vector<uint8_t> t(16384);
        for (size_t i = 0; i < t.size(); ++i) {
            const double v = srgb_oetf(static_cast<double>(i) / (t.size() - 1));
            t[i] = static_cast<uint8_t>(std::lround(v * 255));
        }
        return t;
    }();

    const auto worker = [&](const size_t from, const size_t to) {
        for (size_t y = from; y < to; ++y) {
            for (size_t x = 0; x < pm.width(); ++x) {
                float rgb[3];
                float alpha;
                if (f16) {
                    const auto* px = static_cast<const uint16_t*>(pm.ptr(x, y));
                    for (size_t c = 0; c < 3; ++c) {
                        rgb[c] = cs.decode(half_to_float(px[c]), c);
                    }
                    alpha = std::clamp(half_to_float(px[3]), 0.0F, 1.0F);
                } else {
                    const argb_t& px = pm.at(x, y);
                    rgb[0] = dec8[px.r];
                    rgb[1] = dec8[256 + px.g];
                    rgb[2] = dec8[512 + px.b];
                    alpha = px.a / 255.0F;
                }
                if (cs.transfer == Transfer::HLG) {
                    const float lum =
                        cs.luma[0] * rgb[0] + cs.luma[1] * rgb[1] + cs.luma[2] * rgb[2];
                    const float k = HDR_PEAK / REFERENCE_WHITE *
                        std::pow(std::max(lum, 1e-6F), 0.2F);
                    for (float& v : rgb) {
                        v *= k;
                    }
                }
                const Matrix3& m = cs.matrix;
                const float lin[3] = {
                    m[0] * rgb[0] + m[1] * rgb[1] + m[2] * rgb[2],
                    m[3] * rgb[0] + m[4] * rgb[1] + m[5] * rgb[2],
                    m[6] * rgb[0] + m[7] * rgb[1] + m[8] * rgb[2],
                };
                std::copy(lin, lin + 3, rgb);
                tonemap(rgb, cs.peak, 1.0F);

                const auto encode = [](const float v) {
                    return enc[static_cast<size_t>(std::clamp(v, 0.0F, 1.0F) *
                                                   (enc.size() - 1))];
                };
                out.at(x, y) = argb_t(static_cast<uint8_t>(std::lround(alpha * 255)),
                                      encode(rgb[0]), encode(rgb[1]),
                                      encode(rgb[2]));
            }
        }
    };

    const size_t threads = std::clamp<size_t>(
        std::min<size_t>(std::thread::hardware_concurrency(),
                         pm.height() / 64),
        1, 64);
    std::vector<std::thread> pool;
    const size_t step = pm.height() / threads;
    for (size_t i = 0; i < threads; ++i) {
        const size_t from = i * step;
        const size_t to = i == threads - 1 ? pm.height() : from + step;
        pool.emplace_back(worker, from, to);
    }
    for (auto& t : pool) {
        t.join();
    }

    return out;
}

void ColorSpace::tonemap(float rgb[3], const float peak, const float headroom)
{
    if (peak <= headroom) {
        return;
    }
    const float knee = 0.75F * headroom;
    const float m = std::max({ rgb[0], rgb[1], rgb[2] });
    if (m <= knee) {
        return;
    }
    // extended Reinhard above the knee, maps peak to headroom
    const float range = headroom - knee;
    const float s = (m - knee) / range;
    const float sp = (peak - knee) / range;
    const float y = knee + range * s * (1.0F + s / (sp * sp)) / (1.0F + s);
    for (size_t i = 0; i < 3; ++i) {
        rgb[i] *= y / m;
    }
}

void ColorSpace::set_peak_nits(const float nits)
{
    if (nits > 0) {
        peak = std::max(nits / REFERENCE_WHITE, 1.0F);
    }
}

void ColorSpace::set_peak(const Pixmap& pm)
{
    float max = 1.0F;
    for (size_t y = 0; y < pm.height(); ++y) {
        const auto* px = static_cast<const uint16_t*>(pm.ptr(0, y));
        for (size_t x = 0; x < pm.width(); ++x, px += 4) {
            float rgb[3];
            for (size_t c = 0; c < 3; ++c) {
                rgb[c] = decode(half_to_float(px[c]), c);
            }
            for (size_t c = 0; c < 3; ++c) {
                max = std::max(max, matrix[c * 3] * rgb[0] +
                                        matrix[c * 3 + 1] * rgb[1] +
                                        matrix[c * 3 + 2] * rgb[2]);
            }
        }
    }
    peak = max;
}

float ColorSpace::decode(const float value, const size_t channel) const
{
    switch (transfer) {
        case Transfer::SRGB:
            return static_cast<float>(srgb_eotf(value));
        case Transfer::Linear:
            return value;
        case Transfer::Gamma:
            return std::copysign(std::pow(std::abs(value), gamma), value);
        case Transfer::PQ:
            return static_cast<float>(pq_eotf(value));
        case Transfer::HLG:
            return static_cast<float>(hlg_inverse_oetf(value));
        case Transfer::Table: {
            const float pos =
                std::clamp(value, 0.0F, 1.0F) * (TABLE_SIZE - 1);
            const auto idx = std::min(static_cast<size_t>(pos), TABLE_SIZE - 2);
            const float* t = &table[channel * TABLE_SIZE];
            return t[idx] + (t[idx + 1] - t[idx]) * (pos - idx);
        }
    }
    return value;
}

bool ColorSpace::is_srgb() const
{
    return transfer == Transfer::SRGB && matrix == IDENTITY && peak <= 1.0F;
}
