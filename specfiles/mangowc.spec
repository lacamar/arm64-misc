%global tag 0.12.7
Name:           mangowc
Version:        %{tag}
Release:        1%?dist
Summary:        Lightweight Wayland compositor without compromises
License:        GPL-3.0
URL:            https://github.com/DreamMaoMao/mangowc
Source:         %{url}/archive/%{version}.tar.gz

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  pkgconfig(xcb)
BuildRequires:  pkgconfig(xcb-icccm)
BuildRequires:  pkgconfig(wayland-protocols)
BuildRequires:  pkgconfig(wayland-server)
BuildRequires:  pkgconfig(wlroots-0.19)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(libpcre2-8)
BuildRequires:  pkgconfig(scenefx-0.4)

%description
MangoWC is a lightweight, high-performance Wayland compositor built on dwl, designed for speed, flexibility, and a modern, customizable desktop experience.

%prep
%autosetup -n mango-%{tag}

%build
%meson
%meson_build

%install
%meson_install

%files
%doc README.md
%license LICENSE
%license LICENSE.wlroots
%license LICENSE.tinywl
%license LICENSE.sway
%license LICENSE.dwm
%license LICENSE.dwl
%{_bindir}/mango
%{_bindir}/mmsg
%{_sysconfdir}/mango/config.conf
%{_datadir}/wayland-sessions/mango.desktop
%{_datadir}/xdg-desktop-portal/mango-portals.conf

%changelog
* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.12.7-1
 - Update to 0.12.7

* Thu Jan 08 2026 Lachlan Marie <lchlnm@pm.me>
- Added to arm64-misc COPR

* Wed Nov 12 2025 metcya <metcya@gmail.com>
- Package mangowc
