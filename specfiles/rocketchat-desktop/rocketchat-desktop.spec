%global debug_package %{nil}
%global __requires_exclude_from ^%{_libexecdir}/%{name}/.*$
%global __provides_exclude_from ^%{_libexecdir}/%{name}/.*$
%global srcdir Rocket.Chat.Electron-%{version}
%global appdir %{_libexecdir}/%{name}

Name:           rocketchat-desktop
Version:        4.18.3
Release:        3%{?dist}
Summary:        Desktop client for Rocket.Chat

License:        MIT
URL:            https://github.com/RocketChat/Rocket.Chat.Electron
Source0:        %{url}/archive/refs/tags/%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-yarn-cache.tar.zst

ExclusiveArch:  aarch64

BuildRequires:  /usr/bin/node
BuildRequires:  nodejs22-devel
BuildRequires:  zstd
BuildRequires:  desktop-file-utils

Requires:       electron

%description
Rocket.Chat desktop client, running on the system Electron.

%prep
%autosetup -n %{srcdir} -N
tar --zstd -xf %{SOURCE1}
sed -i '/^      downloadSupportedVersions(),$/d' rollup.config.mjs
sed -i '/"afterPack"/d' electron-builder.json

%build
export PATH=/usr/bin:$PATH
export YARN_ENABLE_TELEMETRY=0
export YARN_ENABLE_NETWORK=0
export YARN_ENABLE_GLOBAL_CACHE=false
export ELECTRON_SKIP_BINARY_DOWNLOAD=1
export PUPPETEER_SKIP_DOWNLOAD=1
export SHARP_SKIP_DOWNLOAD=1
export HUSKY=0
export NODE_ENV=production
export NODE_OPTIONS=--max-old-space-size=8192
yarn() { node .yarn/releases/yarn-4.6.0.cjs "$@"; }
yarn install --immutable --immutable-cache --mode=skip-build
yarn build
mkdir eldist
touch eldist/electron
yarn electron-builder --linux dir --publish never \
  -c.electronDist=eldist -c.npmRebuild=false -c.asar=false

%install
install -d %{buildroot}%{appdir}
cp -a dist/linux-arm64-unpacked/resources/app/. %{buildroot}%{appdir}/
find %{buildroot}%{appdir} -name '*.map' -delete
find %{buildroot}%{appdir} -path '*/prebuilds/*' ! -path '*/linux-arm64/*' -type f -delete
find %{buildroot}%{appdir} -type d -empty -delete

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'SH'
#!/bin/sh
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
  export ELECTRON_OZONE_PLATFORM_HINT=wayland
fi
case " $* " in
  *" --password-store"*) ;;
  *) set -- --password-store=gnome-libsecret "$@" ;;
esac
exec /usr/bin/electron %{appdir} "$@"
SH
chmod 755 %{buildroot}%{_bindir}/%{name}

for i in 16 32 48 64 128 256 512; do
  install -Dm644 build/icons/${i}x${i}.png %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/%{name}.png
done

cat > %{name}.desktop <<'DESKTOP'
[Desktop Entry]
Name=Rocket.Chat
Comment=Official Rocket.Chat desktop client
Exec=rocketchat-desktop %U
Icon=rocketchat-desktop
Terminal=false
Type=Application
StartupWMClass=rocket-chat
MimeType=x-scheme-handler/rocketchat;
Categories=Network;InstantMessaging;Chat;
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
%{_datadir}/icons/hicolor/*/apps/%{name}.png

%changelog
* Sun Oct 18 2026 lacamar <lchlnm@pm.me> - 4.18.3-3
- Fix StartupWMClass

* Sun Oct 18 2026 lacamar <lchlnm@pm.me> - 4.18.3-2
- Rebuild on system electron, offline yarn cache
