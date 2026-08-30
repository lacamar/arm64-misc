#!/bin/bash
# Minimal stand-in for `rustup`, for building with Fedora's system Rust
# instead of a rustup-managed toolchain. cargokit (used by
# flutter_rust_bridge) hard-requires the `rustup` binary to exist on PATH:
# it uses `rustup toolchain`/`target` subcommands to check whether the
# rust-toolchain.toml-pinned version and target are already installed
# (installing them via a real rustup otherwise), then always builds by
# running the actual compiler through `rustup run <toolchain> cargo ...`
# rather than calling `cargo` on PATH directly. As long as the system
# cargo/rustc already are the exact version cargokit wants (checked by the
# caller before relying on this), the toolchain/target bookkeeping
# subcommands can just report "already installed" and no-op instead of
# really installing a second, redundant toolchain -- but `run` has to
# really delegate to the real system cargo, since that's the only place
# actual compilation happens.
set -euo pipefail

case "$1" in
  run)
    # `rustup run <toolchain> <cmd> [args...]` -- this is how cargokit
    # actually invokes cargo (not by calling `cargo` on PATH directly), so
    # unlike every other subcommand here this one must really delegate,
    # not no-op: drop `run <toolchain>` and exec the real command.
    shift 2
    exec "$@"
    ;;
  toolchain)
    case "$2" in
      list) exit 0 ;;
      install) exit 0 ;;
      *) exit 0 ;;
    esac
    ;;
  target)
    case "$2" in
      list) echo "aarch64-unknown-linux-gnu" ;;
      add) exit 0 ;;
      *) exit 0 ;;
    esac
    ;;
  component)
    exit 0
    ;;
  *)
    exit 0
    ;;
esac
