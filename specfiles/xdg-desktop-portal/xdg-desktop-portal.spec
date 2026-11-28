# copr-exclude-chroots: fedora-43-aarch64
Name:           xdg-desktop-portal
Version:        1.22.1
Release:        22%{?dist}
Summary:        Portal frontend service for Flatpak

License:        LGPL-2.1-or-later
URL:            https://github.com/flatpak/xdg-desktop-portal
Source0:        %{url}/releases/download/%{version}/%{name}-%{version}.tar.xz
Source1:        10-credentialsd.conf
Source2:        portal-watchdog.sh
Source3:        portal-watchdog.service
Source4:        portal-watchdog.timer
Source5:        portal-watchdog-test.sh
Patch0:         pr-1938.patch
Patch1:         pr-2036.patch
Patch2:         pr-1889.patch
Patch3:         xdp-app-info-registry-race.patch
Patch4:         xdp-registry-reject-promise.patch

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

%package watchdog
Summary:        Restart %{name} when it stops answering
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}

%description watchdog
User timer that restarts %{name} when it hangs or leaks threads,
except during a memory stall.

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
install -Dm755 %{SOURCE2} %{buildroot}%{_libexecdir}/%{name}-watchdog
install -Dm644 -t %{buildroot}%{_userunitdir} %{SOURCE3} %{SOURCE4}
install -d %{buildroot}%{_userpresetdir}
echo 'enable portal-watchdog.timer' > %{buildroot}%{_userpresetdir}/90-portal-watchdog.preset
%find_lang %{name}

%check
bash %{SOURCE5} %{SOURCE2}

%post
%systemd_user_post %{name}.service xdg-document-portal.service xdg-permission-store.service

%preun
%systemd_user_preun %{name}.service xdg-document-portal.service xdg-permission-store.service

%post watchdog
%systemd_user_post portal-watchdog.timer

%preun watchdog
%systemd_user_preun portal-watchdog.timer

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

%files watchdog
%{_libexecdir}/%{name}-watchdog
%{_userunitdir}/portal-watchdog.service
%{_userunitdir}/portal-watchdog.timer
%{_userpresetdir}/90-portal-watchdog.preset

%files devel
%{_datadir}/pkgconfig/%{name}.pc

%changelog
* Sat Nov 28 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.1-22
- Add watchdog subpackage
- Skip watchdog restart during memory stall

* Fri Nov 20 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.1-21
- Reject app info promise on failed Register (stuck authorize threads)

* Mon Nov 16 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.1-20
- Exclude f43 COPR chroot (deps unavailable)

* Wed Nov 11 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.1-19
- Import from home:MSirringhaus:webauthn_devel 1.22.1-18.1
- Fix app-info-registry race leaking stuck authorize threads
- Lock app_infos across threads
