%global debug_package %{nil}
%global srcdir ledger-live--ledgerhq-live-desktop-%{version}
%global appdir %{_libexecdir}/%{name}

Name:           ledger-live
Version:        4.10.1
Release:        1%{?dist}
Summary:        Ledger Wallet desktop app

License:        MIT
URL:            https://github.com/LedgerHQ/ledger-live
Source0:        https://github.com/LedgerHQ/ledger-live/archive/refs/tags/@ledgerhq/live-desktop@%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-pnpm-store.tar.zst
Source2:        pnpm-store-tarballer.sh

ExclusiveArch:  aarch64

BuildRequires:  nodejs24
BuildRequires:  pnpm
BuildRequires:  zstd
BuildRequires:  desktop-file-utils

Requires:       electron

%description
Desktop companion app for Ledger hardware wallets.

%prep
%autosetup -n %{srcdir} -N -a 1
node -e 'const p=require("./package.json");delete p.pnpm.supportedArchitectures;require("fs").writeFileSync("package.json",JSON.stringify(p,null,2)+"\n")'
echo '[]' > apps/ledger-live-desktop/release-notes.json

%build
export npm_config_manage_package_manager_versions=false
export ELECTRON_SKIP_BINARY_DOWNLOAD=1
export NX_DAEMON=false
export NX_NO_CLOUD=true
export NODE_ENV=production
export NODE_OPTIONS=--max-old-space-size=8192
pnpm install --offline --frozen-lockfile --ignore-scripts --store-dir "$PWD/pnpm-store" --filter="ledger-live-desktop..." --filter="@ledgerhq/ledger-live"
pnpm run nx:write-cache-config
pnpm exec nx run @ledgerhq/icons-ui:build
cp -a libs/ui/packages/icons/{react,native,reactLegacy,nativeLegacy} "$(readlink -f libs/ui/packages/react/node_modules/@ledgerhq/icons-ui)/"
pnpm exec nx run ledger-live-desktop:build-lib-deps
pnpm desktop build:js

%install
cd apps/ledger-live-desktop
install -d %{buildroot}%{appdir}/node_modules/@ledgerhq/zcash-utils
cp -r .webpack package.json %{buildroot}%{appdir}/
find %{buildroot}%{appdir}/.webpack -name '*.map' -delete
cp -L node_modules/@ledgerhq/zcash-utils/{package.json,index.js,index.linux-arm64-gnu.node} %{buildroot}%{appdir}/node_modules/@ledgerhq/zcash-utils/

install -d %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'SH'
#!/bin/sh
if [ "$XDG_SESSION_TYPE" = "wayland" ] || [ -n "$WAYLAND_DISPLAY" ]; then
  export ELECTRON_OZONE_PLATFORM_HINT=wayland
fi
exec /usr/bin/electron %{appdir} "$@"
SH
chmod 755 %{buildroot}%{_bindir}/%{name}

for i in 128 256 512 1024; do
  install -Dm644 build/icons/icon@${i}x${i}.png %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/%{name}.png
done

install -d %{buildroot}%{_datadir}/applications
cat > %{name}.desktop <<'DESKTOP'
[Desktop Entry]
Name=Ledger Wallet
Comment=Ledger Wallet - Desktop
Exec=ledger-live %U
Icon=ledger-live
Terminal=false
Type=Application
StartupWMClass=Ledger Wallet
MimeType=x-scheme-handler/ledgerlive;x-scheme-handler/ledgerwallet;
Categories=Finance;
DESKTOP
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{name}.desktop

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

%files
%license apps/ledger-live-desktop/LICENSE
%doc apps/ledger-live-desktop/README.md
%{_bindir}/%{name}
%{appdir}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png

%changelog
* Sun Oct 18 2026 lacamar <lchlnm@pm.me> - 4.10.1-1
- Initial package
