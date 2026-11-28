#!/usr/bin/bash
set -eu
watchdog=$(realpath "$1")
work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir "$work/bin"
printf '#!/usr/bin/bash\necho "$*" >>"%s/calls"\n[[ $2 != show ]] || echo 1\n' "$work" >"$work/bin/systemctl"
printf '#!/bin/sh\nexit 1\n' >"$work/bin/gdbus"
for fake in sleep dbus-monitor notify-send; do
  printf '#!/bin/sh\n' >"$work/bin/$fake"
done
chmod +x "$work/bin"/*

run() {
  printf 'some avg10=%s avg60=0 avg300=0 total=0\nfull avg10=%s avg60=0 avg300=0 total=0\n' "$1" "$1" >"$work/psi"
  : >"$work/calls"
  PATH="$work/bin:$PATH" PSI_MEMORY="$work/psi" bash "$watchdog"
}

run 95.39 | grep -q 'hung under 95% memory stall; not restarting'
if grep -q -e kill -e restart "$work/calls"; then
  exit 1
fi

run 0.10 | grep -q 'hung; dumping core and restarting'
grep -q 'kill -s ABRT xdg-desktop-portal' "$work/calls"
grep -q 'restart xdg-desktop-portal' "$work/calls"
