%bcond  tests   1
%global tag 5.5

Name:           swayimg
Version:        %{tag}
Release:        3%{?dist}
Summary:        Lightweight image viewer for Wayland display servers

License:        MIT
URL:            https://github.com/artemsen/%{name}
Source:         %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

Patch0:          %{url}/commit/5c2d958.patch#/swayimg-5.0-missing-includes.patch
# Adds an "exif" imagelist.order sort mode using the EXIF capture time
# (DateTimeOriginal/DateTimeDigitized/DateTime, via exiv2), falling back to
# path order when unavailable. Not upstream.
Patch1:          0001-imagelist-add-exif-capture-time-sort-order.patch

# Exclude x86 and all the platforms where luajit is not available
ExcludeArch:    %{ix86} riscv64 ppc64 ppc64le

BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
%if %{with tests}
BuildRequires:  glibc-langpack-en
%endif
BuildRequires:  meson >= 1.1

BuildRequires:  giflib-devel
# BuildRequires:  pkgconfig(OpenEXR) >= 3.4
BuildRequires:  pkgconfig(bash-completion)
BuildRequires:  pkgconfig(exiv2)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
%if %{with tests}
BuildRequires:  pkgconfig(gtest)
%endif
BuildRequires:  pkgconfig(libavif)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libheif)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libjxl)
BuildRequires:  pkgconfig(libopenjp2)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libraw)
BuildRequires:  pkgconfig(librsvg-2.0) >= 2.46
BuildRequires:  pkgconfig(libsixel)
BuildRequires:  pkgconfig(libtiff-4)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(libwebpdemux)
BuildRequires:  pkgconfig(luajit)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.35
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
%autosetup -N
%patch -P 0 -p1 -F3
%patch -P 1 -p1 -F3


%build
%meson \
    -Dexr=disabled \
    -Dlicense=false \
    -Dtests=%[%{with tests}?"enabled":"disabled"] \
    -Dversion=%{version}
%meson_build


%install
%meson_install


%check
desktop-file-validate %{buildroot}%{_datadir}/applications/swayimg.desktop
%if %{with tests}
%ifarch s390x
# A few tests fail on s390x (endianness?)
%global gtest_exclude ImageLoadTest.*
%else
# HEIF test requires libheif-freeworld from rpmfusion
%global gtest_exclude ImageLoadTest.heif
%endif

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
