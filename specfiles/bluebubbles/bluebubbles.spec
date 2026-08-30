%global debug_package %{nil}
%global __requires_exclude_from ^%{_libexecdir}/%{name}/.*$
%global __provides_exclude_from ^%{_libexecdir}/%{name}/.*$

%global appid app.bluebubbles.BlueBubbles
%global flutter_version 3.44.6

%global tag 2.1.1.91
%global appver %(echo %{tag} | sed -E 's/\\.[0-9]+$//')
%global build_num %(echo %{tag} | sed -E 's/^.*\\.//')
%global dirtag %(echo %{tag} | sed -E 's/\\.([0-9]+)$/-\\1/')

Name:       bluebubbles
Version:    %{tag}
Release:    1%{?dist}
Summary:    iMessage client for Linux, part of the BlueBubbles ecosystem

License:    Apache-2.0
URL:        https://bluebubbles.app
Source0:    https://github.com/BlueBubblesApp/bluebubbles-app/archive/refs/tags/v%{appver}+%{build_num}.tar.gz

ExclusiveArch:  aarch64

BuildRequires:  git
BuildRequires:  curl
BuildRequires:  unzip
BuildRequires:  jq
BuildRequires:  clang
BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  pkgconf-pkg-config
BuildRequires:  patchelf
BuildRequires:  gtk3-devel
BuildRequires:  webkit2gtk4.1-devel
BuildRequires:  mpv-devel
BuildRequires:  libayatana-appindicator-gtk3-devel
BuildRequires:  libnotify-devel
BuildRequires:  json-glib-devel

Requires:       gtk3
Requires:       webkit2gtk4.1
Requires:       mpv-libs
Requires:       libayatana-appindicator-gtk3
Requires:       libnotify
Requires:       json-glib
Requires:       wmctrl

%description
BlueBubbles is a cross-platform ecosystem that brings iMessage to Android,
Windows, Linux, and the web by pairing with a BlueBubbles Server running on a
Mac. This package builds the Flutter-based desktop client from source for
Linux.

%prep
%autosetup -n bluebubbles-app-%{dirtag}

echo 'KLIPY_API_KEY=' > .env

%build
export CFLAGS="$(sed -E 's/-specs=[^ ]+//g' <<<"$CFLAGS")"
export CXXFLAGS="$(sed -E 's/-specs=[^ ]+//g' <<<"$CXXFLAGS")"
export LDFLAGS="$(sed -E 's/-specs=[^ ]+//g' <<<"$LDFLAGS")"

FLUTTER_ROOT=%{_builddir}/flutter-sdk
git clone -q --depth 1 --branch %{flutter_version} \
  https://github.com/flutter/flutter.git "$FLUTTER_ROOT"
export PATH="$FLUTTER_ROOT/bin:$PATH"

export CI=true
export FLUTTER_SUPPRESS_ANALYTICS=true
flutter config --no-analytics --no-cli-animations

flutter precache --linux

flutter pub get --enforce-lockfile
flutter build linux --release -v --no-pub

tmp=$(mktemp)
jq --arg v "%{appver}" '.version = $v' \
  build/linux/arm64/release/bundle/data/flutter_assets/version.json > "$tmp"
mv "$tmp" build/linux/arm64/release/bundle/data/flutter_assets/version.json

%install
install -d %{buildroot}%{_libexecdir}/%{name}
cp -a build/linux/arm64/release/bundle/. %{buildroot}%{_libexecdir}/%{name}/
chmod 0755 %{buildroot}%{_libexecdir}/%{name}/bluebubbles

find %{buildroot}%{_libexecdir}/%{name}/lib -name '*.so*' -print0 | \
  xargs -0 -r patchelf --set-rpath '$ORIGIN'

install -d %{buildroot}%{_bindir}
ln -s %{_libexecdir}/%{name}/bluebubbles %{buildroot}%{_bindir}/%{name}

install -Dpm0644 flatpak/icon/128x128.png \
  %{buildroot}%{_datadir}/icons/hicolor/128x128/apps/%{appid}.png

install -Dpm0644 flatpak/%{appid}.desktop \
  %{buildroot}%{_datadir}/applications/%{appid}.desktop

install -Dpm0644 flatpak/%{appid}.metainfo.xml \
  %{buildroot}%{_metainfodir}/%{appid}.metainfo.xml

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_libexecdir}/%{name}/
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/icons/hicolor/128x128/apps/%{appid}.png
%{_metainfodir}/%{appid}.metainfo.xml

%changelog
* Fri Aug 14 2026 Lachlan Marie <lchlnm@pm.me> - 2.1.1.91-1
 - Update to 2.1.1.91

* Mon Aug 10 2026 Lachlan Marie <lchlnm@pm.me> - 2.1.0.90-1
- Initial RPM packaging of bluebubbles (built from source, online build)
