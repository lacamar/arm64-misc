#!/usr/bin/env bash
set -euo pipefail
version=$(rpmspec -q --srpm --qf '%{version}' "$1")
pnpm_version=$(awk '$1=="%global" && $2=="pnpm_version" {print $3}' "$1")
ec_commit=$(awk '$1=="%global" && $2=="ec_commit" {print $3}' "$1")
src=$2
work=${XDG_CACHE_HOME:-$HOME/.cache}/mx-rpm-tarballer/element-desktop
export npm_config_manage_package_manager_versions=false
rm -rf "$work"; mkdir -p "$work"; cd "$work"
tar xzf "$src/pnpm-$pnpm_version.tgz"
tar xzf "$src/element-desktop-$version.tar.gz"
tar xzf "$src/element-call-$ec_commit.tar.gz"
pnpm=(node "$work/package/bin/pnpm.mjs")
(cd "element-web-$version" && "${pnpm[@]}" install --frozen-lockfile --ignore-scripts --store-dir "$work/pnpm-store")
(cd "element-call-$ec_commit" && "${pnpm[@]}" install --frozen-lockfile --ignore-scripts --store-dir "$work/pnpm-store")
tar -C "$work" -cf - pnpm-store | zstd -T0 -10 -o "$src/element-desktop-$version-pnpm-store.tar.zst" -f
