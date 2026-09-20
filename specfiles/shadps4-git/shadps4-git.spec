%global bumpver 0
%global _name shadps4
%global tag 4.2026.09.20.277.671.9.2357.392.9339.89.8.8
# Upstream shadps4-emu/shadPS4 commit the aarch64 patch series is based on
%global commit 4a151b811634a7bcf1c0140cb0959cefeedf7439
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}
# Prebuilt FFmpeg release matching externals/ffmpeg-core
%global ffmpeg_sha 94dde08

%global toolchain clang
%global _lto_cflags %{nil}

Name:           %{_name}-git
Version:        %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:        1%{?dist}
Summary:        PlayStation 4 emulator (native aarch64 port using box64 dynarec)
License:        GPL-2.0-or-later
URL:            https://github.com/shadps4-emu/shadPS4
Source0:        https://github.com/shadps4-emu/shadPS4/archive/%{commit}/shadPS4-%{commit}.tar.gz
Source1:        https://github.com/shadps4-emu/ext-ffmpeg-core/releases/download/%{ffmpeg_sha}/ffmpeg-linux-arm64.zip
Source2:        https://github.com/shadps4-emu/ext-ffmpeg-core/releases/download/%{ffmpeg_sha}/ffmpeg-linux-x64.zip
# Native aarch64 support: box64 dynarec as guest CPU, bridges, JIT fault recovery,
# portable SRT walker, 16K page tracking (github.com/lacamar/shadps4 branch aarch64)
Patch0:         0001-native-aarch64-box64.patch

# Submodules (externals/), fetched as tarballs; nested ones listed after their parent.
%{lua:
local externals = {
 { name="CLI11", ref="12ba4ac4dbaa6489cb07e01be796e2bc074ef4f4", owner="shadexternals", path="CLI11" },
 { name="ImGuiFileDialog", ref="57a1c6a6d44bd99e844e3642d27851f6c065af62", owner="shadexternals", path="ImGuiFileDialog" },
 { name="ext-LibAtrac9", ref="946e05a9212976626a9f5e52f29c0a7202871f29", owner="shadps4-emu", path="LibAtrac9" },
 { name="fdk-aac", ref="ee76460efbdb147e26d804c798949c23f174460b", url="https://android.googlesource.com/platform/external/aac/+archive/ee76460efbdb147e26d804c798949c23f174460b.tar.gz", path="aacdec/fdk-aac", strip=0 },
 { name="abseil-cpp", ref="76bb24329e8bf5f39704eb10d21b9a80befa7c81", owner="abseil", path="abseil-cpp" },
 { name="box64", ref="496fb4bebf13f9172db7cd33a52e9aad3bc89874", owner="ptitSeb", path="box64" },
 { name="cpp-httplib", ref="28f8264d134a576422cd0f99f19719c2749d9e47", owner="shadexternals", path="cpp-httplib" },
 { name="date", ref="a45ea7c17b4a7f320e199b71436074bd624c9e15", owner="HowardHinnant", path="date" },
 { name="ext-discord-rpc", ref="19f66e6dcabb2268965f453db9e5774ede43238f", owner="shadps4-emu", path="discord-rpc" },
 { name="rapidjson", ref="d621dc9e9c77f81e5c8a35b8dcc16dcd63351321", owner="Tencent", path="discord-rpc/thirdparty/rapidjson" },
 { name="epoll-shim", ref="18159584bb3d17e601b9315a7398ace018251bdc", owner="jiixyj", path="epoll-shim" },
 { name="ext-boost", ref="ca6f230e67be7cc45fc919057f07b2aee64dadc1", owner="shadps4-emu", path="ext-boost" },
 { name="ext-wepoll", ref="d3bb81035304a0dc6a5ca48ebf0f8cee1fe269e4", owner="shadps4-emu", path="ext-wepoll" },
 { name="ext-ffmpeg-core", ref="94dde08c8a9e4271a93a2a7e4159e9fb05d30c0a", owner="shadps4-emu", path="ffmpeg-core" },
 { name="ext-fmt", ref="ec73fb72477d80926c758894a3ab2cb3994fd051", owner="shadps4-emu", path="fmt" },
 { name="freetype", ref="b91f75bd02db43b06d634591eb286d3eb0ce3b65", owner="freetype", path="freetype" },
 { name="glslang", ref="ba1640446f3826a518721d1f083f3a8cca1120c3", owner="KhronosGroup", path="glslang" },
 { name="half", ref="1ddada225144cac0de8f6b5c0dd9acffd99a2e68", owner="ROCm", path="half" },
 { name="ext-hwinfo", ref="8660006e0ca4aae5dda7a29e585968b50b0273b7", owner="shadps4-emu", path="hwinfo" },
 { name="imgui", ref="7e1b65d26d52e9dd199d889c148c72184de647b4", owner="shadexternals", path="imgui" },
 { name="json", ref="55f93686c01528224f448c19128836e7df245f72", owner="nlohmann", path="json" },
 { name="libpng", ref="c1cc0f3f4c3d4abd11ca68c59446a29ff6f95003", owner="pnggroup", path="libpng" },
 { name="libressl", ref="b0504086dbbc186724b0cc92e6ba1832c245de0b", owner="shadexternals", path="libressl" },
 { name="libusb", ref="d087ea86539ab1f1ec42faf86e2357e2fad126a6", owner="shadexternals", path="libusb" },
 { name="magic_enum", ref="a413fcc9c46a020a746907136a384c227f3cd095", owner="Neargye", path="magic_enum" },
 { name="minimp3", ref="7b590fdcfa5a79c033e76eacc05d0c3e4c79f536", owner="lieff", path="minimp3" },
 { name="miniupnp", ref="bf4215a7574f88aa55859db9db00e3ae58cf42d6", owner="miniupnp", path="miniupnp" },
 { name="miniz", ref="174573d60290f447c13a2b1b3405de2b96e27d6c", owner="richgel999", path="miniz" },
 { name="openal-soft", ref="83ea7236c6f23fc98e2b62eb9c5b3abfd4b2be86", owner="shadexternals", path="openal-soft" },
 { name="protobuf", ref="5917ee224a7e47383a78acc129628511fe210dff", owner="shadexternals", path="protobuf" },
 { name="pugixml", ref="caade5a28aad86b92a4b5337a9dc70c4ba73c5eb", owner="zeux", path="pugixml" },
 { name="robin-map", ref="4ec1bf19c6a96125ea22062f38c2cf5b958e448e", owner="Tessil", path="robin-map" },
 { name="sdl3", ref="d5af35e3fbb5bb6555ed00e69740d52af2a4e877", owner="shadexternals", path="sdl3" },
 { name="sirit", ref="c58f4d441cfdb6905d011a906704716833485486", owner="shadps4-emu", path="sirit" },
 { name="SPIRV-Headers", ref="2acb319af38d43be3ea76bfabf3998e5281d8d12", owner="KhronosGroup", path="sirit/externals/SPIRV-Headers" },
 { name="spdlog", ref="b8944a4bcd478ee03375c9c50dc8d6c741f43f7b", owner="gabime", path="spdlog" },
 { name="toml11", ref="a01fe3b4c14c6d7b99ee3f07c9e80058c6403097", owner="ToruNiina", path="toml11" },
 { name="tracy", ref="143a53d1985b8e52a7590a0daca30a0a7c653b42", owner="shadps4-emu", path="tracy" },
 { name="VulkanMemoryAllocator", ref="f378e7b3f18f6e2b06b957f6ba7b1c7207d2a536", owner="GPUOpen-LibrariesAndSDKs", path="vma" },
 { name="Vulkan-Headers", ref="ee3b5caaa7e372715873c7b9c390ee1c3ca5db25", owner="KhronosGroup", path="vulkan-headers" },
 { name="Vulkan-Loader", ref="466498bc64eb77955c3b782f0127520548224de0", owner="KhronosGroup", path="vulkan-loader" },
 { name="xbyak", ref="44a72f369268f7d552650891b296693e91db86bb", owner="herumi", path="xbyak" },
 { name="xxHash", ref="953a09abc39096da9e216b6eb0002c681cdc1199", owner="Cyan4973", path="xxhash" },
 { name="ZArchive", ref="965b66c8d67b6b7e30fd63b3b75aa91a99ff303b", owner="shadexternals", path="zarchive" },
 { name="ext-zlib-ng", ref="fd0d263cedab1a136f40d65199987e3eaeecfcbd", owner="shadps4-emu", path="zlib-ng" },
 { name="zstd", ref="5c7b7bad26808e6b40ac3b3d0075466e27738a9d", owner="shadexternals", path="zstd" },
 { name="zydis", ref="120e0e705f8e3b507dc49377ac2879979f0d545c", owner="zyantific", path="zydis" },
 { name="zycore-c", ref="38d4f0285e6157ee840ea82a9b90aba71c8a705d", owner="zyantific", path="zydis/dependencies/zycore" },
}
for i, s in ipairs(externals) do
  si = 100 + i
  if s.url then
    print(string.format("Source%d: %s#/%s-%s.tar.gz", si, s.url, s.name, s.ref).."\n")
  else
    print(string.format("Source%d: https://github.com/%s/%s/archive/%s/%s-%s.tar.gz", si, s.owner, s.name, s.ref, s.name, s.ref).."\n")
  end
  print(string.format("Provides: bundled(%s)", s.name).."\n")
end
function print_setup_externals()
  for i, s in ipairs(externals) do
    si = 100 + i
    local strip = s.strip or 1
    print(string.format("rm -rf externals/%s && mkdir -p externals/%s\n", s.path, s.path))
    print(string.format("tar -xzf %s --strip-components=%d -C externals/%s\n", rpm.expand("%{SOURCE"..si.."}"), strip, s.path))
  end
end
}

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
%autosetup -p1 -n shadPS4-%{commit}
%{lua: print_setup_externals()}
# ffmpeg-core derives the prebuilt archive name from git; feed it offline.
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
* Sun Sep 20 2026 Lachlan Marie <lchlnm@pm.me> - 4.2026.09.20.277.671.9.2357.392.9339.89.8.8^0.git.4a151b8-1
 - Update to 4.2026.09.20.277.671.9.2357.392.9339.89.8.8

* Sat Sep 19 2026 lm <lchlnm@pm.me> - 1
- Skip block re-validation for immutable text segments
- Cheaper fault handling inside JIT code
- Rebase on upstream 42c555b

* Fri Sep 18 2026 Lachlan Marie <lchlnm@pm.me> - 4.2026.09.18.42.555.7.5.0678.531.7.4.505560.0.8^0.git.42c555b-1
 - Update to 4.2026.09.18.42.555.7.5.0678.531.7.4.505560.0.8

* Fri Sep 18 2026 lm <lchlnm@pm.me> - 0.18.0^1.git.ba74702-1
- Initial package
- Native aarch64 port via box64 dynarec as patch on upstream
