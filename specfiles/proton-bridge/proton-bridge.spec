%global debug_package %{nil}

Name:           proton-bridge
Version:        3.25.0
Release:        1%{?dist}
Summary:        IMAP/SMTP bridge for Proton Mail, with GUI

License:        GPL-3.0-or-later AND MIT
URL:            https://github.com/ProtonMail/proton-bridge

# Build vendor tarball with:
#   git archive <ref> | tar -x -C proton-bridge-VERSION
#   cd proton-bridge-VERSION && go mod vendor
#   tar czf proton-bridge-VERSION.tar.gz proton-bridge-VERSION

Source0:        proton-bridge-%{version}.tar.gz
Source1:        proton-bridge.service
# sentry-native's self-contained release asset (bundles its vendored deps,
# unlike GitHub's auto-generated source tarball). Not in Fedora's repos.
# https://github.com/getsentry/sentry-native/releases/download/0.16.3/sentry-native.zip
Source2:        sentry-native-0.16.3.zip

Patch0:         0001-linux-arm64-system-deps-no-vcpkg.patch

ExclusiveArch:  aarch64

BuildRequires:  golang >= 1.26
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  unzip
BuildRequires:  pkgconf-pkg-config
BuildRequires:  libfido2-devel
BuildRequires:  libcbor-devel
BuildRequires:  openssl-devel
BuildRequires:  libsecret-devel
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtdeclarative-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  qt6-qttools-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  libglvnd-devel
BuildRequires:  grpc-devel
BuildRequires:  grpc-plugins
BuildRequires:  protobuf-devel
BuildRequires:  protobuf-compiler
BuildRequires:  systemd-rpm-macros

Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

Recommends:     gnupg2
Recommends:     pass

%description
Proton Mail Bridge runs in the background and seamlessly encrypts and
decrypts your mail as it enters and leaves your computer, letting any
IMAP/SMTP-capable mail client (Thunderbird, Outlook, Apple Mail, ...)
work with Proton Mail's end-to-end encryption.

%prep
%autosetup -p1 -n %{name}-%{version}
unzip -q %{SOURCE2} -d %{_builddir}/sentry-native-src

%build
export GO111MODULE=on
export GOFLAGS=-mod=vendor
export GOPROXY=off
export GOSUMDB=off
export CGO_ENABLED=1

make build-nogui \
    BRIDGE_APP_VERSION=%{version} \
    BUILD_ENV=prod

cmake -S %{_builddir}/sentry-native-src -B %{_builddir}/sentry-native-build \
    -DCMAKE_BUILD_TYPE=Release \
    -DSENTRY_BACKEND=none \
    -DSENTRY_TRANSPORT=none \
    -DBUILD_SHARED_LIBS=OFF \
    -DSENTRY_BUILD_TESTS=OFF \
    -DSENTRY_BUILD_EXAMPLES=OFF \
    -DCMAKE_INSTALL_PREFIX=%{_builddir}/sentry-install \
    -G Ninja
cmake --build %{_builddir}/sentry-native-build
cmake --install %{_builddir}/sentry-native-build

cmake -S internal/frontend/bridge-gui -B %{_builddir}/bridge-gui-build \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_TESTING=OFF \
    -DBRIDGE_GUI_BUNDLE_QT=OFF \
    -DBRIDGE_APP_VERSION=%{version} \
    -DBRIDGE_APP_FULL_NAME="Proton Mail Bridge" \
    -DBRIDGE_VENDOR="Proton AG" \
    -DBRIDGE_REVISION=NOGIT \
    -DBRIDGE_TAG=NOTAG \
    -DBRIDGE_BUILD_ENV=prod \
    -DCMAKE_PREFIX_PATH=%{_builddir}/sentry-install \
    -DCMAKE_SKIP_RPATH=ON \
    -G Ninja
cmake --build %{_builddir}/bridge-gui-build --target bridge-gui

%install
install -Dpm0755 bridge %{buildroot}%{_libexecdir}/%{name}/bridge
install -Dpm0755 proton-bridge %{buildroot}%{_libexecdir}/%{name}/proton-bridge
install -Dpm0755 %{_builddir}/bridge-gui-build/bridge-gui/bridge-gui %{buildroot}%{_libexecdir}/%{name}/bridge-gui
install -dm0755 %{buildroot}%{_bindir}
ln -s %{_libexecdir}/%{name}/proton-bridge %{buildroot}%{_bindir}/proton-bridge
install -Dpm0644 %{SOURCE1} %{buildroot}%{_userunitdir}/proton-bridge.service

install -Dpm0644 dist/bridge.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/proton-bridge.svg
install -Dpm0644 dist/proton-bridge.desktop %{buildroot}%{_datadir}/applications/proton-bridge.desktop
sed -i \
    -e 's/^Exec=.*/Exec=proton-bridge/' \
    -e 's/^Icon=.*/Icon=proton-bridge/' \
    %{buildroot}%{_datadir}/applications/proton-bridge.desktop

%post
%systemd_user_post proton-bridge.service

%preun
%systemd_user_preun proton-bridge.service

%postun
%systemd_user_postun_with_restart proton-bridge.service

%files
%license LICENSE
%doc Changelog.md README.md
%{_libexecdir}/%{name}/bridge
%{_libexecdir}/%{name}/proton-bridge
%{_libexecdir}/%{name}/bridge-gui
%{_bindir}/proton-bridge
%{_userunitdir}/proton-bridge.service
%{_datadir}/icons/hicolor/scalable/apps/proton-bridge.svg
%{_datadir}/applications/proton-bridge.desktop

%changelog
* Fri Aug 14 2026 Lachlan Marie <lchlnm@pm.me> - 3.25.0-1
- GUI (bridge-gui) build for Fedora 44 aarch64, with a systemd --user
  service that autostarts it minimized to the tray, plus BuildRequires
  and desktop/icon files.
