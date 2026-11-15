// SPDX-License-Identifier: MIT
// Color spaces and color management.

#pragma once

#include <array>
#include <bit>
#include <cstddef>
#include <cstdint>
#include <memory>
#include <vector>

class Pixmap;

using Matrix3 = std::array<float, 9>;

// Working space: linear light, sRGB primaries (extended range, D65),
// 1.0 is the SDR reference white.
class ColorSpace {
public:
    enum class Transfer : uint8_t { SRGB, Linear, Gamma, PQ, HLG, Table };

    using Ptr = std::shared_ptr<const ColorSpace>;

    static constexpr float REFERENCE_WHITE = 203.0F; // cd/m², BT.2408
    static constexpr float HDR_PEAK = 1000.0F;       // default mastering peak
    static constexpr size_t TABLE_SIZE = 4096;
    static constexpr Matrix3 IDENTITY = { 1, 0, 0, 0, 1, 0, 0, 0, 1 };

    // CICP (ITU-T H.273) code points
    static std::shared_ptr<ColorSpace> from_cicp(uint16_t primaries,
                                                 uint16_t transfer);
    // Chromaticities: red, green, blue, white (x, y)
    static std::shared_ptr<ColorSpace>
    from_chromaticities(const std::array<float, 8>& xy, Transfer transfer,
                        float gamma = 1.0F);
    // Matrix/shaper ICC profiles only
    static std::shared_ptr<ColorSpace> from_icc(const void* data,
                                                size_t size);

    // Tag pixmap with ICC profile, or convert it to sRGB for LUT profiles
    static void apply_icc(Pixmap& pm, const void* data, size_t size);

    // Convert pixmap to 8-bit sRGB, tone mapped to SDR
    static Pixmap to_srgb(const Pixmap& pm);
    static bool needs_conversion(const Pixmap& pm);

    static void tonemap(float rgb[3], float peak, float headroom);

    void set_peak_nits(float nits);
    void set_peak(const Pixmap& pm);
    float decode(float value, size_t channel) const;

    [[nodiscard]] bool is_srgb() const;

    Transfer transfer = Transfer::SRGB;
    float gamma = 1.0F;
    std::vector<float> table;
    Matrix3 matrix = IDENTITY;
    std::array<float, 3> luma = { 0.2126729F, 0.7151522F, 0.0721750F };
    float peak = 1.0F;

    static bool native;
};

inline float half_to_float(const uint16_t h)
{
    const uint32_t sign = static_cast<uint32_t>(h & 0x8000U) << 16;
    uint32_t exp = (h >> 10) & 0x1fU;
    uint32_t mant = h & 0x3ffU;
    uint32_t bits;
    if (exp == 0) {
        if (mant == 0) {
            bits = sign;
        } else {
            exp = 113;
            while (!(mant & 0x400U)) {
                mant <<= 1;
                --exp;
            }
            bits = sign | (exp << 23) | ((mant & 0x3ffU) << 13);
        }
    } else if (exp == 31) {
        bits = sign | 0x7f800000U | (mant << 13);
    } else {
        bits = sign | ((exp + 112) << 23) | (mant << 13);
    }
    return std::bit_cast<float>(bits);
}

inline uint16_t float_to_half(const float f)
{
    const uint32_t x = std::bit_cast<uint32_t>(f);
    const auto sign = static_cast<uint16_t>((x >> 16) & 0x8000U);
    const uint32_t fexp = (x >> 23) & 0xffU;
    uint32_t mant = x & 0x7fffffU;
    if (fexp == 0xff) {
        return sign | 0x7c00U | (mant ? 0x200U : 0);
    }
    const int32_t exp = static_cast<int32_t>(fexp) - 112;
    if (exp >= 31) {
        return sign | 0x7c00U;
    }
    if (exp <= 0) {
        if (exp < -10) {
            return sign;
        }
        mant |= 0x800000U;
        const uint32_t shift = 14 - exp;
        uint32_t h = mant >> shift;
        if ((mant >> (shift - 1)) & 1U) {
            ++h;
        }
        return sign | static_cast<uint16_t>(h);
    }
    uint32_t h = (static_cast<uint32_t>(exp) << 10) | (mant >> 13);
    if (mant & 0x1000U) {
        ++h;
    }
    return sign | static_cast<uint16_t>(h);
}
