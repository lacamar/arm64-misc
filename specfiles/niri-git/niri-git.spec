%bcond_without check

%global cargo_install_lib 0

# We want panic backtraces to work without installing the debuginfo package,
# so we leave the debuginfo in the main binary.
%global debug_package %{nil}
%global __strip /bin/true

# To reduce the file size, do some convincing of rust-srpm-macros
# to leave alone the chosen debug settings from Cargo.toml.
%global rustflags_debuginfo please-remove-me
%global build_rustflags %{shrink:
  -Copt-level=%rustflags_opt_level
  -Ccodegen-units=%rustflags_codegen_units
  -Cstrip=none
  %{expr:0%{?_include_frame_pointers} ? "-Cforce-frame-pointers=yes" : ""}
  -Clink-arg=-Wl,-z,relro
  -Clink-arg=-Wl,-z,now
  %[0%{?_package_note_status} ? "-Clink-arg=%_package_note_flags" : ""]
  --cap-lints=warn
}

# Convince rust-srpm-macros to use Cargo.lock with the Smithay commit.
%global __cargo_common_opts %{?_smp_mflags} -Z avoid-dev-deps --locked

%global bumpver 8
%global tag 26.04
%global commit ed22699d99462f61ab171472d3ea67e844ea580d
%global shortcommit %{sub %{commit} 1 8}
%global smithay_commit 79bbed5e1199090d787115614847a79c76607181

Name:           niri
Version:        %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:        6%{?dist}
Summary:        Scrollable-tiling Wayland compositor

SourceLicense:  GPL-3.0-or-later

License:        ((MIT OR Apache-2.0) AND BSD-3-Clause) AND ((MIT OR Apache-2.0) AND Unicode-3.0) AND (0BSD OR MIT OR Apache-2.0) AND Apache-2.0 AND (Apache-2.0 AND MIT) AND (Apache-2.0 OR MIT) AND (Apache-2.0 OR MIT OR Unlicense) AND (Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT) AND BSD-2-Clause AND (BSD-2-Clause OR Apache-2.0 OR MIT) AND (BSD-3-Clause OR MIT OR Apache-2.0) AND GPL-3.0-or-later AND ISC AND MIT AND (MIT OR Apache-2.0) AND (MIT OR Apache-2.0 OR LGPL-2.1-or-later) AND (MIT OR Apache-2.0 OR Zlib) AND (MIT OR Zlib OR Apache-2.0) AND MPL-2.0 AND (Unlicense OR MIT) AND Zlib AND (Zlib OR Apache-2.0 OR MIT)
# LICENSE.dependencies contains a full license breakdown

URL:            https://github.com/niri-wm/niri
VCS:            git+%{url}#%{commit}:
Source:         %{url}/archive/%{commit}/niri-%{shortcommit}.tar.gz
Source1:        https://github.com/Smithay/smithay/archive/%{smithay_commit}/smithay-%{sub %{smithay_commit} 1 8}.tar.gz
Patch:          niri-argb2101010.patch
Patch:          niri-ctm-gamma.patch
# https://github.com/niri-wm/niri/pull/4485
Patch:          niri-pr4485.patch
# https://github.com/niri-wm/niri/pull/4365
Patch:          niri-pr4365.patch
# https://github.com/niri-wm/niri/pull/4295
Patch:          niri-pr4295.patch
# https://github.com/niri-wm/niri/pull/4574
Patch:          niri-pr4574.patch
# https://github.com/niri-wm/niri/pull/4330
Patch:          niri-pr4330.patch
# https://github.com/niri-wm/niri/pull/4392
Patch:          niri-pr4392.patch
Patch:          niri-scratchpad.patch
Patch:          niri-session-management.patch
# https://github.com/niri-wm/niri/pull/3956
Patch:          niri-pr3956.patch
Patch:          niri-wp-protocols.patch
# https://github.com/niri-wm/niri/pull/4118
Patch:          niri-pr4118.patch
# https://github.com/niri-wm/niri/pull/4001
Patch:          niri-pr4001.patch
Patch:          niri-smithay-local.patch
Patch:          niri-smithay-overlay-cursor.patch
Patch:          niri-smithay-opaque-overlays.patch

BuildRequires:  cargo-rpm-macros >= 26
BuildRequires:  pkgconfig(udev)
BuildRequires:  pkgconfig(gbm)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  wayland-devel
BuildRequires:  pkgconfig(libinput)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(systemd)
BuildRequires:  pkgconfig(libseat)
BuildRequires:  pkgconfig(libdisplay-info)
BuildRequires:  pipewire-devel
BuildRequires:  pango-devel
BuildRequires:  cairo-gobject-devel
# Needed for pipewire-rs
BuildRequires:  clang
# Needed for some tests with a surfaceless EGL renderer
BuildRequires:  mesa-libEGL

Requires:       mesa-dri-drivers
Requires:       mesa-libEGL

# Loaded through dlopen
Requires:       libwayland-server

# Integrated Xwayland support
Requires:       xwayland-satellite >= 0.7

# Portal implementations used by niri
Recommends:     xdg-desktop-portal-gtk
Recommends:     xdg-desktop-portal-gnome
Recommends:     gnome-keyring

# Suggested utilities, bound in the default config
Recommends:     alacritty
Recommends:     fuzzel
Recommends:     swaylock
Recommends:     waybar
# Suggested utilities
Recommends:     swaybg
Recommends:     mako
Recommends:     swayidle

%description
A scrollable-tiling Wayland compositor.

Windows are arranged in columns on an infinite strip going to the right.
Opening a new window never causes existing windows to resize.

%prep
%setup -q -n niri-%{commit} -a1
mv smithay-%{smithay_commit} smithay
%autopatch -p1

%cargo_prep -N

# We're doing an online build.
sed -i 's/^offline = true$//' .cargo/config.toml

# Final step in leaving alone our debug settings.
sed -i 's/.*please-remove-me$//' .cargo/config.toml

# Set the commit string.
sed -i 's/\[env\]/[env]\nNIRI_BUILD_COMMIT="%{version}"/' .cargo/config.toml

%build
%cargo_build

target/rpm/niri completions bash > ./niri
target/rpm/niri completions fish > ./niri.fish
target/rpm/niri completions zsh > ./_niri

%install
%cargo_install

install -Dm755 -t %{buildroot}%{_bindir} ./resources/niri-session
install -Dm644 -t %{buildroot}%{_datadir}/wayland-sessions ./resources/niri.desktop
install -Dm644 -t %{buildroot}%{_datadir}/xdg-desktop-portal ./resources/niri-portals.conf
install -Dm644 -t %{buildroot}%{_userunitdir} ./resources/niri.service
install -Dm644 -t %{buildroot}%{_userunitdir} ./resources/niri-shutdown.target

install -Dm644 -t %{buildroot}%{bash_completions_dir} ./niri
install -Dm644 -t %{buildroot}%{fish_completions_dir} ./niri.fish
install -Dm644 -t %{buildroot}%{zsh_completions_dir} ./_niri

%if %{with check}
%check
%cargo_test -- --workspace --exclude niri-visual-tests
%endif

%files
%license LICENSE
%doc README.md
%doc resources/default-config.kdl
%doc docs/wiki
%{_bindir}/niri
%{_bindir}/niri-session
%{_datadir}/wayland-sessions/niri.desktop
%dir %{_datadir}/xdg-desktop-portal
%{_datadir}/xdg-desktop-portal/niri-portals.conf
%{_userunitdir}/niri.service
%{_userunitdir}/niri-shutdown.target
%{bash_completions_dir}/niri
%{fish_completions_dir}/niri.fish
%{zsh_completions_dir}/_niri

%changelog
* Wed Oct 07 2026 Lachlan Marie <lchlnm@pm.me> - 26.04^8.git.ed22699d-6
 - Opaque-only overlay planes on apple-drm

* Wed Oct 07 2026 Lachlan Marie <lchlnm@pm.me> - 26.04^8.git.ed22699d-5
 - Vendor Smithay at pinned rev
 - Overlay-plane hardware cursor on apple-drm

* Tue Oct 06 2026 Lachlan Marie <lchlnm@pm.me> - 26.04^8.git.ed22699d-4
 - Add PR 3956: drm syncobj
 - Add fifo, commit-timing, content-type, alpha-modifier
 - Add PR 4118: xdg-toplevel-tag
 - Add PR 4001: pointer warp

* Mon Oct 05 2026 Lachlan Marie <lchlnm@pm.me> - 26.04^8.git.ed22699d-3
 - Add xdg/xx-session-management-v1

* Sat Oct 03 2026 Lachlan Marie <lchlnm@pm.me> - 26.04^8.git.ed22699d-2
 - Add scratchpad actions

* Fri Oct 02 2026 Lachlan Marie <lchlnm@pm.me> - 26.04^8.git.ed22699d-1
 - Update to commit ed22699d99462f61ab171472d3ea67e844ea580d
 - Add NIRI_CTM_GAMMA knob
 - Add PR 4485: layer surface cleanup on output removal
 - Add PR 4365: precise solid color rounding
 - Add PR 4295: snap working area to output edges
 - Add PR 4574: ext-image-copy cursor session fix
 - Add PR 4330: refresh windows only after commit
 - Add PR 4392: force-render window rule

* Thu Oct 01 2026 Lachlan Marie <lchlnm@pm.me> - 26.04^7.git.c7616326-1
 - Update to commit c7616326a60d00cafba8c5e0c92bc7a02c8c10f2
 - Drop CTM night light patch (upstreamed)

* Sat Sep 26 2026 Lachlan Marie <lchlnm@pm.me> - 26.04^6.git.1f03391e-2
 - Update to commit 1f03391ea644c2a43597de7f637269e26d1e1b49

* Wed Sep 23 2026 Lachlan Marie <lchlnm@pm.me> - 26.04^5.git.5f4469b6-2
 - Update to commit 5f4469b6a992492cf7221b269e9379f42e737649

* Tue Sep 22 2026 Lachlan Marie <lchlnm@pm.me> - 26.04^4.git.9a35d377-2
 - Update to commit 9a35d3774a7ff1acdce07fde05bdc94dfa5a0258

* Mon Sep 21 2026 Lachlan Marie <lchlnm@pm.me> - 26.04^3.git.8be4c6df-2
 - Add Argb2101010 output format

* Mon Sep 21 2026 Lachlan Marie <lchlnm@pm.me> - 26.04^3.git.8be4c6df-1
 - Update to commit 8be4c6df68ddef2afd4ccdde7f27dbc782c30603

* Sun Sep 20 2026 Lachlan Marie <lchlnm@pm.me> - 26.04^2.git.7256ccf6-1
 - Update to commit 7256ccf6274a1f953c6987ade34ea1c0e4944c27

* Fri Sep 18 2026 lm <lchlnm@pm.me> - 26.04^1.git.ee8a04bb-1
- Drop display-only scanout patch
- Switch to tag/bumpver versioning

* Fri Sep 18 2026 lm <lchlnm@pm.me> - 0.0.git.2911.ee8a04bb-4
- Allow direct scanout on display-only devices

* Fri Sep 18 2026 lm <lchlnm@pm.me> - 0.0.git.2911.ee8a04bb-3
- Add NIRI_CTM_GAMMA knob

* Fri Sep 18 2026 lm <lchlnm@pm.me> - 0.0.git.2911.ee8a04bb-2
- Add CTM gamma fallback for night light
