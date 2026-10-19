%global lwa_commit efa374d6303eb1ebeff373878fa76736f3d2c308
%global portalconfdir %{_sysconfdir}/xdg/xdg-desktop-portal

Name:           credentialsd
Version:        0.3.1
Release:        2%{?dist}
Summary:        xdg-desktop-portal backend for WebAuthn credentials

License:        LGPL-3.0-only
URL:            https://github.com/linux-credentials/credentialsd
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        https://github.com/linux-credentials/libwebauthn/archive/%{lwa_commit}/libwebauthn-%{lwa_commit}.tar.gz
Source2:        credentialsd.portal
Source3:        portals.conf
Patch0:         credentialsd-supersede-stale-request.patch
Patch1:         libwebauthn-hybrid-maxmsgsize.patch
Patch2:         credentialsd-webext-all-frames.patch

BuildRequires:  blueprint-compiler >= 0.20.4
BuildRequires:  cargo
BuildRequires:  clang-devel
BuildRequires:  desktop-file-utils
BuildRequires:  gettext
BuildRequires:  gobject-introspection
BuildRequires:  libnfc-devel
BuildRequires:  meson
BuildRequires:  pcsc-lite-devel
BuildRequires:  systemd-rpm-macros
BuildRequires:  zip
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(gtk4)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(udev)

Requires:       xdg-desktop-portal
Requires:       (publicsuffix-list-dafsa or publicsuffix-list)

%description
xdg-desktop-portal backend for WebAuthn: security keys over USB/NFC and
phone passkeys over hybrid (QR code).

%package ui
Summary:        GUI for credentialsd
Requires:       %{name} = %{version}-%{release}

%description ui
GTK prompt for credentialsd requests.

%package webextension
Summary:        Firefox web extension and native helper for credentialsd
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}
Requires:       python3-dbus-next

%description webextension
Routes WebAuthn calls from Firefox-based browsers to credentialsd.

%prep
%autosetup -N
%autopatch -p1 -M 0
%autopatch -p1 -m 2
tar -xf %{SOURCE1}
%patch -P 1 -p1 -d libwebauthn-%{lwa_commit}
cat >> Cargo.toml <<EOF

[patch."https://github.com/linux-credentials/libwebauthn.git"]
libwebauthn = { path = "libwebauthn-%{lwa_commit}/libwebauthn" }
EOF

%build
%meson
%meson_build

%install
%meson_install
%find_lang %{name}-ui
install -Dpm0644 %{SOURCE2} %{buildroot}%{_datadir}/xdg-desktop-portal/portals/credentialsd.portal
install -Dpm0644 %{SOURCE3} %{buildroot}%{portalconfdir}/portals.conf

%post
%systemd_user_post xyz.iinuwa.credentialsd.Credentials.service

%preun
%systemd_user_preun xyz.iinuwa.credentialsd.Credentials.service

%postun
%systemd_user_postun_with_restart xyz.iinuwa.credentialsd.Credentials.service

%post ui
%systemd_user_post xyz.iinuwa.credentialsd.UiControl.service

%preun ui
%systemd_user_preun xyz.iinuwa.credentialsd.UiControl.service

%postun ui
%systemd_user_postun_with_restart xyz.iinuwa.credentialsd.UiControl.service

%files
%license LICENSE.md
%{_bindir}/credentialsd
%{_datadir}/dbus-1/services/xyz.iinuwa.credentialsd.Credentials.service
%dir %{_datadir}/xdg-desktop-portal
%dir %{_datadir}/xdg-desktop-portal/portals
%{_datadir}/xdg-desktop-portal/portals/credentialsd.portal
%dir %{portalconfdir}
%config(noreplace) %{portalconfdir}/portals.conf
%{_userunitdir}/xyz.iinuwa.credentialsd.Credentials.service

%files ui -f %{name}-ui.lang
%license LICENSE.md
%{_bindir}/credentialsd-ui
%{_datadir}/glib-2.0/schemas/xyz.iinuwa.credentialsd.CredentialsUi.gschema.xml
%{_datadir}/metainfo/xyz.iinuwa.credentialsd.CredentialsUi.metainfo.xml
%{_datadir}/credentialsd-ui/
%{_datadir}/icons/hicolor/scalable/apps/xyz.iinuwa.credentialsd.CredentialsUi.svg
%{_datadir}/icons/hicolor/symbolic/apps/xyz.iinuwa.credentialsd.CredentialsUi-symbolic.svg
%{_datadir}/dbus-1/services/xyz.iinuwa.credentialsd.UiControl.service
%{_userunitdir}/xyz.iinuwa.credentialsd.UiControl.service

%files webextension
%{_bindir}/credentialsd-firefox-helper
%dir %{_prefix}/lib64/mozilla
%dir %{_prefix}/lib64/mozilla/native-messaging-hosts
%{_prefix}/lib64/mozilla/native-messaging-hosts/xyz.iinuwa.credentialsd_helper.json
%{_datadir}/credentialsd/

%changelog
* Mon Oct 19 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.1-2
- Inject web extension into iframes
- Require blueprint-compiler >= 0.20.4

* Mon Oct 19 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.1-1
- Initial package
- Allow hybrid authenticators without maxMsgSize
- Supersede stale requests
- Fix helper crash on getClientCapabilities
