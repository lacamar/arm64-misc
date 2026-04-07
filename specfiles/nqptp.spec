Name:           nqptp
Version:        1.2.4
Release:        1%{?dist}
Summary:        Not Quite PTP
License:        GPL-2.0-only
URL:            https://github.com/mikebrady/nqptp
Source0:        https://github.com/mikebrady/%{name}/archive/%{version}/%{name}-%{version}.tar.gz
Source1:        nqptp-user.conf
# Backported from 1.2.5-dev:
Patch0:         backport-050a8c2de9f3e1f4859abf9b36d2f18afd4c34d7.patch
# Backported from 1.2.5-dev:
Patch1:         backport-b5321a88d21b854aaa461dc0f6c226d650309b91.patch
Patch2:         disable-user-group-generation.patch

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  systemd-rpm-macros
BuildRequires:  make
BuildRequires:  gcc

%description
nqptp is a daemon that monitors timing data from any PTP clocks – up to 64 – it
sees on ports 319 and 320. It maintains records for each clock, identified by
Clock ID and IP.

It is a companion application to Shairport Sync and provides timing information
for AirPlay 2 operation.

%prep
%autosetup -p1

%build
autoreconf -i -f
%configure --with-systemd-startup
%make_build

%install
%make_install
mkdir -p %{buildroot}%{_unitdir}
mv %{buildroot}%{_libdir}/systemd/system/%{name}.service \
   %{buildroot}%{_unitdir}/%{name}.service
install -D -m 0644 %{SOURCE1} %{buildroot}%{_sysusersdir}/nqptp.conf

%pre
%sysusers_create_package %{name} %{SOURCE1}

%post
%systemd_post %{name}.service

%preun
%systemd_preun %{name}.service

%postun
%systemd_postun %{name}.service

%files
%license LICENSE
%doc README.md RELEASE_NOTES.md
%{_bindir}/%{name}
%{_unitdir}/%{name}.service
%{_sysusersdir}/nqptp.conf

%changelog
* Tue Apr 07 2026 ChatGPT <noreply@example.com> - 1.2.4-1
- Convert openSUSE systemd/sysusers macros to Fedora macros
