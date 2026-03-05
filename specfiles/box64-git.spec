%global bumpver 58
%global _name box64

%global commit c92456a744de745268fa99778f07f60cc492cd1c
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:           %{_name}-git
Conflicts:      %{_name}
Provides:       %{_name} = %{version}-%{release}
Version:        0.4.0%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:        2%{?dist}
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

%package        data
Provides:       box64-data = %{version}-%{release}
Summary:        Common files for %{_name}
BuildArch:      noarch
%description    data %{common_description}

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
echo "%{_sbindir}/update-alternatives --install %{_bindir}/%{_name} \
  %{_name} %{_bindir}/%{_name}.aarch64 10 --auto"
%{_sbindir}/update-alternatives --install %{_bindir}/%{_name} \
  %{_name} %{_bindir}/%{_name}.aarch64 10

%postun
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove %{_name} %{_bindir}/%{_name}.aarch64
fi

%post asahi
echo "%{_sbindir}/update-alternatives --install %{_bindir}/%{_name} \
  %{_name} %{_bindir}/%{_name}.asahi 200 --auto"
%{_sbindir}/update-alternatives --install %{_bindir}/%{_name} \
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

%files data
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
* Thu Mar 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^58.git.c92456a-2
 - Update to commit c92456a744de745268fa99778f07f60cc492cd1c

* Tue Mar 03 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^57.git.1848ec1-2
 - Update to commit 1848ec1ee83b7ee635acc790a4b49ca0b8958c38

* Mon Mar 02 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^56.git.bc16008-2
 - Update to commit bc16008759b89278ea931cd8384ec1ae10be0516

* Mon Mar 02 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^55.git.f288184-2
 - Update to commit f2881840e6a2c95d74df2c817cdfbd4b8cdf585a

* Sun Mar 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^54.git.aab7817-2
 - Update to commit aab7817df8a3b8410556289b9db423319464d693

* Sun Mar 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^53.git.388d9c8-1
 - Update to commit 388d9c88a4740fad14cfbb3c063ef6678b66a684

* Sat Feb 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^52.git.2ef63f2-1
 - Update to commit 2ef63f29f118813ed650b0266c7138af02438c33

* Mon Jan 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^51.git.4bcc910-1
 - Update to commit 4bcc910d1568eec51d478d9465a7e8979d4124ab

* Sun Jan 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^50.git.0eb0f9d-1
 - Update to commit 0eb0f9decb0b7e560005b30c11e019f18805eec2

* Wed Jan 21 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^49.git.b5407c4-1
 - Update to commit b5407c4aabdd5e24335abf040e69be99b6f0eb4a

* Wed Jan 21 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^48.git.aca2450-1
 - Update to commit aca2450749102ba5f4908f532539facceed9cc2b

* Mon Jan 19 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^47.git.a2a1f1c-1
 - Update to commit a2a1f1cc401bd98aae3e7b8534dd6155f350267a

* Mon Jan 19 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^46.git.8744f02-1
 - Update to commit 8744f024c89ebcc2db4b611c3ec8b6471ac20e29

* Sun Jan 18 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^45.git.df22349-1
 - Update to commit df223496b263e0ea44cd521740d618730c771df2

* Sat Jan 17 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^44.git.0414fad-1
 - Update to commit 0414fadaf0ee810ed448f25d9ab48098c6ab0923

* Wed Jan 14 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^43.git.341b20c-1
 - Update to commit 341b20c3e41bff8d6f8ec87504ca2a086fd5135d

* Wed Jan 14 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^42.git.8d53ad5-1
 - Update to commit 8d53ad5408ee63d0d4d73a59108d6306209cd0cf

* Tue Jan 13 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^41.git.299c747-1
 - Update to commit 299c74752ee62614a61f12a2de881fe6760d95fd

* Tue Jan 13 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^40.git.61b1253-1
 - Update to commit 61b1253e8014dd642159465472d77b9f33831479

* Sat Jan 10 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^39.git.7a79244-1
 - Update to commit 7a7924495cfc7401da7a7552cdcfa68284aaeb0b

* Sat Jan 10 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^38.git.71f5207-1
 - Update to commit 71f5207f6d7a2569c263cd641c399513783748af

* Fri Jan 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^37.git.b6c1735-1
 - Update to commit b6c1735c075ff0af12bdf0cda259d97f58918fb8

* Fri Jan 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^36.git.57e87b4-1
 - Update to commit 57e87b4ee92ea6dc2d6383af8d3b0faf08ff345a

* Tue Jan 06 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^35.git.b9d36a2-1
 - Update to commit b9d36a205b11115756f09ae915f54574ca4f104f

* Tue Jan 06 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^34.git.c31bf33-1
 - Update to commit c31bf3329c9501300a37e580c5e49744c9a8b527

* Mon Jan 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^33.git.24076b6-1
 - Update to commit 24076b60d7e21ce98c8fdf5a49eee67102321237

* Sun Jan 04 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^32.git.dae0917-1
 - Update to commit dae0917c47b4edd8956f314210417a20fd225c4b

* Sat Jan 03 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.8^31.git.baa962f-1
 - Update to commit baa962f5869d6209648d29d17e658c0271f53fef

* Fri Jan 02 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.8^30.git.0254fbd-1
 - Update to commit 0254fbdd83e3d6aec8c19cbcdeae5dbc55b9b804

* Thu Jan 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.8^29.git.7f6e5fc-1
 - Update to commit 7f6e5fca9005c446b6d1613840a8e1fab320c123

* Tue Dec 30 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^28.git.e0b4a8a-1
 - Update to commit e0b4a8a48acbe36dfaffbf2555ff932a4deb8d35

* Tue Dec 30 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^27.git.a89704c-1
 - Update to commit a89704c8a7c866f348b57c363790c4872e4fdc00

* Mon Dec 29 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^26.git.816f807-1
 - Update to commit 816f807a2dc89ed0a6a942a98b5d8f915e8c3dbd

* Sun Dec 28 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^25.git.050e0f9-1
 - Update to commit 050e0f9f43dcec2d9b2365056e248ca7b6ff0e03

* Sun Dec 28 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^24.git.9a5a8fe-1
 - Update to commit 9a5a8fedc5cbb9d8e503264038b9e520706bdfbe

* Sat Dec 27 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^23.git.490350a-1
 - Update to commit 490350acacdcdf7b960cf04ec257ab0ded9b0a91

* Thu Dec 25 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^22.git.fddba78-1
 - Update to commit fddba78b849f62560a13c8cbc29a8f1b5efb11e9

* Thu Dec 25 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^21.git.0cec2e8-1
 - Update to commit 0cec2e8bf8c86211ab3c310101d4a914359ed3c7

* Wed Dec 24 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^20.git.dd1420e-1
 - Update to commit dd1420eebae16d6afc0ad11878050cc32d16bae4

* Mon Dec 22 2025 Lachlan Marie <lchlnm@pm.me> - 0.3.8^19.git.e912aff-1
 - Update to commit e912aff5c6888ed84b4dc21d648a9aacd0b4ffb7

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
