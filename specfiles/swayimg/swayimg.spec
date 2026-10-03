%bcond  tests   1
%global tag 5.6

Name:           swayimg
Version:        %{tag}
Release:        6%{?dist}
Summary:        Lightweight image viewer for Wayland display servers

License:        MIT
URL:            https://github.com/artemsen/%{name}
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

# Adds an "exif" imagelist.order sort mode using the EXIF capture time
# (DateTimeOriginal/DateTimeDigitized/DateTime, via exiv2), falling back to
# path order when unavailable. Not upstream.
Patch1:          0001-imagelist-add-exif-capture-time-sort-order.patch
# Fixes upside-down/sideways display of portrait DNGs (confirmed live with
# an iPhone 17 Pro Max ProRAW DNG) whose raw SubIFD uses a codec libraw
# can't decode (JPEG XL), so format detection falls back to the "tiff"
# handler. That handler asked libtiff's TIFFReadRGBAImageOriented() to
# normalize to ORIENTATION_TOPLEFT itself, but TIFFRGBAImage(3tiff) can only
# mirror an image, never rotate it -- orientations 5-8 come back wrong
# regardless of what's requested -- and its partial correction then got
# double-applied on top of the generic EXIF-driven fix_orientation() every
# other format relies on for this, which the tiff handler didn't opt out of
# the way raw.cpp does. Now requests the file's own stored orientation (a
# no-op for libtiff) and leaves 100% of the correction to that generic pass.
# Not upstream.
Patch2:          0002-tiff-fix-dng-orientation-double-apply.patch
# Color managed OpenGL ES renderer: ICC/CICP, wide gamut, HDR (PQ output
# via wp_color_management_v1), software fallback. Not upstream.
Patch3:          0003-render-color-managed-gpu-hdr.patch

BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
%if %{with tests}
BuildRequires:  glibc-langpack-en
%endif
BuildRequires:  meson >= 1.1

BuildRequires:  giflib-devel
# BuildRequires:  pkgconfig(OpenEXR) >= 3.4
BuildRequires:  pkgconfig(bash-completion)
BuildRequires:  pkgconfig(egl)
BuildRequires:  pkgconfig(exiv2)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(glesv2)
BuildRequires:  pkgconfig(lcms2)
%if %{with tests}
BuildRequires:  pkgconfig(gtest)
%endif
BuildRequires:  pkgconfig(libavcodec) >= 60.31.102
BuildRequires:  pkgconfig(libavformat) >= 60.16.100
BuildRequires:  pkgconfig(libavif)
BuildRequires:  pkgconfig(libavutil) >= 58.29.100
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libheif)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libjxl)
BuildRequires:  pkgconfig(libopenjp2)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libraw)
BuildRequires:  pkgconfig(librsvg-2.0) >= 2.46
BuildRequires:  pkgconfig(libsixel)
BuildRequires:  pkgconfig(libswscale) >= 7.5.100
BuildRequires:  pkgconfig(libtiff-4)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(libwebpdemux)
BuildRequires:  pkgconfig(luajit)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.45
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(xkbcommon)

Requires:       hicolor-icon-theme

# src/external/json: MIT
Provides:       bundled(json) = 3.12.0
# src/external/luabridge: MIT
Provides:       bundled(luabridge) = 3.0~rc4^20240929g713c1f5

%description
Swayimg is a lightweight image viewer for Wayland display servers.


%prep
%autosetup -p1


%build
%meson \
    -Dexr=disabled \
    -Dgpu=enabled \
    -Dlicense=false \
    -Dtests=%[%{with tests}?"enabled":"disabled"] \
    -Dversion=%{version}
%meson_build


%install
%meson_install


%check
desktop-file-validate %{buildroot}%{_datadir}/applications/swayimg.desktop
%if %{with tests}
# HEIF test requires libheif-freeworld from rpmfusion
%global gtest_exclude ImageLoadTest.heif

export LANG=en_US.UTF-8 # ImageListTest.SortAlphaUnicode fails with LANG=C
%meson_test --test-args='--gtest_filter=-%{gtest_exclude}'
%endif


%files
%license LICENSE
%doc %{_pkgdocdir}/*.md
%{_bindir}/swayimg
%{_mandir}/man1/swayimg.1*
%{_datadir}/applications/swayimg.desktop
%{_datadir}/icons/hicolor/*/apps/swayimg.png
%dir %{_datadir}/swayimg
%{_datadir}/swayimg/*.lua
%{bash_completions_dir}/swayimg
%{zsh_completions_dir}/_swayimg


%changelog
* Wed Sep 30 2026 Lachlan Marie <lchlnm@pm.me> - 5.6-6
 - Decode 16-bit and float TIFF in high precision

* Sat Sep 26 2026 Lachlan Marie <lchlnm@pm.me> - 5.6-5
 - Add color managed GPU renderer
 - Add ICC/CICP color space support
 - Add HDR and wide gamut output

* Sun Sep 20 2026 Lachlan Marie <lchlnm@pm.me> - 5.6-4
 - Update to 5.6

* Mon Aug 31 2026 Lachlan Marie <lchlnm@pm.me> - 5.5-4
 - Add a patch fixing upside-down/sideways display of portrait DNGs whose
   raw layer libraw can't decode (confirmed live: an iPhone 17 Pro Max
   ProRAW DNG using JPEG XL, falling back to the tiff format handler). See
   0002-tiff-fix-dng-orientation-double-apply.patch for the root cause.

* Mon Aug 31 2026 Lachlan Marie <lchlnm@pm.me> - 5.5-3
 - Add missing pkgconfig(libopenjp2) BuildRequires (fixes fc45/rawhide builds)

* Mon Aug 31 2026 Lachlan Marie <lchlnm@pm.me> - 5.5-2
 - Add exif imagelist.order sort mode (EXIF capture time)

* Mon Jul 27 2026 Lachlan Marie <lchlnm@pm.me> - 5.5-1
 - Update to 5.5

* Sun Jun 21 2026 Lachlan Marie <lchlnm@pm.me> - 5.4-1
 - Update to 5.4

* Fri Jun 19 2026 Lachlan Marie <lchlnm@pm.me> - 5.3-1
 - Update to 5.3

* Thu Apr 09 2026 Lachlan Marie <lchlnm@pm.me> - 5.2-1
 - Update to 5.2

* Wed Mar 25 2026 Lachlan Marie <lchlnm@pm.me> - 5.1-1
 - Update to 5.1
