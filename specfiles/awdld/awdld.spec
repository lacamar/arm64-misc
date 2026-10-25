Name:           awdld
Version:        0.1.0
Release:        1%{?dist}
Summary:        AWDL peer manager for brcmfmac firmware AWDL

License:        MIT
Source0:        awdld
Source1:        awdld.service
Source2:        90-awdl-unmanaged.conf

BuildArch:      noarch
BuildRequires:  python3
BuildRequires:  systemd-rpm-macros

Requires:       python3
Requires:       iw
Requires:       iproute

%description
Creates awdl0 on a brcmfmac kernel with AWDL support, adds peers seen in
firmware AWDL action frames and keeps NetworkManager away from the interface.
Start with: systemctl start awdld.service

%prep

%install
install -Dm755 %{SOURCE0} %{buildroot}%{_bindir}/awdld
install -Dm644 %{SOURCE1} %{buildroot}%{_unitdir}/awdld.service
install -Dm644 %{SOURCE2} %{buildroot}%{_prefix}/lib/NetworkManager/conf.d/90-awdl-unmanaged.conf

%check
python3 -I %{SOURCE0} selftest

%post
%systemd_post awdld.service

%preun
%systemd_preun awdld.service

%postun
%systemd_postun_with_restart awdld.service

%files
%{_bindir}/awdld
%{_unitdir}/awdld.service
%{_prefix}/lib/NetworkManager/conf.d/90-awdl-unmanaged.conf

%changelog
* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0-1
- Initial package
