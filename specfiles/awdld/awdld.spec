Name:           awdld
Version:        0.2.0
Release:        1%{?dist}
Summary:        AWDL peer manager for brcmfmac firmware AWDL

License:        MIT
Source0:        awdld
Source1:        awdld.service
Source2:        90-awdl-unmanaged.conf
Source3:        90-awdld.conf
Source4:        awdld.sleep

BuildArch:      noarch
BuildRequires:  python3
BuildRequires:  systemd-rpm-macros

Requires:       python3
Requires:       iw
Requires:       iproute
Requires:       nftables
Requires:       NetworkManager

%description
Creates awdl0 on a brcmfmac kernel with AWDL support, adds peers seen in
firmware AWDL action frames and keeps NetworkManager away from the interface.
Start with: systemctl start awdld.service

%prep

%install
install -Dm755 %{SOURCE0} %{buildroot}%{_bindir}/awdld
install -Dm644 %{SOURCE1} %{buildroot}%{_unitdir}/awdld.service
install -Dm644 %{SOURCE2} %{buildroot}%{_prefix}/lib/NetworkManager/conf.d/90-awdl-unmanaged.conf
install -Dm644 %{SOURCE3} %{buildroot}%{_sysctldir}/90-awdld.conf
install -Dm755 %{SOURCE4} %{buildroot}%{_prefix}/lib/systemd/system-sleep/awdld

%check
python3 -I %{SOURCE0} selftest

%post
nmcli general reload conf >/dev/null 2>&1 || :
%sysctl_apply 90-awdld.conf
%systemd_post awdld.service

%preun
%systemd_preun awdld.service

%postun
%systemd_postun_with_restart awdld.service

%files
%{_bindir}/awdld
%{_unitdir}/awdld.service
%{_prefix}/lib/NetworkManager/conf.d/90-awdl-unmanaged.conf
%{_sysctldir}/90-awdld.conf
%{_prefix}/lib/systemd/system-sleep/awdld

%changelog
* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.2.0-1
- Persist awdl0 MAC and ARPA name
- Exit when awdl0 disappears
- Restart on failure
- Stop before sleep
- Skip start without AWDL kernel
- Host election: follow best peer via awdl_advertisers/opmode/election tree
- ARPA name derived from AWDL MAC
- Allow only AirDrop traffic on awdl0
- Sync peer entries to the firmware clock
- Wait for a steady peer AW sequence
- Re-add peers on chan seq change
- Follow the nearest peer in the tree
- Fast TCP retransmit on awdl0
- Restart after resume

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.1-1
- Unmanage awdl0 at start
- Reload NM conf on install
- Add -v frame logging

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0-1
- Initial package
