%global bumpver 1
%global tag 1.4.0
%global _name umu-launcher

%global commit 7f360de5e7f8d92944dd5ccd75ed6b923644afee
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:        umu-launcher-git
Conflicts:   umu-launcher
Provides:    umu-launcher
Version:     %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:     1%{?dist}
Summary:     A tool for launching non-steam games with proton

# F41 doesn't ship urllib3 >= 2.0 needed
%global urllib3 2.3.0

License:        GPLv3
URL:            https://github.com/Open-Wine-Components/%{_name}
Source0:        %{url}/archive/%{shortcommit}/%{_name}-%{shortcommit}.tar.gz
Source1:        https://github.com/urllib3/urllib3/releases/download/%{urllib3}/urllib3-%{urllib3}.tar.gz
Source2:        umu-launcher-%{commit}-vendor.tar.zst
Source3:        umu-launcher-git-tarballer

BuildArch:      x86_64 aarch64
BuildRequires:  meson >= 0.54.0
BuildRequires:  ninja-build
BuildRequires:  cmake
BuildRequires:  g++
BuildRequires:  gcc-c++
BuildRequires:  scdoc
BuildRequires:  git
BuildRequires:  sed
BuildRequires:  python3-devel
BuildRequires:  python3-build
BuildRequires:  python3-installer
BuildRequires:  python3-hatchling
BuildRequires:  python
BuildRequires:  python3
BuildRequires:  python3-pip
BuildRequires:  libzstd-devel
BuildRequires:  python3-hatch-vcs
BuildRequires:  python3-wheel
BuildRequires:  python3-xlib
BuildRequires:  python3-pyzstd
BuildRequires:  python3-vdf
BuildRequires:  python3-hatch-vcs
BuildRequires:  cargo
BuildRequires:  python3-urllib3
BuildRequires:  rust2rpm

Requires:	python
Requires:	python3
Requires:	python3-xlib
Requires:	python3-filelock
Requires:	python3-pyzstd
Requires:       python3-urllib3

Recommends:	python3-cbor2
Recommends:	python3-xxhash
Recommends:	libzstd


%description
%{name} A tool for launching non-steam games with proton

%prep
%autosetup -n %{_name}-%{commit} -p 1 -a 2
%cargo_prep -v %{_name}-%{commit}-vendor/vendor


%build
./configure.sh --prefix=/usr --use-system-pyzstd --use-system-urllib
make

%install
make DESTDIR=%{buildroot} PYTHONDIR=%{python3_sitelib} install

%files
%{_bindir}/umu-run
%{_datadir}/man/*
%{python3_sitelib}/umu*

%changelog
* Tue Apr 28 2026 Lachlan Marie <lchlnm@pm.me> - 1.4.0^1.git.7f360de-1
 - Update to commit 7f360de5e7f8d92944dd5ccd75ed6b923644afee

* Wed Mar 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.4.0^0.git.e17b257-1
 - Update to 1.4.0

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 1.4.0.3^0.git.ff468bc-1
 - Update to 1.4.0.3

* Thu Mar 12 2026 Lachlan Marie <lchlnm@pm.me> - 1.3.0^4.git.cfa9df7-1
 - Update to commit cfa9df7a069b792cb06c5fe5e13a7e6020570010

* Wed Mar 11 2026 Lachlan Marie <lchlnm@pm.me> - 1.3.0^3.git.c0efc4c-1
 - Update to commit c0efc4ce0cf162f5db107c1f920f5897bba02373

* Sat Feb 28 2026 Lachlan Marie <lchlnm@pm.me> - 1.3.0^2.git.577d9f6-1
 - Update to commit 577d9f68fcb19cb398c026962b3be649f277d322

* Tue Dec 16 2025 Lachlan Marie <lchlnm@pm.me> - 1.3.0^1.git.bb5c870-1
 - Update to commit bb5c870fe076e21fe60cb652b57365022fbfd77a

* Sun Dec 07 2025 Lachlan Marie <lchlnm@pm.me> - 1.3.0^0.git.4ed61d1-1
 - Adapted specfile from gmanka copr
 - Changed build from project git commits
 - Update to commit 4ed61d1031ea43d55100ae2ffa3057280ed2540c
