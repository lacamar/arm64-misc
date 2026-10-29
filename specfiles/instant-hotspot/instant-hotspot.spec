%global debug_package %{nil}

Name:           instant-hotspot
Version:        0.4.0
Release:        1%{?dist}
Summary:        Apple Instant Hotspot client: start and join a same-account iPhone's hotspot

License:        MIT
Source0:        instant-hotspot-%{version}.tar.gz
Source1:        instant-hotspot.service
Source2:        49-instant-hotspot.rules

BuildRequires:  cargo-rpm-macros >= 26
BuildRequires:  gcc
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  systemd-rpm-macros

Requires:       bluez
Requires:       NetworkManager
Requires:       polkit

%description
Asks a nearby iPhone on the same Apple account to turn on Personal Hotspot
over Rapport (BLE L2CAP), using the Rapport identity of an Apple device on
that account, then joins the network with NetworkManager. The phone needs no
interaction. The user unit watches NetworkManager and joins whenever the
machine is offline, idling on D-Bus signals rather than polling. Credentials
go in ~/.config/instant-hotspot/ (rapport_selfidentity.bin,
rapport_selfidentity_gena.bin).

%prep
%autosetup -n instant-hotspot-%{version}
%cargo_prep -N
# build online: the crates are not packaged for Fedora
sed -i 's/^offline = true$//' .cargo/config.toml

%build
%cargo_build

%install
install -Dpsm0755 target/rpm/%{name} %{buildroot}%{_bindir}/%{name}
install -Dm644 %{SOURCE1} %{buildroot}%{_userunitdir}/%{name}.service
install -Dm644 %{SOURCE2} %{buildroot}%{_datadir}/polkit-1/rules.d/49-%{name}.rules

%check
%cargo_test

%post
%systemd_user_post %{name}.service

%preun
%systemd_user_preun %{name}.service

%postun
%systemd_user_postun_with_restart %{name}.service

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_userunitdir}/%{name}.service
%{_datadir}/polkit-1/rules.d/49-%{name}.rules

%changelog
* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0-1
- Rewritten in Rust: ~4 MB resident, no CPU while idle, no Python runtime
- Unit tests, including a fake phone that completes Pair-Verify
- Keep BLE discovery running while connecting, as BlueZ needs

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.1-1
- Stop awdld in parallel with the BLE exchange
- Skip the blocking BlueZ Disconnect (2.5s); bluetoothd drops the idle link

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.0-1
- --auto reacts to NetworkManager D-Bus state instead of polling every 20s
- Skip while already on the hotspot; ignore drops during a connect
- Stop scanning as soon as a hotspot phone is seen
- Join on targeted SSID scan instead of fixed sleeps

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.2.1-1
- Treat limited connectivity as offline (awdl0/tailscale keep NM at limited)
- Log when --auto acts

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.2.0-2
- Restart the user unit on upgrade

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.2.0-1
- Pause awdld while associating; brcmfmac cannot join a new AP with AWDL up
- Polkit rule: wheel may start/stop awdld.service
- Try phones without the hotspot advert flag; skip our own identity's device

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0-1
- Initial package
- Rapport same-account Pair-Verify over BLE L2CAP 0x81
- com.sharing.hotspot.request, join via NetworkManager
- --auto user unit joins when offline
