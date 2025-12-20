%global bumpver 18
%global _name box64

%global commit 2babe3aa897f3df30aeda72ebc1541f789ab72f8
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:           %{_name}-git
Conflicts:      %{_name}
Provides:       %{_name} = %{version}-%{release}
Version:        0.3.8%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:        1%{?dist}
Summary:        Linux userspace x86_64 emulator with a twist, targeted at ARM64

# Tests are disabled as they require x86_64 libraries to run
%bcond tests 0

%global forgeurl https://github.com/ptitSeb/box64

%global common_description %{expand:
Box64 lets you run x86_64 Linux programs (such as games) on non-x86_64 Linux
systems, like ARM (host system needs to be 64-bit little-endian).}


License:        MIT
URL:            https://box86.org
Source0:        https://github.com/ptitSeb/%{_name}/archive/%{shortcommit}/%{_name}-%{shortcommit}.tar.gz

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  perl-podlators
BuildRequires:  systemd-rpm-macros
BuildRequires:  alternatives

# box64 only supports these architectures
ExclusiveArch:  aarch64 riscv64 ppc64le %{x86_64}

Requires:       alternatives
Requires:       %{_name}-data = %{version}-%{release}
# These should not be pulled in on x86_64 as they can cause a loop and prevent
# any binary from successfully executing (#2344770)
%ifnarch %{x86_64}
Recommends:     %{name}-binfmts = %{version}-%{release}
%endif
%ifarch aarch64
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives
%endif

%description    %{common_description}

%package        -n box64-data
Provides:       box64-data = %{version}-%{release}
Summary:        Common files for %{_name}
BuildArch:      noarch
%description    -n box64-data %{common_description}

This package provides common data files for box64.

%ifnarch %{x86_64}
%package        binfmts
Conflicts:      box64-binfmts
Provides:       box64-binfmts = %{version}-%{release}
Summary:        binfmt_misc handler configurations for box64

%description    binfmts %{common_description}

This package provides binfmt_misc handler configurations to use box64 to
execute x86_64 binaries.
%endif

%ifarch aarch64
%package        asahi
Conflicts:      box64-asahi
Provides:       box64-asahi = %{version}-%{release}
Summary:        Apple Silicon version of box64

Requires:       %{_name}-data = %{version}-%{release}
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives

%description    asahi %{common_description}

This package contains a version of box64 targeting Apple Silicon systems using
a 16k page size.
%endif

%prep
%autosetup -p1 -n %{_name}-%{commit}

# Remove prebuilt libraries
rm -r x64lib

# Fix encoding
sed -i 's/\r$//' docs/*.md

# Fix install paths
sed -i 's:/etc/binfmt.d:%{_binfmtdir}:g' CMakeLists.txt

%build
%global common_flags -DNOGIT=ON -DCMAKE_BUILD_TYPE=RelWithDebInfo -DBOX32=ON -DBOX32_BINFMT=ON -DBOX32_FMT=ON
%ifarch aarch64
%global common_flags -DARM_DYNAREC=ON %{common_flags}

# Apple Silicon
%cmake %{common_flags} -DM1=ON
%cmake_build
cp -p %{__cmake_builddir}/%{_name} %{_name}.asahi
rm -r %{__cmake_builddir}

%endif

%cmake %{common_flags} -DNO_LIB_INSTALL=ON \
%ifarch aarch64
  -DARM64=ON
%endif
%ifarch riscv64
  -DRV64=ON
%endif
%ifarch ppc64le
  -DPPC64LE=ON
%endif
%ifarch %{x86_64}
  -DLD80BITS=ON \
  -DNOALIGN=ON
%endif
%cmake_build

# Build manpage
pod2man --stderr docs/%{_name}.pod > docs/%{_name}.1

%install
%ifarch %{x86_64}
# Install manually as cmake_install doesn't seem to work on x86_64
install -Dpm0755 -t %{buildroot}%{_bindir} %{__cmake_builddir}/%{_name}
install -Ddpm0755 %{buildroot}%{_binfmtdir}
sed 's:${CMAKE_INSTALL_PREFIX}/bin/${BOX64}:%{_bindir}/%{_name}:' \
  < system/box32.conf.cmake > system/box32.conf
sed 's:${CMAKE_INSTALL_PREFIX}/bin/${BOX64}:%{_bindir}/%{_name}:' \
  < system/box64.conf.cmake > system/box64.conf
install -Dpm0644 -t %{buildroot}%{_sysconfdir} system/box64.box64rc
%else
%cmake_install
%endif

# Install manpage
install -Dpm0644 -t %{buildroot}%{_mandir}/man1 docs/%{_name}.1

%ifarch aarch64
mv %{buildroot}%{_bindir}/%{_name} %{buildroot}%{_bindir}/%{_name}.aarch64
touch %{buildroot}%{_bindir}/%{_name}
chmod +x %{buildroot}%{_bindir}/%{_name}
install -Dpm0755 -t %{buildroot}%{_bindir} \
  %{_name}.asahi

%post
%{_sbindir}/update-alternatives --auto --install %{_bindir}/%{_name} \
  %{_name} %{_bindir}/%{_name}.aarch64 10

%postun
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove %{_name} %{_bindir}/%{_name}.aarch64
fi

%post asahi
%{_sbindir}/update-alternatives --auto --install %{_bindir}/%{_name} \
  %{_name} %{_bindir}/%{_name}.asahi 200

%postun asahi
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove %{_name} %{_bindir}/%{_name}.asahi
fi

%endif

%if %{with tests}
%check
%ctest
%endif

%files
%ifarch aarch64
%ghost %{_bindir}/%{_name}
%{_bindir}/%{_name}.aarch64
%else
%{_bindir}/%{_name}
%endif

%ifarch aarch64
%files asahi
%ghost %{_bindir}/%{_name}
%{_bindir}/%{_name}.asahi
%endif

%files -n box64-data
%license LICENSE
%doc README.md
%doc %lang(cn) README_CN.md
%doc %lang(uk) README_UK.md
%doc docs/*.md docs/img
%{_mandir}/man1/box64.1*
%config(noreplace) %{_sysconfdir}/box64.box64rc

%ifnarch %{x86_64}
%files binfmts
%{_binfmtdir}/box32.conf
%{_binfmtdir}/box64.conf
%endif

%changelog
* Sun Dec 21 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^18.git.2babe3a-1
 - Update to commit 2babe3aa897f3df30aeda72ebc1541f789ab72f8

* Sat Dec 20 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^17.git.f2660cd-1
 - Update to commit f2660cd3f007bd765873dafb21c8e482ec2b288e

* Fri Dec 19 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^16.git.14b660e-1
 - Update to commit 14b660e3bbcf025bb93be8ba13e13268c8989e40

* Fri Dec 19 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^15.git.7586bd4-1
 - Update to commit 7586bd47cbc10db36d86828e7fd4a8a77976fb17

* Thu Dec 18 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^14.git.7f20c20-1
 - Update to commit 7f20c20031fb1f910d9b90c3a6f3fad4526ac774

* Wed Dec 17 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^13.git.57f1b60-1
 - Update to commit 57f1b60fb05a1a8cefbc5d66ad4ec6a25c867130

* Tue Dec 16 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^12.git.b7c3862-1
 - Update to commit b7c386289dfe360ac4f19df0828712ae9e9e8157

* Tue Dec 16 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^11.git.b9af627-1
 - Update to commit b9af6270d40670fef8aaeb478660985cf0fe40ee

* Sun Dec 14 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^10.git.bb78e2e-1
 - Update to commit bb78e2e63b8fa78522ce4c61a4a20bc29f76ebb8

* Sun Dec 14 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^9.git.acad5ac-1
 - Update to commit acad5acbef2f62544290260b2b2b63bedb27c95c

* Sat Dec 13 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^8.git.466e5eb-1
 - Update to commit 466e5eb84b34f592666f9bf1563e058157849755

* Sat Dec 13 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^7.git.ac08b01-1
 - Update to commit ac08b010d533c6e2de0368322e213add8efe5125

* Fri Dec 12 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^6.git.a1f9147-1
 - Update to commit a1f9147868c3ed1d9671a7f48bf43390403149d4

* Fri Dec 12 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^5.git.52e2514-1
 - Update to commit 52e251427915a508ce7df4399c6081e129c78cf6

* Thu Dec 11 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^4.git.f79a31e-1
 - Update to commit f79a31e5359d2990dbced287ef19f54e98acf0f0

* Thu Dec 11 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^3.git.aa45e25-1
 - Update to commit aa45e2583d673220efca08bc1c217d359f271dab

## START: Generated by rpmautospec
* Sun Dec 07 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8-2
- Update to 0.3.8
- Apple silicon only

* Wed Aug 06 2025 Davide Cavalca <dcavalca@fedoraproject.org> - 0.3.6-1
- Update to 0.3.6; Fixes: RHBZ#2370862

* Wed Jul 23 2025 Fedora Release Engineering <releng@fedoraproject.org> - 0.3.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_43_Mass_Rebuild

* Tue Mar 11 2025 Davide Cavalca <dcavalca@fedoraproject.org> - 0.3.4-1
- Update to 0.3.4; Fixes: RHBZ#2351162

* Wed Feb 12 2025 Davide Cavalca <dcavalca@fb.com> - 0.3.2-3
- Do not install binfmt_misc configs on x86_64; Fixes: RHBZ#2344770

* Thu Jan 16 2025 Fedora Release Engineering <releng@fedoraproject.org> - 0.3.2-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Sat Dec 21 2024 Davide Cavalca <dcavalca@fb.com> - 0.3.2-1
- Update to 0.3.2; Fixes: RHBZ#2330808

* Sat Nov 02 2024 Teoh Han Hui <teohhanhui@gmail.com> - 0.3.0-1
- Update to 0.3.0

* Wed Jul 17 2024 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Wed May 22 2024 Davide Cavalca <dcavalca@fedoraproject.org> - 0.2.8-1
- Update to 0.2.8; Fixes: RHBZ#2282278

* Wed Jan 24 2024 Davide Cavalca <davide@cavalca.name> - 0.2.6-1
- Update to 0.2.6; Fixes: RHBZ#2254840

* Tue Jan 23 2024 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.4-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Fri Jan 19 2024 Fedora Release Engineering <releng@fedoraproject.org> - 0.2.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Wed Aug 23 2023 Davide Cavalca <dcavalca@fedoraproject.org> - 0.2.4-1
- Update to 0.2.4

* Wed Aug 23 2023 Davide Cavalca <dcavalca@fedoraproject.org> - 0.2.2-1
- Initial import; Fixes: RHBZ#2217227
## END: Generated by rpmautospec
