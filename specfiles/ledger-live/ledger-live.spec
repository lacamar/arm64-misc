%global debug_package %{nil}
%global srcdir ledger-live--ledgerhq-live-desktop-%{version}
%global appdir %{_libexecdir}/%{name}
%global pnpm_version 11.23.0

Name:           ledger-live
Version:        4.29.0
Release:        2%{?dist}
Summary:        Ledger Wallet desktop app

License:        MIT
URL:            https://github.com/LedgerHQ/ledger-live
Source0:        https://github.com/LedgerHQ/ledger-live/archive/refs/tags/@ledgerhq/live-desktop@%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-pnpm-store.tar.zst
Source2:        pnpm-store-tarballer.sh
Source3:        20-hw1.rules
Source4:        https://registry.npmjs.org/pnpm/-/pnpm-%{pnpm_version}.tgz

ExclusiveArch:  aarch64

BuildRequires:  nodejs24
BuildRequires:  zstd
BuildRequires:  desktop-file-utils
BuildRequires:  systemd-rpm-macros

Requires:       electron

%description
Desktop companion app for Ledger hardware wallets.

%prep
%autosetup -n %{srcdir} -N -a 1
node -e 'const p=require("./package.json");if(!p.pnpm?.supportedArchitectures)process.exit();delete p.pnpm.supportedArchitectures;require("fs").writeFileSync("package.json",JSON.stringify(p,null,2)+"\n")'
sed -i 's/"packageManager": "pnpm@[^"]*"/"packageManager": "pnpm@%{pnpm_version}"/' package.json
sed -i '/^minimumReleaseAge:/d' pnpm-workspace.yaml
echo "minimumReleaseAge: 0" >> pnpm-workspace.yaml
sed -i "s/^        version: 1.20.0(debug@4.4.3)$/        version: 1.21.1(debug@4.4.3)/" pnpm-lock.yaml
tar xzf %{SOURCE4}
echo '[]' > apps/ledger-live-desktop/release-notes.json

%build
export npm_config_manage_package_manager_versions=false
export ELECTRON_SKIP_BINARY_DOWNLOAD=1
export NX_DAEMON=false
export NX_NO_CLOUD=true
export NODE_ENV=production
export NODE_OPTIONS=--max-old-space-size=8192
mkdir -p bin
printf '#!/bin/sh\nexec node %s/package/bin/pnpm.mjs "$@"\n' "$PWD" > bin/pnpm
chmod 755 bin/pnpm
export PATH=$PWD/bin:$PATH
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
zcash=$(readlink -f node_modules/@ledgerhq/zcash-utils)
cp $zcash/{package.json,index.js} $zcash/../zcash-utils-linux-arm64-gnu/index.linux-arm64-gnu.node %{buildroot}%{appdir}/node_modules/@ledgerhq/zcash-utils/

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
  install -Dm644 build/icons/${i}x${i}.png %{buildroot}%{_datadir}/icons/hicolor/${i}x${i}/apps/%{name}.png
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
StartupWMClass=ledger-wallet
MimeType=x-scheme-handler/ledgerlive;x-scheme-handler/ledgerwallet;
Categories=Finance;
DESKTOP
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{name}.desktop
install -Dm644 %{SOURCE3} %{buildroot}%{_udevrulesdir}/20-hw1.rules

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

%files
%license apps/ledger-live-desktop/LICENSE
%doc apps/ledger-live-desktop/README.md
%{_bindir}/%{name}
%{appdir}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/*/apps/%{name}.png
%{_udevrulesdir}/20-hw1.rules

%changelog
* Fri Nov 27 2026 Lachlan Marie <lchlnm@pm.me> - 4.29.0-2
- Fix stale axios catalog pin in lockfile

* Fri Nov 20 2026 Lachlan Marie <lchlnm@pm.me> - 4.29.0-1
- Update to 4.29.0

* Fri Nov 20 2026 lacamar <lchlnm@pm.me> - 4.10.1-3
- Bundle pnpm 11.23.0
- Follow 4.29 icon names, zcash-utils layout

* Fri Nov 20 2026 lacamar <lchlnm@pm.me> - 4.10.1-2
- Fix tarballer args (spec, source dir)

* Sun Oct 18 2026 lacamar <lchlnm@pm.me> - 4.10.1-1
- Initial package
