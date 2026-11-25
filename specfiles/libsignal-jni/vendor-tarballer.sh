#!/usr/bin/env bash
set -euo pipefail
parsed=$(rpmspec -P "$1")
src0=$(awk '/^Source0?:/{print $2; exit}' <<<"$parsed")
vendor=$(awk '/^Source[0-9]*:.*-vendor\.tar\.zst$/{print $2; exit}' <<<"$parsed")
out=$2/$(basename "$vendor")
[[ -e $out ]] && exit 0
top=$(basename "$vendor" .tar.zst)
work=$(mktemp -d); trap 'rm -rf "$work"' EXIT
mkdir -p "$work/src" "$work/$top"
curl -fsSL --retry 5 "$src0" | tar -xz -C "$work/src" --strip-components=1
(cd "$work/src" && /usr/bin/cargo vendor --locked "$work/$top/vendor" >"$work/$top/vendor-config.toml")
tar -C "$work" --zstd -cf "$out" "$top"
