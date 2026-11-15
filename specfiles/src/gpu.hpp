// SPDX-License-Identifier: MIT
// GPU drawing backend interface.

#pragma once

#include "color.hpp"
#include "geometry.hpp"

class Pixmap;

class Gpu {
public:
    virtual ~Gpu() = default;

    virtual void fill(const Pixmap& dst, const Rectangle& rect,
                      const argb_t& color, bool blend) = 0;
    virtual void grid(const Pixmap& dst, const Rectangle& rect, size_t size,
                      const argb_t& clr0, const argb_t& clr1) = 0;
    virtual void mask(const Pixmap& dst, const Pixmap& src, const Point& pos,
                      const argb_t& color) = 0;
    virtual void draw(const Pixmap& dst, const Pixmap& src, const Point& pos,
                      double scale, bool antialiasing) = 0;
    virtual void background(const Pixmap& dst, const Rectangle& preserve,
                            bool mirror) = 0;
};
