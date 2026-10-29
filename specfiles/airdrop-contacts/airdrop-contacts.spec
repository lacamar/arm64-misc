Name:           airdrop-contacts
Version:        0.6.0
Release:        1%{?dist}
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
Source9:        opendrop-model.conf

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
install -Dm644 %{SOURCE9} %{buildroot}%{_userunitdir}/opendrop-receive.service.d/10-%{name}.conf

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
%dir %{_userunitdir}/opendrop-receive.service.d
%{_userunitdir}/opendrop-receive.service.d/10-%{name}.conf

%changelog
* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.6.0-1
- Stream peers from --list as they are seen, for a picker that fills live
- Cap the Discover name lookup so one slow peer cannot stall the list
- Kill avahi-browse and opendrop children on exit or signal

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.5.0-1
- --list resolves the device name via Discover, tab separated output

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.1-1
- --list gathers peers across rounds; MACs rotate and records age out

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0-1
- Accept several files and send them in one transfer

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.1-1
- Default MODEL=MacBookPro18,3; newer ids render a generic icon on iOS

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.0-1
- Set the share-sheet name and model via MODEL=/NAME= in the config
- Drop-in so the receiver advertises a real Mac model instead of OpenDrop

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.2.1-1
- Use the cached avahi record when there is one; only provoke if needed

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.2.0-1
- Send without restarting awdld; the BLE advert alone keeps peers reachable
- AWDL re-init is now opt-in via --cycle
- Default to 3 attempts

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0-3
- Default to 8 attempts; peers often need several AWDL re-inits

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0-2
- Match --to against the peer address too (ids rotate each discovery)

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0-1
- Initial package
- BLE advert of Apple ID hashes for Contacts Only receivers
- Static AWDL neighbours
- airdrop-send with AWDL re-init and retries
