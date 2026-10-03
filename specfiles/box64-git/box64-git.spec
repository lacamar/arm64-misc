%global bumpver 30
%global _name box64
%global tag 0.4.5.1

%global commit 50069bcf69f62a780074cf8458c5339f00579a5a
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:           %{_name}-git
Version:        %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:        4%{?dist}
Conflicts:      %{_name}
Provides:       %{_name} = %{version}-%{release}
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

Requires:       alternatives
Requires:       %{_name}-data = %{version}-%{release}
Recommends:     %{name}-binfmts = %{version}-%{release}
Requires(post): %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives

%description    %{common_description}

%package        data
Provides:       box64-data = %{version}-%{release}
Summary:        Common files for %{_name}
BuildArch:      noarch
%description    data %{common_description}

This package provides common data files for box64.

%package        binfmts
Conflicts:      box64-binfmts
Provides:       box64-binfmts = %{version}-%{release}
Summary:        binfmt_misc handler configurations for box64

%description    binfmts %{common_description}

This package provides binfmt_misc handler configurations to use box64 to
execute x86_64 binaries.

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
  %{_name}.asahi

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

%files asahi
%ghost %{_bindir}/%{_name}
%{_bindir}/%{_name}.asahi

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
