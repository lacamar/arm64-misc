#!/bin/bash
# cargokit needs rustup; delegate `run` to system cargo, no-op the rest
case "$1" in
  run) shift 2; exec "$@" ;;
  target) [ "$2" = list ] && echo aarch64-unknown-linux-gnu ;;
esac
exit 0
