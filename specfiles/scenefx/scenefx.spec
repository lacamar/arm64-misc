%define apiver  0.5
%global tag 0.5

Name:           scenefx
Version:        %{tag}
Release:        2
Summary:        A drop-in wlroots replacement that allows eye-candy effects
License:        MIT
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
Obsoletes:      libscenefx5 < %{version}-%{release}

%description
SceneFX is a project that takes the scene api and replaces the wlr
renderer with our own fx renderer, capable of rendering surfaces
with eye-candy effects including blur, shadows, and rounded
corners, while maintaining the benefits of simplicity gained from
using the scene api.

%package devel
Summary:        Development libraries for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
This package provides all the necessary files for development with %{name}

%prep
%autosetup -p1 -n %{name}-%{tag}

%build
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%doc README.md
%{_libdir}/libscenefx-%{apiver}.so

%files devel
%{_includedir}/scenefx-%{apiver}/
%{_libdir}/pkgconfig/scenefx-%{apiver}.pc

%changelog
* Sat Oct 03 2026 Lachlan Marie <lchlnm@pm.me> - 0.5-2
 - Merge libscenefx5 into main package

* Thu Jul 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.5.0-1
 - Update to 0.5.0 (requires wlroots 0.20)
 - Switch wlroots BuildRequires to pkgconfig(wlroots-0.20)
 - Bump versioned paths from 0.4 to 0.5, dedupe unversioned .so

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.4
 - Update to 0.4.1

* Thu Jan 08 2026 Lachlan Marie <lchlnm@pm.me>
- Added to arm64-misc COPR
- Bumped version to 0.4.1
- Adjusted spec to build on Fedora
