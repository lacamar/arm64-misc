Name:           airdrop-contacts
Version:        0.1.0
Release:        2%{?dist}
Summary:        AirDrop sending to Contacts-Only Apple devices over AWDL

License:        MIT
Source0:        airdrop-send
Source1:        airdrop-ble
Source2:        airdrop-neigh
Source3:        airdrop-privhelper
Source4:        airdrop-ble.service
Source5:        airdrop-neigh.service
Source6:        90-airdrop-contacts.preset
Source7:        49-airdrop-contacts.rules
Source8:        airdrop-contacts.conf

BuildArch:      noarch
BuildRequires:  python3
BuildRequires:  systemd-rpm-macros
BuildRequires:  python3-dbus-next

Requires:       python3
Requires:       python3-dbus-next
Requires:       python3-opendrop
Requires:       awdld
Requires:       avahi-tools
Requires:       iproute
Requires:       polkit
Requires:       bluez

%description
Lets this machine AirDrop to Apple devices set to Contacts Only. Advertises the
Apple ID hashes receivers match against their contacts, keeps static AWDL
neighbours because awdl0 neighbour discovery never resolves, and sends with
airdrop-send.

%prep

%install
install -Dm755 %{SOURCE0} %{buildroot}%{_bindir}/airdrop-send
install -Dm755 %{SOURCE1} %{buildroot}%{_libexecdir}/%{name}/airdrop-ble
install -Dm755 %{SOURCE2} %{buildroot}%{_libexecdir}/%{name}/airdrop-neigh
install -Dm755 %{SOURCE3} %{buildroot}%{_libexecdir}/%{name}/airdrop-privhelper
install -Dm644 %{SOURCE4} %{buildroot}%{_unitdir}/airdrop-ble.service
install -Dm644 %{SOURCE5} %{buildroot}%{_unitdir}/airdrop-neigh.service
install -Dm644 %{SOURCE6} %{buildroot}%{_presetdir}/90-%{name}.preset
install -Dm644 %{SOURCE7} %{buildroot}%{_datadir}/polkit-1/rules.d/49-%{name}.rules
install -Dm644 %{SOURCE8} %{buildroot}%{_sysconfdir}/%{name}.conf

%check
python3 -I %{SOURCE0} selftest
python3 -I %{SOURCE1} selftest
python3 -I %{SOURCE2} selftest
sh -n %{SOURCE3}

%post
%systemd_post airdrop-ble.service airdrop-neigh.service

%preun
%systemd_preun airdrop-ble.service airdrop-neigh.service

%postun
%systemd_postun_with_restart airdrop-ble.service airdrop-neigh.service

%files
%{_bindir}/airdrop-send
%dir %{_libexecdir}/%{name}
%{_libexecdir}/%{name}/airdrop-ble
%{_libexecdir}/%{name}/airdrop-neigh
%{_libexecdir}/%{name}/airdrop-privhelper
%{_unitdir}/airdrop-ble.service
%{_unitdir}/airdrop-neigh.service
%{_presetdir}/90-%{name}.preset
%{_datadir}/polkit-1/rules.d/49-%{name}.rules
%config(noreplace) %{_sysconfdir}/%{name}.conf

%changelog
* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0-2
- Match --to against the peer address too (ids rotate each discovery)

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0-1
- Initial package
- BLE advert of Apple ID hashes for Contacts Only receivers
- Static AWDL neighbours
- airdrop-send with AWDL re-init and retries
