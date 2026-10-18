%global debug_package %{nil}
%global __requires_exclude_from ^%{_libexecdir}/%{name}/.*$
%global __provides_exclude_from ^%{_libexecdir}/%{name}/.*$
%global appdir %{_libexecdir}/%{name}
%global pnpm_version 11.23.0
%global ec_commit 9b3c3569ecefbb79cf527ea24e3756ba50553a8f

Name:           element-desktop
Version:        1.12.32
Release:        1%{?dist}
Summary:        Matrix collaboration client

License:        AGPL-3.0-only OR GPL-3.0-only
URL:            https://github.com/element-hq/element-web
Source0:        https://github.com/element-hq/element-web/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
Source1:        %{name}-%{version}-pnpm-store.tar.zst
Source2:        https://registry.npmjs.org/pnpm/-/pnpm-%{pnpm_version}.tgz
Source3:        https://codeload.github.com/element-hq/element-call/tar.gz/%{ec_commit}#/element-call-%{ec_commit}.tar.gz
Source4:        pnpm-store-tarballer.sh
Source5:        collect-prod-deps.mjs

ExclusiveArch:  aarch64

BuildRequires:  nodejs24
BuildRequires:  zstd
BuildRequires:  desktop-file-utils

Requires:       electron

%description
Element desktop app for the Matrix network, running on the system Electron.

%prep
%autosetup -n element-web-%{version} -N -a 3
tar xf %{SOURCE1}
tar xzf %{SOURCE2}
sed -i 's/"packageManager": "pnpm@[^"]*"/"packageManager": "pnpm@%{pnpm_version}"/' element-call-%{ec_commit}/package.json
for d in . element-call-%{ec_commit}; do echo "minimumReleaseAge: 0" >> $d/pnpm-workspace.yaml; done

%build
export npm_config_manage_package_manager_versions=false
export ELECTRON_SKIP_BINARY_DOWNLOAD=1
export NX_DAEMON=false
export NX_NO_CLOUD=true
export NODE_OPTIONS=--max-old-space-size=8192
mkdir -p bin
printf '#!/bin/sh\nexec node %s/package/bin/pnpm.mjs "$@"\n' "$PWD" > bin/pnpm
chmod 755 bin/pnpm
export PATH=$PWD/bin:$PATH
store="--store-dir $PWD/pnpm-store"

pnpm install --offline --frozen-lockfile --ignore-scripts $store

pushd element-call-%{ec_commit}
pnpm install --offline --frozen-lockfile --ignore-scripts $store
ln -sfn "$(readlink -f ../node_modules/.pnpm/matrix-js-sdk@*/node_modules/matrix-js-sdk)" node_modules/matrix-js-sdk
pnpm run build:component:js
popd
cp -a element-call-%{ec_commit}/component/dist node_modules/.pnpm/@element-hq+element-call-component@*/node_modules/@element-hq/element-call-component/

pnpm exec nx run element-web:build
pnpm exec nx run-many -p element-desktop -t build:ts build:res
node %{SOURCE5} "$PWD/apps/desktop" pkcs11js graphene-pk11 > prod-entries

%install
install -d %{buildroot}%{appdir}/build %{buildroot}%{appdir}/node_modules/.pnpm
cp -a apps/desktop/lib %{buildroot}%{appdir}/
while read -r e; do cp -a node_modules/.pnpm/$e %{buildroot}%{appdir}/node_modules/.pnpm/; done < prod-entries
for n in $(node -p 'Object.keys(require("./apps/desktop/package.json").dependencies).join(" ")'); do
  r=$(readlink -f apps/desktop/node_modules/$n)
  mkdir -p $(dirname %{buildroot}%{appdir}/node_modules/$n)
  ln -sr %{buildroot}%{appdir}/node_modules/${r#$PWD/node_modules/} %{buildroot}%{appdir}/node_modules/$n
done
cp -a apps/web/webapp %{buildroot}%{appdir}/webapp
find %{buildroot}%{appdir}/webapp -name '*.map' -delete
install -m644 apps/desktop/element.io/release/config.json %{buildroot}%{appdir}/webapp/config.json
install -m644 apps/desktop/build/icon.png %{buildroot}%{appdir}/build/icon.png
node -e '
const [pkg, out] = process.argv.slice(1);
const p = require(pkg);
const v = require(process.cwd() + "/apps/desktop/element.io/release/build.json");
Object.assign(p, {name: v.name, productName: v.productName, description: v.description,
  desktopName: v.name + ".desktop", electron_appId: v.appId, electron_protocol: v.protocols[0]});
delete p.devDependencies; delete p.scripts; delete p.optionalDependencies;
require("fs").writeFileSync(out, JSON.stringify(p, null, 2) + "\n");
' "$PWD/apps/desktop/package.json" %{buildroot}%{appdir}/package.json

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

install -Dm644 apps/desktop/build/icon.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/%{name}.png

cat > %{name}.desktop <<'DESKTOP'
[Desktop Entry]
Name=Element
Comment=Secure collaboration and messaging
Exec=element-desktop %U
Icon=element-desktop
Terminal=false
Type=Application
StartupWMClass=element-desktop
MimeType=x-scheme-handler/element;x-scheme-handler/io.element.desktop;
Categories=Network;InstantMessaging;Chat;
DESKTOP
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{name}.desktop

%check
desktop-file-validate %{buildroot}%{_datadir}/applications/%{name}.desktop

%files
%license LICENSE-AGPL-3.0 LICENSE-GPL-3.0
%doc apps/desktop/README.md
%{_bindir}/%{name}
%{appdir}
%{_datadir}/applications/%{name}.desktop
%{_datadir}/icons/hicolor/512x512/apps/%{name}.png

%changelog
* Sun Oct 18 2026 lacamar <lchlnm@pm.me> - 1.12.32-1
- Initial package
