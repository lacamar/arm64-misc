%global bumpver 11
%global _name box64
%global tag 0.4.33

%global commit 956c89d8208d6b458f826a78606294ca0bdbecaa
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:           %{_name}-git
Version:        %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:        3%{?dist}
Conflicts:      %{_name}
Provides:       %{_name} = %{version}-%{release}
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
%{_bindir}/box64-configurator
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
* Fri Jun 19 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.33^11.git.956c89d-3
 - Update to commit 956c89d8208d6b458f826a78606294ca0bdbecaa

* Thu Jun 18 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.33^10.git.befc90d-3
 - Update to commit befc90de1ce4214ac720b2f1c154b8c896d7d202

* Wed Jun 17 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.33^9.git.05136b7-3
 - Update to commit 05136b7bfbd3b0df072e4b1c2a3410c6aa165152

* Wed Jun 17 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.33^8.git.e823292-3
 - Update to commit e823292457fdc6af7bcb3020ac93698893bc564d

* Tue Jun 16 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.33^7.git.80bdf9b-3
 - Update to commit 80bdf9bac7f60b9a07c4f14330091743012a2473

* Mon Jun 15 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.33^6.git.3f74772-3
 - Update to commit 3f747727f267f8ba820829699c0271a2ec059070

* Sat Jun 13 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.33^5.git.8f445d9-3
 - Update to commit 8f445d9a0c52767274567f1a9bd76ef28e531ec7

 - Added box64-configurator to files section

* Fri Jun 12 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.33^4.git.8d7f6a5-2
 - Update to commit 8d7f6a54d78ab7c551367c0b43553c8b30dc6a39

* Thu Jun 11 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.33^3.git.d6e26bc-2
 - Update to commit d6e26bc9aa64bc73d570ed30e958649085209e26

* Thu Jun 11 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.33^2.git.be4db11-2
 - Update to commit be4db111990826ea860ca5e9e72a3b064bdb4e3e

* Wed Jun 10 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.33^1.git.c14f0ec-2
 - Update to commit c14f0eca8479779586ae4e9bb821d1b92c30969c

* Mon Jun 08 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.33^0.git.e2345d7-2
 - Update to 0.4.33

* Mon Jun 08 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^18.git.e2345d7-2
 - Update to commit e2345d735af36f7915ab861a55b489d69f2350c7

* Mon Jun 08 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^17.git.7f1cae9-2
 - Update to commit 7f1cae956cb6603adf5b8d77d6dcf2a5aabb6382

* Sat Jun 06 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^16.git.e694f2c-2
 - Update to commit e694f2ca8b349436e483d1c54bc9f313e932208c

* Sat Jun 06 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^15.git.93abdcf-2
 - Update to commit 93abdcf317bc26341c901dbe54274794aaf02c73

* Fri Jun 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^14.git.09bce33-2
 - Update to commit 09bce33a45b0693bc7abf9bd6db034bb2fc7b8ff

* Fri Jun 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^13.git.dab3fdc-2
 - Update to commit dab3fdc351de1a1dc79b799283dfb6ef92085cbd

* Thu Jun 04 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^12.git.419e095-2
 - Update to commit 419e095ea01146bfec8466284760d4f3febea337

* Wed Jun 03 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^11.git.7fb417d-2
 - Update to commit 7fb417db9813e44636e03f5e5d064ee9be8acb3b

* Mon Jun 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^10.git.3583d9c-2
 - Update to commit 3583d9c90e042694a5b0ac2511603ba8230c2316

* Sat May 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^9.git.194d577-2
 - Update to commit 194d577d5153383e857b9ca85d918c490c484071

* Fri May 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^8.git.2e718b4-2
 - Update to commit 2e718b464d0fefeef6623719b82d6ab5ece6aab0

* Fri May 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^7.git.d39062d-2
 - Update to commit d39062d3d768fcf020d8e795c2fad818f5f55375

* Thu May 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^6.git.5687b46-2
 - Update to commit 5687b460b9eddd0271b6f76076cf480e0b3d3a69

* Wed May 27 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^5.git.b946dea-2
 - Update to commit b946deaeeaff69dbabfcb5a101970a3c8de0f9bd

* Wed May 27 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^4.git.0bce9e5-2
 - Update to commit 0bce9e56124e4c6330346e28ff1d9b7650fddcb0

* Tue May 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^3.git.c1d2de4-2
 - Update to commit c1d2de4538440c971f74ac5086d25d9e016a943b

* Mon May 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^2.git.8707b8d-2
 - Update to commit 8707b8d1edc8cc4c43b3566dc210cb3750d54c88

* Sun May 24 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^1.git.86ff049-2
 - Update to commit 86ff049f6b8e0910bb536a3564b1b64659e945bd

* Sat May 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.32^0.git.8b5cc08-2
 - Update to 0.4.32

* Fri May 22 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^23.git.8efb1f0-2
 - Update to commit 8efb1f09bd6142b515926e5ed4d900cdfc6b08b1

* Thu May 21 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^22.git.ee42c71-2
 - Update to commit ee42c716c8bb6a1be06484407daa7e735aac6b63

* Thu May 21 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^21.git.036978b-2
 - Update to commit 036978bffc17dd33c9e4b8ac35f4b280712f8992

* Wed May 20 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^20.git.024717c-2
 - Update to commit 024717cb03356eb4e498ddf316bb442c23eaacc8

* Tue May 19 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^19.git.129fc83-2
 - Update to commit 129fc83e8d962ddae9b0090f1117e7ec1d36e795

* Sat May 16 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^18.git.0a7b7d4-2
 - Update to commit 0a7b7d4f6b6fc7f25c951855bcb5d26e8f745af3

* Thu May 14 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^17.git.ae6fec3-2
 - Update to commit ae6fec30a449955c8a819a5ce18ba083bf8a5245

* Thu May 14 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^16.git.3698195-2
 - Update to commit 3698195c49ddf391c80a112552e5c1422ea7d132

* Wed May 13 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^15.git.d32df97-2
 - Update to commit d32df979a48492333e6546a190a9665dec777ec9

* Wed May 13 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^14.git.37284f9-2
 - Update to commit 37284f9720c04db150fb957de4da29858a9c3e10

* Tue May 12 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^13.git.cf04087-2
 - Update to commit cf040876beda6fbcaaa423f6b3a271df91d240c3

* Sun May 10 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^12.git.740d39c-2
 - Update to commit 740d39c6d1ef6244c717441e6cf20fd0ed0a2d65

* Sun May 10 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^11.git.027c7e9-2
 - Update to commit 027c7e9c05951f1a6188a2452e756403ed12eacf

* Sat May 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^10.git.56cdd9f-2
 - Update to commit 56cdd9f7325d78b6caf37a44fdd0bde6a93f2cce

* Sat May 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^9.git.70b6068-2
 - Update to commit 70b6068ecba07f9fd0bc20fcba5edb072c0cf9c1

* Fri May 08 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^8.git.84a6eba-2
 - Update to commit 84a6eba99f2407032e82b08a7bef732138e245b7

* Thu May 07 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^7.git.469c420-2
 - Update to commit 469c42062674aac8631003160cd6b0d37ba58671

* Thu May 07 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^6.git.19c9af4-2
 - Update to commit 19c9af4dd093e2e8cd2728370ca60531c6e879cb

* Wed May 06 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^5.git.05b8d97-2
 - Update to commit 05b8d9782397132fa92da162e03aff7fe030aecf

* Mon May 04 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^4.git.dfaabd0-2
 - Update to commit dfaabd0187c3c75f7427ea6e3d9eda018eecd3a5

* Sat May 02 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^3.git.234105f-2
 - Update to commit 234105ff8dad024e817539deafffbffd14400464

* Fri May 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^2.git.c6418bc-2
 - Update to commit c6418bc3fd9f45e8b624513c04e654c46fc816ef

* Thu Apr 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^1.git.2e7d01e-2
 - Update to commit 2e7d01ec46dc37a85da2fb4944ed585e17f24834

* Sun Apr 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.31^0.git.2c72942-2
 - Update to 0.4.31

* Sat Apr 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.2^3.git.42ae8b8-2
 - Update to commit 42ae8b818cc0645be56063ea0cc350dcd8f19843

* Fri Apr 24 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.2^2.git.e11c10c-2
 - Update to commit e11c10c1fa64b6ac48a433a22bbb14bb3134483a

* Wed Apr 22 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.2^1.git.96fc30b-2
 - Update to commit 96fc30b1004ec68dd165014768393cfcce36d3b3

* Tue Apr 21 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.2^0.git.7eeb501-2
 - Update to 0.4.2

* Mon Apr 20 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^22.git.3c976b1-2
 - Update to commit 3c976b1ffb1e87aa65e6c93c7ccd7af16a062cfd

* Sat Apr 18 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^21.git.599360c-2
 - Update to commit 599360ce079ca1e39a10417b28d98df6c89201a4

* Sat Apr 18 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^20.git.f6beb43-2
 - Update to commit f6beb4320e7e02d95ba44920be6a97b9ac12876c

* Thu Apr 16 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^19.git.55e8ebf-2
 - Update to commit 55e8ebf5257388cc8bc2058d644a552eccdf4a60

* Tue Apr 14 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^18.git.f388a8f-2
 - Update to commit f388a8f4937dcbc196e2046e291f823b57ef68c0

* Sun Apr 12 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^17.git.13c9fda-2
 - Update to commit 13c9fdaa40422a88af2322e292fe421c2ac8ca1f

* Fri Apr 10 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^16.git.657d69a-2
 - Update to commit 657d69aa3b7248afcbe6bc0c56cf34a679cefc30

* Thu Apr 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^15.git.1a7ea1c-2
 - Update to commit 1a7ea1c09a634892c76d743b718ae7e341c14b52

* Thu Apr 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^14.git.08934a3-2
 - Update to commit 08934a3b0c523c3acf905604102780bed37d7eaf

* Wed Apr 08 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^13.git.95b4d66-2
 - Update to commit 95b4d665cf16f5cc6d38c3587dd7f9952d9e36b0

* Wed Apr 08 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^12.git.3c266d3-2
 - Update to commit 3c266d33e348e5a616bf5a3b36945c738039c50e

* Tue Apr 07 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^11.git.cbcd118-2
 - Update to commit cbcd11894c1959a5393cb3125e828ab7bbfc56f0

* Mon Apr 06 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^10.git.f20db6c-2
 - Update to commit f20db6caae44220ac0dd5ceadc92c11d3ba23dac

* Sun Apr 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^9.git.7e2528c-2
 - Update to commit 7e2528c538e7e1181c3d957c87fd6a265c764159

* Sat Apr 04 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^8.git.1957721-2
 - Update to commit 1957721f37fc64067548b60b41cc497b1101a6e9

* Sat Apr 04 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^7.git.132d401-2
 - Update to commit 132d40108b9b78218c539678b11c54d5a83fcb1a

* Fri Apr 03 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^6.git.58542e4-2
 - Update to commit 58542e4a7286dfebe0bd42dca6536a2953bab0c8

* Thu Apr 02 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^5.git.5e03e18-2
 - Update to commit 5e03e18c683a28e311c58b0f1602b775195b9dcb

* Wed Apr 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^4.git.6ebd9c3-2
 - Update to commit 6ebd9c3b32cb3ad7c2a5eb64577586b8da80b0d5

* Tue Mar 31 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^3.git.0b9df5d-2
 - Update to commit 0b9df5d5a09eab1fbc02b9a7a5a25f80631515c4

* Tue Mar 31 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^2.git.b305638-2
 - Update to commit b3056386f2e932c3d0786f5197ca3101a619bf3e

* Mon Mar 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^1.git.d5a1864-2
 - Update to commit d5a1864cfaea836c8c0c1f7ae69bccda665964cd

* Sun Mar 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.13^0.git.c85b3d6-2
 - Update to 0.4.13

* Sat Mar 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.12^10.git.26dcfc7-2
 - Update to commit 26dcfc7320510750c829f5b7c3a8cbf14ff224a2

* Sat Mar 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.12^9.git.5469887-2
 - Update to commit 54698875f0f5092c3c8aaf0fc0488c7302af6891

* Fri Mar 27 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.12^8.git.79a34b3-2
 - Update to commit 79a34b3d9cc727ad166b316be0054031fcb7ee10

* Fri Mar 27 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.12^7.git.f713cc5-2
 - Update to commit f713cc5840dc51684fb635193ece80479675788e

* Fri Mar 27 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.12^6.git.d7c86ca-2
 - Update to commit d7c86cadf6e935d24f77c66dc3ba7c1cb32f1d8d

* Thu Mar 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.12^5.git.66ccc3f-2
 - Update to commit 66ccc3f65d0fe08e495b4b785503c2044b07ebd6

* Wed Mar 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.12^4.git.e4270f1-2
 - Update to commit e4270f1d28113bc547770326268c8e360ad5e77c

* Wed Mar 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.12^3.git.518f065-2
 - Update to commit 518f065591510da254e25cb75e0d0d132c52207b

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.12^2.git.00e4f02-2
 - Update to commit 00e4f02a2ae92d0de8548aa72db35e85fd7a0f1f

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.12^1.git.40d796a-2
 - Update to commit 40d796a52f7b765cc4bd430dcbf84e3e638fd6f0

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.12^0.git.52cd1d0-2
 - Update to 0.4.12

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^71.git.52cd1d0-2
 - Update to commit 52cd1d09e0aac9dff5aa07a9cb1938a759b88b4d

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^70.git.b2e87cf-2
 - Update to commit b2e87cfc16bee17f49b58687617476da8d471136

* Mon Mar 16 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^69.git.1f705fc-2
 - Update to commit 1f705fc13a6f71f946c6fb0dded4cbe7d26e24c8

* Sun Mar 15 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^68.git.601bba6-2
 - Update to commit 601bba694a973f10f72c1ce782771b6bc0428ab9

* Sun Mar 15 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^67.git.a724bb7-2
 - Update to commit a724bb70fdae3edcf3c3e8096eaa0c96ba045d49

* Thu Mar 12 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^66.git.1ad0b9c-2
 - Update to commit 1ad0b9c737f2d029e8f41320d6c66fc1df164c70

* Wed Mar 11 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^65.git.a22ab35-2
 - Update to commit a22ab3511f436a4460bc18dc12673eff87e08b0e

* Sun Mar 08 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^64.git.2b9cc90-2
 - Update to commit 2b9cc9068e43f096520ba46a75f73a163cedbdef

* Sat Mar 07 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^63.git.8b4c9b3-2
 - Update to commit 8b4c9b3bf0a9797cfb923c1231c9ebfde8ad428e

* Fri Mar 06 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^62.git.cbf21d6-2
 - Update to commit cbf21d696f03bdf3c44626ac47794417d852094c

* Thu Mar 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^61.git.3435090-2
 - Update to commit 3435090558e36ee75fd00f9cf33ff951473600bf

* Thu Mar 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^60.git.863cb47-2
 - Update to commit 863cb47ff4cc3b7f1b0bcf503c9a43b4c1e90d14

* Thu Mar 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.0^59.git.5a83602-2
 - Update to commit 5a83602c10085ee4e0e06158caa6c5f3da871720

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
