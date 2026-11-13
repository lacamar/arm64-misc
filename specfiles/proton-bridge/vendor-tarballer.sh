#!/usr/bin/env bash
set -euo pipefail
version=$(rpmspec -q --srpm --qf '%{version}' "$1")
out=$2/proton-bridge-$version.tar.gz
[[ -e $out ]] && exit 0
work=${XDG_CACHE_HOME:-$HOME/.cache}/mx-rpm-tarballer/proton-bridge
rm -rf "$work"; mkdir -p "$work/proton-bridge-$version"
git -c advice.detachedHead=false clone -q --depth 1 --branch "v$version" https://github.com/ProtonMail/proton-bridge.git "$work/git"
git -C "$work/git" archive HEAD | tar -x -C "$work/proton-bridge-$version"
(cd "$work/proton-bridge-$version" && go mod vendor)
tar -C "$work" -czf "$out" "proton-bridge-$version"
rm -rf "$work"
