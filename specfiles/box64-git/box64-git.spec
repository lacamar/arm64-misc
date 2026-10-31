%global bumpver 47
%global _name box64
%global tag 0.4.5.1

%global commit 6dfbebd2d485efe1510db02a45ac0235c1f75ddc
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:           %{_name}-git
Version:        %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Epoch:          1
Release:        1%{?dist}
Conflicts:      %{_name}
Provides:       %{_name} = %{epoch}:%{version}-%{release}
Summary:        Linux userspace x86_64 emulator with a twist, targeted at ARM64

%global common_description %{expand:
Box64 lets you run x86_64 Linux programs (such as games) on non-x86_64 Linux
systems, like ARM (host system needs to be 64-bit little-endian).}

License:        MIT
URL:            https://box86.org
Source0:        https://github.com/ptitSeb/%{_name}/archive/%{commit}/%{_name}-%{shortcommit}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  perl-podlators
BuildRequires:  systemd-rpm-macros
BuildRequires:  alternatives
BuildRequires:  desktop-file-utils

ExclusiveArch:  aarch64
%global __requires_exclude_from ^%{_bindir}/box64-bash$
%global __provides_exclude_from ^%{_bindir}/box64-bash$

Requires:       alternatives
Requires:       %{_name}-data = %{epoch}:%{version}-%{release}
Recommends:     %{name}-binfmts = %{epoch}:%{version}-%{release}
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives

%description    %{common_description}

%package        data
Provides:       box64-data = %{epoch}:%{version}-%{release}
Summary:        Common files for %{_name}
BuildArch:      noarch
%description    data %{common_description}

This package provides common data files for box64.

%package        binfmts
Conflicts:      box64-binfmts
Provides:       box64-binfmts = %{epoch}:%{version}-%{release}
Summary:        binfmt_misc handler configurations for box64

%description    binfmts %{common_description}

This package provides binfmt_misc handler configurations to use box64 to
execute x86_64 binaries.

%package        asahi
Conflicts:      box64-asahi
Provides:       box64-asahi = %{epoch}:%{version}-%{release}
Summary:        Apple Silicon version of box64

Requires:       %{_name}-data = %{epoch}:%{version}-%{release}
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives

%description    asahi %{common_description}

This package contains a version of box64 targeting Apple Silicon systems using
a 16k page size.

%prep
%autosetup -p1 -n %{_name}-%{commit}

# Remove prebuilt libraries
rm -r x64lib

# Fix encoding
sed -i 's/\r$//' docs/*.md

# Fix install paths
sed -i 's:/etc/binfmt.d:%{_binfmtdir}:g' CMakeLists.txt

%build
%global common_flags -DARM_DYNAREC=ON -DNOGIT=ON -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBOX32=ON -DBOX32_BINFMT=ON -DBOX32_FMT=ON

# Apple Silicon
%cmake %{common_flags} -DM1=ON
%cmake_build
cp -p %{__cmake_builddir}/%{_name} %{_name}.asahi
rm -r %{__cmake_builddir}

%cmake %{common_flags} -DNO_LIB_INSTALL=ON -DARM64=ON
%cmake_build

# Build manpage
pod2man --stderr docs/%{_name}.pod > docs/%{_name}.1

%install
%cmake_install

# Install manpage
install -Dpm0644 -t %{buildroot}%{_mandir}/man1 docs/%{_name}.1

desktop-file-validate %{buildroot}%{_datadir}/applications/box64-configurator.desktop

mv %{buildroot}%{_bindir}/%{_name} %{buildroot}%{_bindir}/%{_name}.aarch64
touch %{buildroot}%{_bindir}/%{_name}
chmod +x %{buildroot}%{_bindir}/%{_name}
install -Dpm0755 -t %{buildroot}%{_bindir} \
  %{_name}.asahi tests/box64-bash

%post
%{_sbindir}/update-alternatives --install %{_bindir}/%{_name} \
  %{_name} %{_bindir}/%{_name}.aarch64 10

%postun
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove %{_name} %{_bindir}/%{_name}.aarch64
fi

%post asahi
%{_sbindir}/update-alternatives --install %{_bindir}/%{_name} \
  %{_name} %{_bindir}/%{_name}.asahi 200

%postun asahi
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove %{_name} %{_bindir}/%{_name}.asahi
fi

%files
%ghost %{_bindir}/%{_name}
%{_bindir}/%{_name}.aarch64
%{_bindir}/box64-configurator
%{_bindir}/box64-bash

%files asahi
%ghost %{_bindir}/%{_name}
%{_bindir}/%{_name}.asahi
%{_bindir}/box64-bash

%files data
%license LICENSE
%doc README.md
%doc %lang(cn) README_CN.md
%doc %lang(uk) README_UK.md
%doc docs/*.md docs/img
%{_mandir}/man1/box64.1*
%config(noreplace) %{_sysconfdir}/box64.box64rc
%{_datadir}/applications/box64-configurator.desktop

%files binfmts
%{_binfmtdir}/box32.conf
%{_binfmtdir}/box64.conf

%changelog
* Sat Oct 31 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^47.git.6dfbebd-1
- Update to commit 6dfbebd2d485efe1510db02a45ac0235c1f75ddc

* Fri Oct 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^46.git.07e9e5c-1
- Update to commit 07e9e5c34420b3116913b44e3f38a5c8f6f4e546

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^45.git.30d5c77-1
- Update to commit 30d5c77188fa9cf8bea7064d93ced554c3a34cde

* Wed Oct 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^44.git.11a20e3-1
- Update to commit 11a20e37c8f5996dfcd3b1f247a9b273e56ad189

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^43.git.74ee428-1
- Update to commit 74ee4280dbd3ea311808d7204e29ae5a6ff85517

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^42.git.a46ad9d-1
- Update to commit a46ad9dfe9db4c5c70c86ac9b4e9b5b737049cc9

* Sat Oct 24 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^41.git.420eda6-1
- Update to commit 420eda69ff51ab5d5a7cbc3dee2e70433be3411d

* Thu Oct 22 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^40.git.d96343f-1
- Update to commit d96343fbb1777458e4bc3adcd5a4b93c113fd245

* Tue Oct 20 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^39.git.ae3412c-1
- Update to commit ae3412c1bf9179b341996e18b656f11fd145f01e

* Mon Oct 19 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^38.git.66dafa5-1
 - Update to commit 66dafa53302efc771352a6f7b4ca74869dc8c276

* Sat Oct 17 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^37.git.27860e6-1
 - Update to commit 27860e6aee72dd33c2588d081652d6e9becc1089

* Fri Oct 16 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^36.git.b99d443-1
 - Update to commit b99d44309e3c0102bfff40d1d680b915f565eb1f

* Fri Oct 16 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^35.git.e296745-1
 - Update to commit e296745e8252520ad17708ccb13a6b6a42182719

* Sun Oct 11 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^34.git.c6a8c44-1
 - Update to commit c6a8c4472f74f9ad204d35195f084b5f996b12e3

* Sat Oct 10 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^33.git.a489cfe-1
 - Update to commit a489cfe7d03f6d57aa38580c157711fbfc69ed7a

* Thu Oct 08 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^32.git.6ece2e8-1
 - Update to commit 6ece2e87f2c4ef9bf2f759e255d36cf4730a06e3

* Tue Oct 06 2026 Lachlan Marie <lchlnm@pm.me> - 1:0.4.5.1^31.git.bc41dac-1
 - Update to commit bc41dacc8cd45353a5918e741170a9256afb4675
 - Add Epoch to fix version ordering
 - Ship box64-bash

* Tue Sep 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^30.git.50069bc-4
 - Update to commit 50069bcf69f62a780074cf8458c5339f00579a5a

* Tue Sep 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^29.git.e1eee08-4
 - Update to commit e1eee0855a8670a19dda3a586a8098231b2502bd

* Sun Sep 27 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^28.git.c61543e-4
 - Update to commit c61543e47b8a9d1720742186bfea205ad8a7ed35

* Sat Sep 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^27.git.ac9b13a-4
 - Update to commit ac9b13a54f59ddfa94a93d595720d0e9dc9a9b75

* Wed Sep 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.5.1^26.git.729c25d-4
 - Update to commit 729c25da67f520bf2a5957d66f5015e34391b86b
