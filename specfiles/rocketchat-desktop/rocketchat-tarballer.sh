#!/usr/bin/env bash
set -euo pipefail
version=$1
src=$HOME/.local/rpm/sources/rocketchat-desktop
work=${XDG_CACHE_HOME:-$HOME/.cache}/mx-rpm-tarballer/rocketchat-desktop
rm -rf "$work"; mkdir -p "$work"; cd "$work"
tar xzf "$src/rocketchat-desktop-$version.tar.gz"
cd "Rocket.Chat.Electron-$version"
export YARN_ENABLE_TELEMETRY=0 YARN_ENABLE_GLOBAL_CACHE=false
node .yarn/releases/yarn-*.cjs install --immutable --mode=skip-build
tar -cf - .yarn/cache | zstd -T0 -10 -o "$src/rocketchat-desktop-$version-yarn-cache.tar.zst" -f
