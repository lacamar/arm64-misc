Name:       rocketchat-desktop
Version:    4.13.0
Release:    2%{?dist}
Summary:    Desktop Client for Rocket.Chat

%global electron_version 40.0.0


License:  MIT
URL:      https://github.com/RocketChat/Rocket.Chat.Electron
Source0:  https://github.com/RocketChat/Rocket.Chat.Electron/archive/refs/tags/%{version}.tar.gz
Source1:  Rocket.Chat.Electron-%{version}-yarn-cache.tar.xz
Source2:  https://github.com/electron/electron/releases/download/v%{electron_version}/electron-v%{electron_version}-linux-arm64.zip

ExclusiveArch:  aarch64

BuildRequires:  gcc-c++
BuildRequires:  yarnpkg
BuildRequires:  chromium
BuildRequires:  vips-devel
BuildRequires:  nodejs-devel
BuildRequires:  python3-devel
BuildRequires:  python3dist(setuptools)
BuildRequires:  electron

Requires:       electron


%description
Desktop client for Rocket.Chat.

%prep
%autosetup -n Rocket.Chat.Electron-%{version} -N -a 1
sed -i '/downloadSupportedVersions()/d' rollup.config.mjs
rm -rf node_modules/electron
mkdir -p node_modules/electron
unzip -q %{SOURCE2} -d node_modules/electron/

%build
export NODE_ENV=production
export ELECTRON_OVERRIDE_DIST_PATH=%{_bindir}/electron
export ELECTRON_SKIP_BINARY_DOWNLOAD=1
export PUPPETEER_SKIP_DOWNLOAD=1
export SHARP_SKIP_DOWNLOAD=1
export npm_config_nodedir=/usr/
export npm_config_build_from_source=true

YARN_ENABLE_INLINE_BUILDS=1 yarn install --immutable --immutable-cache --inline-builds
yarn postinstall
yarn build
yarn electron-builder --linux dir

%install
install -d -m 0755 %{buildroot}%{_bindir}

cat << EOF > %{buildroot}%{_bindir}/%{name}
#!/usr/bin/env sh
export NODE_ENV=production

if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
  export ELECTRON_OZONE_PLATFORM_HINT=wayland
else
  export ELECTRON_OZONE_PLATFORM_HINT=x11
fi

exec /usr/bin/electron /usr/libexec/rocketchat-desktop/app.asar "$@"
EOF

chmod +x %{buildroot}%{_bindir}/%{name}

for i in 16 32 48 64 128 256 512; do
    install -d -m 0755 %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/
    install -pm 0644 build/icons/${i}x${i}.png %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/%{name}.png
done

install -d -m 0755 %{buildroot}%{_datadir}/applications/
cat << EOF > %{buildroot}%{_datadir}/applications/%{name}.desktop
[Desktop Entry]
Name=Rocket.Chat
Exec=/usr/bin/rocketchat-desktop %U
Terminal=false
Type=Application
Icon=rocketchat-desktop
StartupWMClass=Rocket.Chat
MimeType=x-scheme-handler/rocketchat;
Comment=Official OSX, Windows, and Linux Desktop Clients for Rocket.Chat
Categories=GNOME;GTK;Network;InstantMessaging;
EOF

chmod +x %{buildroot}%{_datadir}/applications/%{name}.desktop

mkdir -p %{buildroot}%{_libexecdir}/%{name}
cp -pr dist/linux-*unpacked/resources/app.asar* %{buildroot}%{_libexecdir}/%{name}/


%files
%define debug_package %{nil}

%doc README.md
%license LICENSE
%{_bindir}/%{name}

%{_libexecdir}/%{name}

%{_datadir}/icons/hicolor/*/apps/%{name}.*

%{_datadir}/applications/%{name}.desktop


%changelog
%autochangelog
