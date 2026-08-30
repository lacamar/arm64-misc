%global debug_package %{nil}
%global __requires_exclude_from ^%{_libexecdir}/%{name}/.*$
%global __provides_exclude_from ^%{_libexecdir}/%{name}/.*$

%global flutter_version 3.41.9
%global rust_toolchain 1.97.1

Name:       localsend
Version:    1.18.1
Release:    2%{?dist}
Summary:    An open source cross-platform alternative to AirDrop

License:    Apache-2.0
URL:        https://localsend.org
Source0:    https://github.com/localsend/localsend/archive/refs/tags/v%{version}.tar.gz
Source1:    localsend.service
Source2:    fake-rustup.sh
Source3:    org.localsend.localsend_app.desktop

Patch0:     0002-tray_manager-ayatana-deprecated-appindicator-new.patch

ExclusiveArch:  aarch64

BuildRequires:  git
BuildRequires:  curl
BuildRequires:  unzip
BuildRequires:  clang
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  pkgconf-pkg-config
BuildRequires:  patchelf
BuildRequires:  gtk3-devel
BuildRequires:  libayatana-appindicator-gtk3-devel
BuildRequires:  xdg-user-dirs
BuildRequires:  cargo = %{rust_toolchain}
BuildRequires:  rust = %{rust_toolchain}
BuildRequires:  mesa-libGL-devel
BuildRequires:  systemd-rpm-macros

Requires:       gtk3
Requires:       libayatana-appindicator-gtk3
Requires:       xdg-user-dirs
Requires(post):   systemd
Requires(preun):  systemd
Requires(postun): systemd

%description
LocalSend is an open source cross-platform app that lets you share files
and messages with nearby devices without an internet connection. This
package builds the Flutter-based desktop client (with its Rust protocol
core, built via cargokit) from source for Linux, plus a systemd --user
unit that starts it in the background the same way LocalSend's own
login-autostart does:

    systemctl --user enable --now localsend

%prep
%setup -q -n %{name}-%{version}

%build
export CFLAGS="$(sed -E 's/-specs=[^ ]+//g' <<<"$CFLAGS")"
export CXXFLAGS="$(sed -E 's/-specs=[^ ]+//g' <<<"$CXXFLAGS")"
export LDFLAGS="$(sed -E 's/-specs=[^ ]+//g' <<<"$LDFLAGS")"

install -Dpm0755 %{SOURCE2} %{_builddir}/fake-rustup-bin/rustup
export PATH="%{_builddir}/fake-rustup-bin:$PATH"

FLUTTER_ROOT=%{_builddir}/flutter-sdk
rm -rf "$FLUTTER_ROOT"
git clone -q --depth 1 --branch %{flutter_version} \
  https://github.com/flutter/flutter.git "$FLUTTER_ROOT"
export PATH="$FLUTTER_ROOT/bin:$PATH"

export CI=true
export FLUTTER_SUPPRESS_ANALYTICS=true
flutter config --no-analytics --no-cli-animations

flutter precache --linux

cd app
flutter pub get --enforce-lockfile

tray_manager_dir=$(ls -d "$HOME"/.pub-cache/hosted/pub.dev/tray_manager-*)
patch -p1 -d "$tray_manager_dir" < %{PATCH0}

flutter build linux --release -v --no-pub

%install
install -d %{buildroot}%{_libexecdir}/%{name}
cp -a app/build/linux/arm64/release/bundle/. %{buildroot}%{_libexecdir}/%{name}/
chmod 0755 %{buildroot}%{_libexecdir}/%{name}/localsend_app

find %{buildroot}%{_libexecdir}/%{name}/lib -name '*.so*' -print0 | \
  xargs -0 -r patchelf --set-rpath '$ORIGIN'

install -d %{buildroot}%{_bindir}
ln -s %{_libexecdir}/%{name}/localsend_app %{buildroot}%{_bindir}/%{name}

install -Dpm0644 %{SOURCE1} %{buildroot}%{_userunitdir}/localsend.service
install -Dpm0644 %{SOURCE3} %{buildroot}%{_datadir}/applications/org.localsend.localsend_app.desktop
install -Dpm0644 app/assets/img/logo-512.png \
  %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/localsend.png

%post
%systemd_user_post localsend.service

%preun
%systemd_user_preun localsend.service

%postun
%systemd_user_postun_with_restart localsend.service

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_libexecdir}/%{name}/
%{_userunitdir}/localsend.service
%{_datadir}/applications/org.localsend.localsend_app.desktop
%{_datadir}/icons/hicolor/512x512/apps/localsend.png

%changelog
* Fri Aug 21 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.1-2
- Fix the desktop icon not showing in the window titlebar: the compiled
  binary advertises GTK application-id "org.localsend.localsend_app"
  (set in app/linux/CMakeLists.txt), but the desktop file was installed
  as localsend.desktop, so compositors couldn't correlate the running
  window to any installed .desktop entry and fell back to a generic
  icon. Renamed the desktop file (and its installed path) to
  org.localsend.localsend_app.desktop to match, and added
  StartupWMClass=org.localsend.localsend_app as a belt-and-suspenders
  hint for window managers that only check that field. Icon= still
  points at the already-correctly-installed localsend icon.

* Fri Aug 14 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.1-1
- Initial RPM packaging of LocalSend (Flutter + Rust/cargokit) for
  Fedora 44 aarch64, with a systemd --user service that autostarts it
  minimized to the tray.
