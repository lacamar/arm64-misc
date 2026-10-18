%global debug_package %{nil}
%global __requires_exclude_from ^%{_libexecdir}/%{name}/.*$
%global __provides_exclude_from ^%{_libexecdir}/%{name}/.*$
%global srcdir app--standardnotes-desktop-%{version}
%global appdir %{_libexecdir}/%{name}

Name:           standard-notes
Version:        3.202.10
Release:        1%{?dist}
Summary:        End-to-end encrypted notes app

License:        AGPL-3.0-only
URL:            https://github.com/standardnotes/app
Source0:        https://github.com/standardnotes/app/archive/refs/tags/@standardnotes/desktop@%{version}.tar.gz#/%{name}-%{version}.tar.gz

ExclusiveArch:  aarch64

BuildRequires:  /usr/bin/node
BuildRequires:  nodejs22-devel
BuildRequires:  gcc-c++
BuildRequires:  make
BuildRequires:  python3
BuildRequires:  libsecret-devel
BuildRequires:  desktop-file-utils

Requires:       electron
Requires:       libsecret

%description
Standard Notes desktop app, an end-to-end encrypted notes app.

%prep
%autosetup -n %{srcdir}

%build
export PATH=/usr/bin:$PATH
export YARN_ENABLE_TELEMETRY=0
export YARN_ENABLE_NETWORK=0
export ELECTRON_SKIP_BINARY_DOWNLOAD=1
export PUPPETEER_SKIP_DOWNLOAD=1
export HUSKY=0
export npm_config_nodedir=/usr
export NODE_OPTIONS=--max-old-space-size=8192
yarn() { node .yarn/releases/yarn-3.2.1.cjs "$@"; }
yarn install --immutable
yarn build:desktop
mkdir eldist
touch eldist/electron
cd packages/desktop
node ../../.yarn/releases/yarn-3.2.1.cjs electron-builder --linux --dir \
  -c.electronDist=../../eldist -c.npmRebuild=false -c.asar=false

%install
install -d %{buildroot}%{appdir}
cp -a packages/desktop/dist/linux-arm64-unpacked/resources/app/. %{buildroot}%{appdir}/
find %{buildroot}%{appdir} -name '*.map' -delete
find %{buildroot}%{appdir} -path '*/prebuilds/*' ! -path '*/linux-arm64/*' -type f -delete
find %{buildroot}%{appdir} -name '*musl*.node' -delete
find %{buildroot}%{appdir} -type d -empty -delete
rm -rf %{buildroot}%{appdir}/node_modules/sqlite3/build-tmp-napi-v6

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'SH'
#!/bin/sh
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
  export ELECTRON_OZONE_PLATFORM_HINT=wayland
fi
exec /usr/bin/electron %{appdir} "$@"
SH
chmod 755 %{buildroot}%{_bindir}/%{name}

install -Dm644 packages/desktop/build/icon/Icon-512x512.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/%{name}.png

cat > %{name}.desktop <<'DESKTOP'
[Desktop Entry]
Name=Standard Notes
Comment=An end-to-end encrypted notes app
Exec=standard-notes %U
Icon=standard-notes
Terminal=false
Type=Application
StartupWMClass=standard-notes
MimeType=x-scheme-handler/standardnotes;
Categories=Office;
DESKTOP
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{name}.desktop

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{appdir}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/512x512/apps/%{name}.png

%changelog
* Sun Oct 18 2026 lacamar <lchlnm@pm.me> - 3.202.10-1
- Initial package
