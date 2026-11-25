%global commit b351ae2e70b053f7d875d7ab5f0fa5fea5b967ae
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global tag 0.5.14
%global bumpver 1
%global debug_package %{nil}

Name:           omarchy-ane
Version:        %{tag}^%{bumpver}.git.%{shortcommit}
Release:        2%{?dist}
Summary:        Apple Neural Engine userspace: libane, runner, smoke test, firmware fetch
License:        MIT
URL:            https://github.com/joshuaswarren/omarchy-ane
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
ExclusiveArch:  aarch64

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  libdrm-devel

Requires:       python3

%description
Userspace for the ane_t6021 DRM accel driver (M2 family): libane, ane-run,
smoke test with fixtures, and the pinned macOS 13.5 ANE firmware fetcher.

%package devel
Summary:        Static libane and headers

%description devel
Static libane and headers for /dev/accel ANE clients.

%prep
%autosetup -n %{name}-%{commit}
find . -type f -perm -u+x -name 'test_*' ! -name '*.*' -delete

%build
%make_build -C libane libane
%make_build -C tools ane-run ane-session ane-selfcheck

%install
make -C tools install-smoke DESTDIR=%{buildroot}
install -m755 tools/ane-session %{buildroot}%{_bindir}/ane-session
install -m755 tools/ane-selfcheck %{buildroot}%{_bindir}/ane-selfcheck
install -m755 packaging/omarchy-ane-check %{buildroot}%{_bindir}/omarchy-ane-check
install -m755 packaging/omarchy-ane-firmware-fetch %{buildroot}%{_bindir}/omarchy-ane-firmware-fetch
install -m755 tools/omarchy-ane-probe %{buildroot}%{_bindir}/omarchy-ane-probe
mkdir -p %{buildroot}%{_datadir}/omarchy-ane/fixtures
cp -r fixtures/h14-anec %{buildroot}%{_datadir}/omarchy-ane/fixtures/
install -Dm644 libane/libane.a %{buildroot}%{_libdir}/libane.a
install -Dm644 -t %{buildroot}%{_includedir}/libane libane/ane.h libane/ane_h15.h libane/ane_f16.h ane/src/uapi/drm/ane_accel.h

%check
tools/ane-selfcheck fixtures/h14-anec

%files
%license LICENSE
%doc README.md
%{_bindir}/omarchy-ane-*
%{_bindir}/ane-session
%{_bindir}/ane-selfcheck
%{_datadir}/omarchy-ane/

%files devel
%{_libdir}/libane.a
%{_includedir}/libane/

%changelog
* Wed Nov 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.5.14^1.git.b351ae2-2
- No debuginfo package

* Tue Nov 24 2026 Lachlan Marie <lchlnm@pm.me> - 0.5.14^1.git.b351ae2-1
- Initial package
