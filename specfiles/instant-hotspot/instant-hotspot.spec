Name:           instant-hotspot
Version:        0.2.0
Release:        2%{?dist}
Summary:        Apple Instant Hotspot client: start and join a same-account iPhone's hotspot

License:        MIT
Source0:        instant-hotspot
Source1:        instant-hotspot.service
Source2:        49-instant-hotspot.rules

BuildArch:      noarch
BuildRequires:  python3
BuildRequires:  systemd-rpm-macros

Requires:       python3
Requires:       python3-bleak
Requires:       python3-cryptography
Requires:       python3-dbus-next
Requires:       bluez
Requires:       NetworkManager
Requires:       polkit

%description
Asks a nearby iPhone on the same Apple account to turn on Personal Hotspot
over Rapport (BLE L2CAP), using the Rapport identity of an Apple device on
that account, then joins the network with NetworkManager. The user unit runs
it whenever the machine is offline. Credentials go in
~/.config/instant-hotspot/ (rapport_selfidentity.bin, rapport_selfidentity_gena.bin).

%prep

%install
install -Dm755 %{SOURCE0} %{buildroot}%{_bindir}/instant-hotspot
install -Dm644 %{SOURCE1} %{buildroot}%{_userunitdir}/instant-hotspot.service
install -Dm644 %{SOURCE2} %{buildroot}%{_datadir}/polkit-1/rules.d/49-%{name}.rules

%check
python3 -I %{SOURCE0} selftest

%post
%systemd_user_post instant-hotspot.service

%preun
%systemd_user_preun instant-hotspot.service

%postun
%systemd_user_postun_with_restart instant-hotspot.service

%files
%{_bindir}/instant-hotspot
%{_userunitdir}/instant-hotspot.service
%{_datadir}/polkit-1/rules.d/49-%{name}.rules

%changelog
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
