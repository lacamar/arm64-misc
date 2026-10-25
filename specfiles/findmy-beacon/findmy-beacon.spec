Name:           findmy-beacon
Version:        0.1.1
Release:        1%{?dist}
Summary:        Find My offline-finding beacon for Linux

License:        MIT
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-cryptography
BuildRequires:  systemd-rpm-macros
%{?systemd_ordering}

Requires:       python3-cryptography
Requires:       bluez
Recommends:     python3-findmy

%description
Broadcasts a Find My accessory beacon over Bluetooth LE. findmy-locate fetches
its reports.

%prep
%autosetup

%install
install -Dm755 findmy-beacon findmy-locate -t %{buildroot}%{_bindir}
install -Dm644 findmy-beacon.service -t %{buildroot}%{_unitdir}

%check
python3 test_keys.py

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE
%doc README.md
%{_bindir}/findmy-beacon
%{_bindir}/findmy-locate
%{_unitdir}/findmy-beacon.service

%changelog
* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.1-1
- findmy-locate: UTF-8 safe password prompt

* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0-1
- Initial package
