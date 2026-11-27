%global aurora_commit d0355b1d4aabbda605da5def13af1097310f6d45
%global aurora_src aurora-sep-userspace-%{aurora_commit}

Name:           libfprint
Version:        1.94.100
Release:        1%{?dist}.aurora13
Summary:        Toolkit for fingerprint scanner

License:        LGPL-2.1-or-later AND NIST-PD
URL:            https://github.com/aurora-silicon/aurora-sep-userspace
Source0:        https://gitlab.freedesktop.org/libfprint/libfprint/-/archive/v%{version}/libfprint-v%{version}.tar.gz
Source1:        https://github.com/aurora-silicon/aurora-sep-userspace/archive/%{aurora_commit}/aurora-sep-userspace-%{aurora_commit}.tar.gz
Source2:        fprintd-sep-touchid.conf

BuildRequires:  meson
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  git
BuildRequires:  openssl-devel
BuildRequires:  pkgconfig(glib-2.0) >= 2.50
BuildRequires:  pkgconfig(gio-2.0) >= 2.44.0
BuildRequires:  pkgconfig(gusb) >= 0.3.0
BuildRequires:  pkgconfig(nss)
BuildRequires:  pkgconfig(pixman-1)
BuildRequires:  gtk-doc
BuildRequires:  libgudev-devel
BuildRequires:  systemd
BuildRequires:  systemd-rpm-macros
BuildRequires:  gobject-introspection-devel
BuildRequires:  python3-cairo python3-gobject cairo-devel
BuildRequires:  umockdev >= 0.13.2
BuildRequires:  selinux-policy-devel
BuildRequires:  bzip2

Provides:       libfprint(aurora-sep) = 4
Provides:       libfprint(aurora-sep) = 5
Provides:       libfprint(aurora-sep-lockout) = 1
Provides:       libfprint(aurora-sep-password-reasons) = 1
Provides:       libfprint(aurora-sep-password-required) = 1
Requires:       (%{name}-selinux = %{version}-%{release} if selinux-policy-targeted)

%description
libfprint offers support for consumer fingerprint reader devices.

This build adds the aurora driver for Apple Touch ID, which talks to the
apple_sep kernel driver through /dev/sep-bio. It replaces Fedora's libfprint
of the same version.

%package        selinux
Summary:        SELinux policy module letting fprintd follow the lid switch
BuildArch:      noarch
Requires:       selinux-policy-targeted
%{?selinux_requires}

%description    selinux
libfprint hides a fingerprint reader that a closed laptop lid covers, which
needs fprintd to read the lid switch. This module allows fprintd read-only
access to input devices.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package        tests
Summary:        Tests for the %{name} package
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description tests
The %{name}-tests package contains tests that can be used to verify
the functionality of the installed %{name} package.

%prep
%setup -q -n libfprint-v%{version}
%setup -q -T -D -a 1 -n libfprint-v%{version}
for patch in libfprint-1.94.100-apple-sep.patch \
    0002-aurora-report-unusable-captures-as-retries.patch \
    0003-hide-lid-covered-readers-while-the-lid-is-closed.patch \
    0004-aurora-refuse-unbound-enrollment.patch \
    0005-aurora-support-v4-and-v5.patch \
    0006-aurora-report-finger-lift-and-lockout.patch \
    0007-aurora-name-retry-causes-and-keep-waiting.patch \
    0008-aurora-report-the-touch-id-lockout-as-locked-out.patch \
    0009-aurora-say-why-touch-id-needs-the-password.patch \
    0010-let-a-front-end-ask-whether-the-reader-needs-the-password.patch \
    0011-aurora-name-a-touch-of-another-enrolled-finger.patch; do
    patch -p1 --fuzz=0 -i %{aurora_src}/libfprint/$patch
done
install -Dpm0644 %{aurora_src}/libfprint/apple-sep.h aurora-uapi/linux/apple-sep.h

%build
export CFLAGS="%{build_cflags} -I$(pwd)/aurora-uapi"
%meson -Ddrivers=all
%meson_build
mkdir -p selinux
cp -p %{aurora_src}/libfprint/aurora_fprintd_lid.te selinux/
make -C selinux -f %{_datadir}/selinux/devel/Makefile aurora_fprintd_lid.pp
bzip2 -9 selinux/aurora_fprintd_lid.pp

%install
%meson_install
install -Dpm0644 %{aurora_src}/libfprint/fprintd-aurora-touchid.conf %{buildroot}%{_unitdir}/fprintd.service.d/50-libfprint-aurora-touchid.conf
install -Dpm0644 %{SOURCE2} %{buildroot}%{_unitdir}/fprintd.service.d/60-sep-touchid.conf
install -Dpm0644 selinux/aurora_fprintd_lid.pp.bz2 %{buildroot}%{_datadir}/selinux/packages/targeted/aurora_fprintd_lid.pp.bz2

%pre selinux
%selinux_relabel_pre -s targeted

%post selinux
%selinux_modules_install -s targeted %{_datadir}/selinux/packages/targeted/aurora_fprintd_lid.pp.bz2

%postun selinux
if [ $1 -eq 0 ]; then
    %selinux_modules_uninstall -s targeted aurora_fprintd_lid
fi

%posttrans selinux
%selinux_relabel_post -s targeted

%ldconfig_scriptlets

%check
python3 %{aurora_src}/libfprint/test_interface.py libfprint/drivers/aurora/aurora.c %{aurora_src}/libfprint/libfprint-1.94.100-apple-sep.patch
python3 %{aurora_src}/libfprint/test_lockout_reason.py libfprint/drivers/aurora/aurora.c

%files
%license COPYING
%doc NEWS THANKS AUTHORS README.md
%{_libdir}/*.so.*
%{_libdir}/girepository-1.0/*.typelib
%{_udevhwdbdir}/60-autosuspend-libfprint-2.hwdb
%{_udevrulesdir}/70-libfprint-2.rules
%{_datadir}/metainfo/org.freedesktop.libfprint.metainfo.xml
%dir %{_unitdir}/fprintd.service.d
%{_unitdir}/fprintd.service.d/50-libfprint-aurora-touchid.conf
%{_unitdir}/fprintd.service.d/60-sep-touchid.conf

%files selinux
%{_datadir}/selinux/packages/targeted/aurora_fprintd_lid.pp.bz2

%files devel
%doc HACKING.md
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/%{name}-2.pc
%{_datadir}/gir-1.0/*.gir
%{_datadir}/gtk-doc/html/libfprint-2/

%files tests
%{_libexecdir}/installed-tests/libfprint-2/
%{_datadir}/installed-tests/libfprint-2/

%changelog
* Fri Nov 27 2026 Lachlan Marie <lchlnm@pm.me> - 1.94.100-1.aurora13
- Build aurora-sep-userspace libfprint patches on Fedora 1.94.100
- Pin aurora-sep-userspace d0355b1
- Order fprintd after sep-touchid.service
