#!/usr/bin/env bash
set -euo pipefail
version=$1
src=$HOME/.local/rpm/sources/ledger-live
work=${XDG_CACHE_HOME:-$HOME/.cache}/mx-rpm-tarballer/ledger-live
rm -rf "$work"; mkdir -p "$work"; cd "$work"
tar xzf "$src/ledger-live-$version.tar.gz"
cd "ledger-live--ledgerhq-live-desktop-$version"
node -e 'const p=require("./package.json");delete p.pnpm.supportedArchitectures;require("fs").writeFileSync("package.json",JSON.stringify(p,null,2)+"\n")'
export npm_config_manage_package_manager_versions=false
pnpm install --filter="ledger-live-desktop..." --filter="@ledgerhq/ledger-live" --frozen-lockfile --ignore-scripts --store-dir "$work/pnpm-store"
tar -C "$work" -cf - pnpm-store | zstd -T0 -10 -o "$src/ledger-live-$version-pnpm-store.tar.zst"
