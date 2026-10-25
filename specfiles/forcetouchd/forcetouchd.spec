Name:           forcetouchd
Version:        0.1.0
Release:        1%{?dist}
Summary:        Force Touch trackpad click strength and force click daemon

License:        MIT
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3
BuildRequires:  systemd-rpm-macros
%{?systemd_ordering}

Requires:       python3

%description
Sets click strength and handles force click on Force Touch trackpads.

%prep
%autosetup

%install
install -Dm755 forcetouchd -t %{buildroot}%{_bindir}
install -Dm644 forcetouchd.service -t %{buildroot}%{_unitdir}
install -Dm644 forcetouchd.toml %{buildroot}%{_sysconfdir}/forcetouchd.toml

%check
python3 test_encode.py

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun_with_restart %{name}.service

%files
%license LICENSE
%doc README.md
%{_bindir}/forcetouchd
%{_unitdir}/forcetouchd.service
%config(noreplace) %{_sysconfdir}/forcetouchd.toml

%changelog
* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0-1
- Initial package
