Name:           instant-hotspot
Version:        0.1.0
Release:        1%{?dist}
Summary:        Apple Instant Hotspot client: start and join a same-account iPhone's hotspot

License:        MIT
Source0:        instant-hotspot
Source1:        instant-hotspot.service

BuildArch:      noarch
BuildRequires:  python3
BuildRequires:  systemd-rpm-macros

Requires:       python3
Requires:       python3-bleak
Requires:       python3-cryptography
Requires:       python3-dbus-next
Requires:       bluez
Requires:       NetworkManager

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

%check
python3 -I %{SOURCE0} selftest

%post
%systemd_user_post instant-hotspot.service

%preun
%systemd_user_preun instant-hotspot.service

%files
%{_bindir}/instant-hotspot
%{_userunitdir}/instant-hotspot.service

%changelog
* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0-1
- Initial package
- Rapport same-account Pair-Verify over BLE L2CAP 0x81
- com.sharing.hotspot.request, join via NetworkManager
- --auto user unit joins when offline
