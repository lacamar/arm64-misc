Name:           darkwake
Version:        0.1.0
Release:        1%{?dist}
Summary:        Connected sleep with scheduled dark wakes for Apple Silicon

License:        MIT
Source0:        %{name}-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3
BuildRequires:  systemd-rpm-macros

Requires:       python3
Requires:       iw
Requires:       util-linux
Requires:       polkit

%description
Suspends to idle with the Wi-Fi firmware kept associated and WoWLAN patterns
armed, wakes on a PMU RTC alarm, runs darkwake-sync.target for a bounded
window with the display off, then suspends again until user activity.
Start with: systemctl start darkwake.service

%prep
%autosetup

%install
install -Dm755 darkwake -t %{buildroot}%{_bindir}
install -Dm644 darkwake.service darkwake-sync.target -t %{buildroot}%{_unitdir}
install -Dm644 darkwake.conf %{buildroot}%{_sysconfdir}/darkwake.conf
install -Dm644 50-darkwake.rules -t %{buildroot}%{_datadir}/polkit-1/rules.d

%check
python3 -I darkwake selftest

%files
%license LICENSE
%{_bindir}/darkwake
%{_unitdir}/darkwake.service
%{_unitdir}/darkwake-sync.target
%{_datadir}/polkit-1/rules.d/50-darkwake.rules
%config(noreplace) %{_sysconfdir}/darkwake.conf

%changelog
* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0-1
- Initial package
