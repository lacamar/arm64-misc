%global udevdir %(pkg-config --variable=udevdir udev)
%global tag 1.32.0

Name:           libinput
Version:        %{tag}
Release:        4%{?dist}
Summary:        Input device library

# SPDX
License:        MIT
URL:            https://gitlab.freedesktop.org/libinput/libinput/-/archive/
Source0:        https://gitlab.freedesktop.org/libinput/libinput/-/archive/%{version}/libinput-%{version}.tar.bz2

Patch0:         enable_apple_edge_palm_detection.patch

BuildRequires:  git-core
BuildRequires:  gcc
BuildRequires:  meson
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(mtdev) >= 1.1.0
BuildRequires:  pkgconfig(libevdev) >= 0.4
BuildRequires:  pkgconfig(libwacom) >= 0.20
BuildRequires:  pkgconfig(udev)
BuildRequires:  python3-rpm-macros

BuildRequires:  lua-devel

Obsoletes:      %{name}-test < %{version}-%{release}

%description
libinput is a library that handles input devices for display servers and other
applications that need to directly deal with input devices.

It provides device detection, device handling, input device event processing
and abstraction so minimize the amount of custom input code the user of
libinput need to provide the common set of functionality that users expect.


%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%package        utils
Summary:        Utilities and tools for debugging %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python3-pyudev python3-libevdev

%description    utils
The %{name}-utils package contains tools to debug hardware and analyze
%{name}.

%prep
%autosetup -S git -p0
# Replace whatever the source uses with the approved call
%py3_shebang_fix $(git grep -l  '#!/usr/bin/.*python3')

%build
%meson -Ddebug-gui=false \
       -Ddocumentation=false \
       -Dtests=false \
       -Dautoload-plugins=true \
       -Dudev-dir=%{udevdir}
%meson_build

%install
%meson_install
rm %{buildroot}{%{_libexecdir}/libinput/libinput-test,%{_mandir}/man1/libinput-test.1*}

%files
%doc COPYING
%{_libdir}/libinput.so.*
%{udevdir}/libinput-device-group
%{udevdir}/libinput-fuzz-to-zero
%{udevdir}/libinput-fuzz-extract
%{udevdir}/rules.d/80-libinput-device-groups.rules
%{udevdir}/rules.d/90-libinput-fuzz-override.rules
%{_bindir}/libinput
%dir %{_libexecdir}/libinput/
%{_libexecdir}/libinput/libinput-debug-events
%{_libexecdir}/libinput/libinput-list-devices
%{_mandir}/man1/libinput.1*
%dir %{_datadir}/libinput
%{_datadir}/libinput/*.quirks
%dir %{_datadir}/zsh
%dir %{_datadir}/zsh/site-functions
%{_datadir}/zsh/site-functions/*
%{_mandir}/man1/libinput-list-devices.1*
%{_mandir}/man1/libinput-debug-events.1*

%files devel
%{_includedir}/libinput.h
%{_libdir}/libinput.so
%{_libdir}/pkgconfig/libinput.pc

%files utils
%{_libexecdir}/libinput/libinput-{analyze,debug-tablet,list-kernel-devices,measure,quirks,record,replay}*
%{_mandir}/man1/libinput-{analyze,debug-tablet,list-kernel-devices,measure,quirks,record,replay}*.1*


%changelog
* Sat Oct 03 2026 Lachlan Marie <lchlnm@pm.me> - 1.32.0-4
 - Drop test subpackage

* Fri Sep 18 2026 Lachlan Marie <lchlnm@pm.me> - 1.32.0-3
 - Update to 1.32.0

* Wed Sep 09 2026 Lachlan Marie <lchlnm@pm.me> - 1.31.901-3
 - Update to 1.31.901

* Fri Jun 05 2026 Lachlan Marie <lchlnm@pm.me> - 1.30.4-3
 - Update to 1.30.4

* Thu Jun 04 2026 Lachlan Marie <lchlnm@pm.me> - 1.31.3-3
 - Update to 1.31.3

* Fri May 15 2026 Lachlan Marie <lchlnm@pm.me> - 1.31.2-3
 - Update to 1.31.2
