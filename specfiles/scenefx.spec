
# spec file for package scenefx
#
# Copyright (c) 2023 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via https://bugs.opensuse.org/
#


%define apiver  0.5
%define libname libscenefx5
%global tag 0.5

Name:           scenefx
Version:        0.5.0
Release:        0
Summary:        A drop-in wlroots replacement that allows eye-candy effects
License:        MIT
Group:          System/GUI/Other
URL:            https://github.com/wlrfx/scenefx
Source0:        %{url}/archive/refs/tags/%{tag}.tar.gz#/%{name}-%{tag}.tar.gz
BuildRequires:  gcc-c++
BuildRequires:  libevdev-devel
BuildRequires:  pixman-devel
BuildRequires:  meson >= 0.60.0
BuildRequires:  pam-devel
BuildRequires:  python3-i3ipc
BuildRequires:  scdoc >= 1.9.2
BuildRequires:  pkgconfig(wayland-protocols) >= 1.27
BuildRequires:  pkgconfig(wayland-server) >= 1.22.0
BuildRequires:  pkgconfig(wlroots-0.20) >= 0.20.0
BuildRequires:  pkgconfig(libdrm) >= 2.4.114
BuildRequires:  pkgconfig(pixman-1) >= 0.42.0
BuildRequires:  cmake

%description
SceneFX is a project that takes the scene api and replaces the wlr
renderer with our own fx renderer, capable of rendering surfaces
with eye-candy effects including blur, shadows, and rounded
corners, while maintaining the benefits of simplicity gained from
using the scene api.

%package devel
Summary:        Development libraries for %{name}
Group:          Development/Libraries/C and C++
Requires:       %{libname} = %{version}

%description devel
This package provides all the necessary files for development with %{name}

%package -n %{libname}
Summary:        Shared libraries for %{name}
Group:          System/Libraries

%description -n %{libname}
This package provides the %{name} shared library.

%prep
%autosetup -p1 -n %{name}-%{tag}

%build
echo $CFLAGS
echo %{optflags}
%meson
%meson_build

%install
%meson_install

%post   -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

%files devel
%license LICENSE
%doc README.md
%{_includedir}/scenefx-%{apiver}/
%{_libdir}/pkgconfig/scenefx-%{apiver}.pc

%files -n %{libname}
%{_libdir}/libscenefx-%{apiver}.so

%changelog
* Thu Jul 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.5.0-0
 - Update to 0.5.0 (requires wlroots 0.20)
 - Switch wlroots BuildRequires to pkgconfig(wlroots-0.20)
 - Bump versioned paths from 0.4 to 0.5, dedupe unversioned .so

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.4
 - Update to 0.4.1

* Thu Jan 08 2026 Lachlan Marie <lchlnm@pm.me>
- Added to arm64-misc COPR
- Bumped version to 0.4.1
- Adjusted spec to build on Fedora
