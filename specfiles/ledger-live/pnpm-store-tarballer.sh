#!/usr/bin/env bash
set -euo pipefail
version=$(rpmspec -q --srpm --qf "%{version}" "$1")
pnpm_version=$(awk '$1=="%global" && $2=="pnpm_version" {print $3}' "$1")
src=$2
work=${XDG_CACHE_HOME:-$HOME/.cache}/mx-rpm-tarballer/ledger-live
rm -rf "$work"; mkdir -p "$work"; cd "$work"
tar xzf "$src/pnpm-$pnpm_version.tgz"
tar xzf "$src/ledger-live-$version.tar.gz"
cd "ledger-live--ledgerhq-live-desktop-$version"
node -e 'const p=require("./package.json");if(!p.pnpm?.supportedArchitectures)process.exit();delete p.pnpm.supportedArchitectures;require("fs").writeFileSync("package.json",JSON.stringify(p,null,2)+"\n")'
sed -i "s/\"packageManager\": \"pnpm@[^\"]*\"/\"packageManager\": \"pnpm@$pnpm_version\"/" package.json
sed -i "/^minimumReleaseAge:/d" pnpm-workspace.yaml
printf "minimumReleaseAge: 0\nfetchTimeout: 600000\nfetchRetries: 5\n" >> pnpm-workspace.yaml
sed -i "s/^        version: 1.20.0(debug@4.4.3)$/        version: 1.21.1(debug@4.4.3)/" pnpm-lock.yaml
export npm_config_manage_package_manager_versions=false
node "$work/package/bin/pnpm.mjs" install --filter="ledger-live-desktop..." --filter="@ledgerhq/ledger-live" --frozen-lockfile --ignore-scripts --store-dir "$work/pnpm-store"
tar -C "$work" -cf - pnpm-store | zstd -T0 -10 -f -o "$src/ledger-live-$version-pnpm-store.tar.zst"
