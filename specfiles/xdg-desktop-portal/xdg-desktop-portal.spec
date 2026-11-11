Name:           xdg-desktop-portal
Version:        1.22.1
Release:        19%{?dist}
Summary:        Portal frontend service for Flatpak

License:        LGPL-2.1-or-later
URL:            https://github.com/flatpak/xdg-desktop-portal
Source0:        %{url}/releases/download/%{version}/%{name}-%{version}.tar.xz
Source1:        10-credentialsd.conf
Patch0:         pr-1938.patch
Patch1:         pr-2036.patch
Patch2:         pr-1889.patch
Patch3:         xdp-app-info-registry-race.patch

BuildRequires:  gcc
BuildRequires:  meson >= 0.58
BuildRequires:  gettext
BuildRequires:  python3-docutils
BuildRequires:  systemd-rpm-macros
BuildRequires:  xmlto
BuildRequires:  libdex-devel
BuildRequires:  python3-libdex
BuildRequires:  pkgconfig(flatpak) >= 1.5.0
BuildRequires:  pkgconfig(fuse3) >= 3.10.0
BuildRequires:  pkgconfig(gdk-pixbuf-2.0)
BuildRequires:  pkgconfig(gio-unix-2.0)
BuildRequires:  pkgconfig(glib-2.0) >= 2.76
BuildRequires:  pkgconfig(gstreamer-pbutils-1.0)
BuildRequires:  pkgconfig(json-glib-1.0)
BuildRequires:  pkgconfig(libgeoclue-2.0) >= 2.5.2
BuildRequires:  pkgconfig(libpipewire-0.3) >= 0.2.90
BuildRequires:  pkgconfig(libportal) >= 0.9.0
BuildRequires:  pkgconfig(libsystemd)
Requires:       %{_bindir}/fusermount3

%description
D-Bus portal frontend for Flatpak and other sandboxes, with the experimental
WebAuthn credential portal.

%package devel
Summary:        Development files for %{name}
Requires:       %{name} = %{version}-%{release}

%description devel
pkg-config file for %{name}.

%package experimental-credential
Summary:        Enable the experimental credential portal
Requires:       %{name} = %{version}-%{release}

%description experimental-credential
Enables org.freedesktop.portal.experimental.Credential.

%prep
%autosetup -p1

%build
%meson -Ddocumentation=disabled -Dtests=disabled
%meson_build

%install
%meson_install
install -d %{buildroot}%{_datadir}/%{name}/portals
install -Dm644 %{SOURCE1} %{buildroot}%{_userunitdir}/%{name}.service.d/10-credentialsd.conf
%find_lang %{name}

%post
%systemd_user_post %{name}.service xdg-document-portal.service xdg-permission-store.service

%preun
%systemd_user_preun %{name}.service xdg-document-portal.service xdg-permission-store.service

%files -f %{name}.lang
%license COPYING
%{_datadir}/dbus-1/interfaces/*.xml
%{_datadir}/dbus-1/services/org.freedesktop.impl.portal.PermissionStore.service
%{_datadir}/dbus-1/services/org.freedesktop.portal.Desktop.service
%{_datadir}/dbus-1/services/org.freedesktop.portal.Documents.service
%dir %{_datadir}/%{name}
%dir %{_datadir}/%{name}/portals
%{_libexecdir}/%{name}
%{_libexecdir}/xdg-desktop-portal-validate-icon
%{_libexecdir}/xdg-desktop-portal-validate-sound
%{_libexecdir}/xdg-document-portal
%{_libexecdir}/xdg-permission-store
%{_libexecdir}/xdg-desktop-portal-rewrite-launchers
%{_userunitdir}/%{name}.service
%{_userunitdir}/xdg-document-portal.service
%{_userunitdir}/xdg-permission-store.service
%{_userunitdir}/xdg-desktop-portal-rewrite-launchers.service
%{_mandir}/man5/portals.conf.5*

%files experimental-credential
%dir %{_userunitdir}/%{name}.service.d
%{_userunitdir}/%{name}.service.d/10-credentialsd.conf

%files devel
%{_datadir}/pkgconfig/%{name}.pc

%changelog
* Wed Nov 11 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.1-19
- Import from home:MSirringhaus:webauthn_devel 1.22.1-18.1
- Fix app-info-registry race leaking stuck authorize threads
- Lock app_infos across threads
