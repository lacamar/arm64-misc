%global bumpver 1
%global _name shadps4-qtlauncher
%global tag 2026.09.12
%global commit 4ce2f029c824fe3cb9dac80673b406baa6d22617
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

%global _lto_cflags %{nil}

Name:           %{_name}-git
Version:        %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:        1%{?dist}
Summary:        Qt launcher and game library front-end for shadPS4
License:        GPL-2.0-or-later
URL:            https://github.com/shadps4-emu/shadps4-qtlauncher
Source0:        https://github.com/shadps4-emu/%{_name}/archive/%{commit}/%{_name}-%{shortcommit}.tar.gz
# Seed the version manager with the distro emulator binary
Patch0:         0001-seed-system-emulator-version.patch

%{lua:
local externals = {
 { name="ext-fmt", ref="64db979", owner="shadps4-emu", path="fmt", version="12.0.0", license="MIT" },
 { name="json", ref="54be9b0", owner="nlohmann", path="json", version="3.12", license="MIT" },
 { name="openal-soft", ref="f120be6", owner="shadexternals", path="openal-soft", version="1.24.3", license="LGPL-2.0-or-later" },
 { name="sdl3", ref="d5af35e3fbb5bb6555ed00e69740d52af2a4e877", owner="shadexternals", path="sdl3", version="3.4", license="Zlib" },
 { name="spdlog", ref="b8944a4", owner="gabime", path="spdlog", version="1.15", license="MIT" },
 { name="toml11", ref="a01fe3b", owner="ToruNiina", path="toml11", version="4.4", license="MIT" },
 { name="volk", ref="e51c647", owner="zeux", path="volk", version="1.4", license="MIT" },
 { name="Vulkan-Headers", ref="33d7f51", owner="KhronosGroup", path="vulkan-headers", version="1.4", license="Apache-2.0" },
 { name="ZArchive", ref="965b66c", owner="shadexternals", path="zarchive", version="0.1.2", license="MIT" },
 { name="zstd", ref="5c7b7ba", owner="shadexternals", path="zstd", version="1.5.7", license="BSD-3-Clause" },
}
for i, s in ipairs(externals) do
  si = 100 + i
  print(string.format("Source%d: https://github.com/%s/%s/archive/%s/%s-%s.tar.gz", si, s.owner, s.name, s.ref, s.name, s.ref).."\n")
  print(string.format("Provides: bundled(%s) = %s", s.path, s.version).."\n")
end
function print_setup_externals()
  for i, s in ipairs(externals) do
    si = 100 + i
    print(string.format("rmdir externals/%s || true\n", s.path))
    print(string.format("mkdir -p externals/%s\n", s.path))
    print(string.format("tar -xzf %s --strip-components=1 -C externals/%s\n", rpm.expand("%{SOURCE"..si.."}"), s.path))
  end
end
}

Conflicts:      %{_name}
Provides:       %{_name} = %{version}-%{release}
ExclusiveArch:  aarch64 x86_64

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  gcc-c++
BuildRequires:  git-core
BuildRequires:  pkgconfig
BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  qt6-qttools-devel
BuildRequires:  qt6-qtmultimedia-devel
BuildRequires:  openssl-devel
BuildRequires:  libX11-devel
BuildRequires:  libXext-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libXi-devel
BuildRequires:  libXfixes-devel
BuildRequires:  libXrandr-devel
BuildRequires:  libXScrnSaver-devel
BuildRequires:  libXtst-devel
BuildRequires:  libXinerama-devel
BuildRequires:  libxkbcommon-devel
BuildRequires:  wayland-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  libdecor-devel
BuildRequires:  libdrm-devel
BuildRequires:  mesa-libEGL-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libgbm-devel
BuildRequires:  alsa-lib-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  pipewire-devel
BuildRequires:  dbus-devel
BuildRequires:  systemd-devel

Requires:       shadps4
Requires:       hicolor-icon-theme
Recommends:     qt6-qtwayland
Recommends:     qt6-qtsvg

%description
Game library, settings and version manager front-end for the shadPS4
PlayStation 4 emulator.

%prep
%autosetup -p1 -n %{_name}-%{commit}
%{lua: print_setup_externals()}

%build
%cmake -G Ninja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DENABLE_UPDATER=OFF
%cmake_build

%install
%cmake_install
# Icon is shipped by the emulator package
rm -f %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/net.shadps4.shadPS4.png
desktop-file-validate %{buildroot}%{_datadir}/applications/net.shadps4.shadps4-qtlauncher.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/net.shadps4.shadps4-qtlauncher.metainfo.xml || :

%files
%license LICENSE
%doc README.md
%{_bindir}/shadPS4QtLauncher
%{_datadir}/applications/net.shadps4.shadps4-qtlauncher.desktop
%{_metainfodir}/net.shadps4.shadps4-qtlauncher.metainfo.xml
%{_datadir}/icons/hicolor/scalable/apps/net.shadps4.shadPS4.svg

%changelog
* Fri Sep 18 2026 lm <lchlnm@pm.me> - 2026.09.12^1.git.4ce2f02-1
- Initial package
- Seed system emulator into version manager
