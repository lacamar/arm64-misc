%global debug_package %{nil}
%global extid webhid@k4zoku.dev

Name:           webhid
Version:        3.2.0
Release:        2%{?dist}
Summary:        WebHID for Firefox via a native-messaging bridge and hidraw daemon

License:        MIT
URL:            https://github.com/OpenPolyfill/WebHID
Source0:        %{url}/archive/v%{version}/WebHID-%{version}.tar.gz
Source1:        https://addons.mozilla.org/firefox/downloads/file/4981792/webhid-%{version}.xpi
Patch0:         webhid-allow-same-uid.patch

BuildRequires:  cargo
BuildRequires:  gcc
BuildRequires:  patch
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(libudev)

%description
Daemon, native-messaging hosts, udev rule and signed Firefox extension
providing navigator.hid in Gecko browsers.

%prep
%autosetup -n WebHID-%{version}

%build
cargo build --release --locked -p webhid-daemon -p webhid-native-messaging --manifest-path crates/Cargo.toml

%install
install -Dm755 crates/target/release/webhid-daemon %{buildroot}%{_bindir}/webhid-daemon
install -Dm755 crates/target/release/webhid-native-messaging %{buildroot}%{_bindir}/webhid-native-messaging
install -Dm644 manifests/72-webhid.rules %{buildroot}%{_udevrulesdir}/72-webhid.rules
install -dm755 %{buildroot}%{_libdir}/mozilla/native-messaging-hosts
sed 's|{{NM_BIN}}|%{_bindir}/webhid-native-messaging|' manifests/webhid.forwarder_nm_host.json \
  > %{buildroot}%{_libdir}/mozilla/native-messaging-hosts/webhid.forwarder_nm_host.json
sed 's|{{DAEMON_BIN}}|%{_bindir}/webhid-daemon|' manifests/webhid.daemon_nm_host.json \
  > %{buildroot}%{_libdir}/mozilla/native-messaging-hosts/webhid.daemon_nm_host.json
sed 's|{{DAEMON_BIN}}|%{_bindir}/webhid-daemon|' manifests/webhid-daemon.user.service \
  | install -Dm644 /dev/stdin %{buildroot}%{_userunitdir}/webhid-daemon.service
install -Dm644 /dev/stdin %{buildroot}%{_userpresetdir}/80-webhid.preset <<<'enable webhid-daemon.service'
install -Dm644 %{SOURCE1} %{buildroot}%{_datadir}/webhid/webhid.xpi

%post
%systemd_user_post webhid-daemon.service
udevadm control --reload >/dev/null 2>&1 || :
udevadm trigger --subsystem-match=hidraw >/dev/null 2>&1 || :

%preun
%systemd_user_preun webhid-daemon.service

%postun
%systemd_user_postun_with_restart webhid-daemon.service

%files
%license LICENSE
%doc README.md
%{_bindir}/webhid-daemon
%{_bindir}/webhid-native-messaging
%{_udevrulesdir}/72-webhid.rules
%{_libdir}/mozilla/native-messaging-hosts/webhid.*_nm_host.json
%{_userunitdir}/webhid-daemon.service
%{_userpresetdir}/80-webhid.preset
%{_datadir}/webhid/

%changelog
* Mon Oct 19 2026 Lachlan Marie <lchlnm@pm.me> - 3.2.0-2
- Accept same-user socket peers

* Mon Oct 19 2026 Lachlan Marie <lchlnm@pm.me> - 3.2.0-1
- Initial package
