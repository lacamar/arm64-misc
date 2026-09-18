%global bumpver 1
%global _name shadps4
%global tag 0.18.0
%global commit 2e4b770898a292daa72102a4162d0441eec028f3
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}
# Prebuilt FFmpeg from shadps4-emu/ext-ffmpeg-core, matching externals/ffmpeg-core
%global ffmpeg_sha 94dde08

%global toolchain clang
%global _lto_cflags %{nil}

Name:           %{_name}-git
Version:        %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:        1%{?dist}
Summary:        PlayStation 4 emulator (native aarch64 port using box64 dynarec)
License:        GPL-2.0-or-later
URL:            https://github.com/lacamar/shadps4
# Full tarball with submodules: scripts/make-source-tarball.sh in the repo
Source0:        https://github.com/lacamar/%{_name}/releases/download/aarch64-%{shortcommit}/%{_name}-%{shortcommit}-full.tar.zst
Source1:        https://github.com/shadps4-emu/ext-ffmpeg-core/releases/download/%{ffmpeg_sha}/ffmpeg-linux-arm64.zip
Source2:        https://github.com/shadps4-emu/ext-ffmpeg-core/releases/download/%{ffmpeg_sha}/ffmpeg-linux-x64.zip

Conflicts:      %{_name}
Provides:       %{_name} = %{version}-%{release}
ExclusiveArch:  aarch64 x86_64

BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  clang
BuildRequires:  lld
BuildRequires:  gcc-c++
BuildRequires:  git-core
BuildRequires:  python3
BuildRequires:  pkgconfig
BuildRequires:  zstd
BuildRequires:  desktop-file-utils
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
BuildRequires:  libusb1-devel
BuildRequires:  systemd-devel
BuildRequires:  libuuid-devel

Requires:       vulkan-loader
Recommends:     mesa-vulkan-drivers

%description
shadPS4 is an early PlayStation 4 emulator. This build adds native Linux
aarch64 support: guest x86-64 code runs through an embedded box64 dynarec
instead of requiring an x86-64 host.

%prep
%autosetup -p1 -n %{_name}-%{shortcommit}
# ffmpeg-core wants the prebuilt archive at a git-derived path; feed it offline.
sed -i '/^execute_process(/,/OUTPUT_STRIP_TRAILING_WHITESPACE)/c set(FFMPEG_GIT_SHA %{ffmpeg_sha})' \
  externals/ffmpeg-core/CMakeLists.txt
mkdir -p %{__cmake_builddir}/externals
%ifarch aarch64
cp %{SOURCE1} %{__cmake_builddir}/externals/ffmpeg-%{ffmpeg_sha}.zip
%else
cp %{SOURCE2} %{__cmake_builddir}/externals/ffmpeg-%{ffmpeg_sha}.zip
%endif

%build
%cmake -G Ninja \
  -DCMAKE_BUILD_TYPE=RelWithDebInfo \
  -DENABLE_UPDATER=OFF \
  -DENABLE_DISCORD_RPC=ON
%cmake_build

%install
install -Dpm0755 %{__cmake_builddir}/%{_name} %{buildroot}%{_bindir}/%{_name}
install -Dpm0644 src/dist/net.shadps4.shadPS4.desktop \
  %{buildroot}%{_datadir}/applications/net.shadps4.shadPS4.desktop
install -Dpm0644 src/resources/%{_name}.png \
  %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/net.shadps4.shadPS4.png
desktop-file-validate %{buildroot}%{_datadir}/applications/net.shadps4.shadPS4.desktop

%files
%license LICENSE
%doc README.md
%{_bindir}/%{_name}
%{_datadir}/applications/net.shadps4.shadPS4.desktop
%{_datadir}/icons/hicolor/512x512/apps/net.shadps4.shadPS4.png

%changelog
* Fri Sep 18 2026 lm <lchlnm@pm.me> - 0.18.0^1.git.e83f729-1
- Initial package
- Native aarch64 port via box64 dynarec
