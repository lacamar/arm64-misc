%global forgeurl https://github.com/iDescriptor/iDescriptor

# lib/idevice-rs and lib/uxplay are git submodules; GitHub's tag archive
# doesn't include submodule content, so they're pulled in as separate
# sources pinned to the exact commit iDescriptor v%{version} points at
# (see .gitmodules and `git ls-tree v%{version} -- lib`).
%global idevice_commit ef0c66073e79f513a9e5a541d5fa3682b45d8c5f
%global uxplay_commit  eaca2458946d8a283df3b872f25c6b7cc98be411

Name:           idescriptor
Version:        0.6.2
Release:        2%{?dist}
Summary:        Cross-platform tool for managing iDevices (iPhone, iPad, iPod)

License:        AGPL-3.0-or-later
URL:            %{forgeurl}
Source0:        %{forgeurl}/archive/refs/tags/v%{version}/iDescriptor-%{version}.tar.gz
Source1:        https://github.com/uncor3/idevice/archive/%{idevice_commit}/idevice-rs-%{idevice_commit}.tar.gz
Source2:        https://github.com/iDescriptor/uxplay/archive/%{uxplay_commit}/uxplay-%{uxplay_commit}.tar.gz

BuildRequires:  cargo
BuildRequires:  anda-srpm-macros
BuildRequires:  cargo-rpm-macros
BuildRequires:  systemd-rpm-macros
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  cmake >= 3.16
BuildRequires:  pkgconf-pkg-config
BuildRequires:  git
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qtdeclarative-private-devel
BuildRequires:  qt6-qtmultimedia-devel
BuildRequires:  qt6-qtpositioning-devel
BuildRequires:  qt6-qtserialport-devel
BuildRequires:  qt6-qttools-devel
BuildRequires:  openssl-devel
BuildRequires:  libplist-devel
BuildRequires:  libheif-devel
BuildRequires:  glib2-devel
BuildRequires:  gstreamer1-devel
BuildRequires:  gstreamer1-plugins-base-devel
BuildRequires:  ffmpeg-free-devel
BuildRequires:  avahi-compat-libdns_sd-devel
BuildRequires:  fuse3-devel
BuildRequires:  libusb1-devel
BuildRequires:  desktop-file-utils

Requires:       gstreamer1-plugins-good
Requires:       gstreamer1-plugins-bad-free
Requires:       gstreamer1-plugins-ugly-free
Requires:       hicolor-icon-theme

%description
iDescriptor is a free, open-source, cross-platform tool for managing
Apple mobile devices (iPhone, iPad, iPod) over USB or Wi-Fi. It can
browse files and photos, inspect device/cable/diagnostic info, create
and inspect backups, mirror the device screen via AirPlay, manage apps
and developer disk images, and restart/erase/shut down the device.

%prep
%autosetup -n iDescriptor-%{version}

rm -rf lib/idevice-rs lib/uxplay
tar xf %{SOURCE1}
mv idevice-*/ lib/idevice-rs
tar xf %{SOURCE2}
mv uxplay-*/ lib/uxplay

%build
%cargo_prep_online

export IDESCRIPTOR_PACKAGE_MANAGER_MESSAGE="Please update iDescriptor with 'dnf upgrade idescriptor'."
%cargo_build -f package_manager

%install
install -Dm755 target/rpm/idescriptor %{buildroot}%{_bindir}/idescriptor

install -Dm644 io.github.idescriptor.iDescriptor.desktop \
  %{buildroot}%{_datadir}/applications/io.github.idescriptor.iDescriptor.desktop
install -Dm644 io.github.idescriptor.iDescriptor.metainfo.xml \
  %{buildroot}%{_metainfodir}/io.github.idescriptor.iDescriptor.metainfo.xml
install -Dm644 packaging/shared/resources/app-icon/icon-512.png \
  %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/io.github.idescriptor.iDescriptor.png

# iDescriptor looks for its UDEV rules specifically at this path (see UDEV.md)
# to grant non-root USB access to recovery/DFU-mode devices.
install -Dm644 /dev/stdin %{buildroot}%{_udevrulesdir}/99-idevice.rules <<EOF
SUBSYSTEM=="usb", ATTR{idVendor}=="05ac", MODE="0666", GROUP="idevice"
EOF

desktop-file-validate %{buildroot}%{_datadir}/applications/io.github.idescriptor.iDescriptor.desktop

%post
getent group idevice >/dev/null || groupadd -r idevice
udevadm control --reload-rules >/dev/null 2>&1 || :
udevadm trigger --subsystem-match=usb >/dev/null 2>&1 || :

%postun
udevadm control --reload-rules >/dev/null 2>&1 || :

%files
%license LICENSE
%doc README.md AUTHORS
%{_bindir}/idescriptor
%{_datadir}/applications/io.github.idescriptor.iDescriptor.desktop
%{_metainfodir}/io.github.idescriptor.iDescriptor.metainfo.xml
%{_datadir}/icons/hicolor/512x512/apps/io.github.idescriptor.iDescriptor.png
%{_udevrulesdir}/99-idevice.rules

%changelog
* Wed Sep 02 2026 Lachlan Marie <lchlnm@pm.me> - 0.6.2-2
- Drop the >= 2.7.0 version constraint on libplist-devel: Fedora 43 only
  ships 2.6.0, so the constraint made `dnf5 builddep` fail to resolve on
  that release (Fedora 44 has 2.7.0 too, so this wasn't needed there
  either -- it only mirrored what upstream CI happens to use).

* Wed Sep 02 2026 Lachlan Marie <lchlnm@pm.me> - 0.6.2-1
- Initial packaging
