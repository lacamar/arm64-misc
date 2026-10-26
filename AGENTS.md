# arm64-misc

- Specs: `specfiles/<pkg>/`, symlinked from `~/.local/rpm/specs`; sources in `~/.local/rpm/sources/<pkg>`
- Autobuild: `~/.local/rpm/specs/autobuild`, run by user unit `autobuild-everything.service`
- Build logs: `~/.local/rpm/rpms/.logs/<pkg>/`
- Release: COPR `lacamar/arm64-misc`, tags `<specstem>-<version>-<release>` (`mx-rpm --tag`, enabled via `git config mxrpm.tag true`); see `bd memories release-conventions`
- Pre-commit: `tools/check-specs` requires a new `%changelog` entry with `- ` bullets
