%global bumpver 81

%global tag 0.0.40
%global commit c11979d1245509478145da11d7fcbe4e8815dd15
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:       rpcs3-git
Version:    %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:    1%{dist}
Summary:    PlayStation 3 emulator and debugger

Conflicts:      rpcs3
Provides:       rpcs3

License:  GPLv2
URL:      https://github.com/RPCS3/rpcs3
Source0:  https://github.com/RPCS3/rpcs3/archive/%{shortcommit}/rpcs3-%{shortcommit}.tar.gz

%{lua:
local externals = {
 { name="7zip", ref="839151e", owner="ip7z", path="7zip/7zip", version="26.00",  license="GNU-LGPL" },
 { name="FAudio", ref="dc034fc", owner="FNA-XNA", path="FAudio", version="26.03",  license="zlib" },
 { name="VulkanMemoryAllocator", ref="1d8f600", owner="GPUOpen-LibrariesAndSDKs", path="GPUOpen/VulkanMemoryAllocator", version="3.3.0",  license="MIT" },
 { name="openal-soft", ref="c41d64c", owner="kcat", path="OpenAL/openal-soft", version="1.25.1",  license="PFFFT" },
 { name="soundtouch", ref="3982730", owner="RPCS3", path="SoundTouch/soundtouch/", version="2.4.0",  license="LGPLv2.1" },
 { name="asmjit", ref="416f735", owner="asmjit", path="asmjit/asmjit/", license="zlib" },
 { name="cubeb", ref="4848575", owner="mozilla", path="cubeb/cubeb", license="ISC" },
 { name="curl", ref="400fffa", owner="curl", path="curl/curl", version="8.17.0",  license="MIT" },
 { name="discord-rpc", ref="3dc2c32", owner="Vestrel", path="discord-rpc/discord-rpc", license="MIT" },
 { name="gamemode", ref="c54d6d4", owner="FeralInteractive", path="feralinteractive/feralinteractive", version="1.8.2", license="BSD-3-Clause" },
 { name="ffmpeg-core", ref="ce81114", owner="RPCS3", path="ffmpeg", version="7.1.2", license="LGPLv2.1" },
 { name="Fusion", ref="759ac5d", owner="xioTechnologies", path="fusion/fusion", version="1.2.9",  license="MIT" },
 { name="glslang", ref="fc9889c", owner="KhronosGroup", path="glslang/glslang", version="15.3.0",  license="BSD-3-Clause" },
 { name="hidapi", ref="d6b2a97", owner="RPCS3", path="hidapi/hidapi", version="0.15.0",  license="GPLv3, BSD" },
 { name="libpng", ref="c3e3049", owner="pnggroup", path="libpng/libpng", version="1.6.55",  license="PNGRLLv2" },
 { name="SDL", ref="683181b", owner="libsdl-org", path="libsdl-org/SDL", version="3.4.2",  license="zlib" },
 { name="libusb", ref="15a7ebb", owner="libusb", path="libusb/libusb", version="1.0.29",  license="LGPLv2.1" },
 { name="llvm-project", ref="cd70802", owner="llvm", path="llvm/llvm", version="19.1.7",  license="Apache-v2" },
 { name="miniupnp", ref="d66872e", owner="miniupnp", path="miniupnp/miniupnp", version="2.3.9",  license="BSD-3-Clause" },
 { name="opencv_minimal", ref="67f53c2", owner="Megamouse", path="opencv/opencv", version="4.12.0" },
 { name="protobuf", ref="edaa823", owner="protocolbuffers", path="protobuf/protobuf", version="33.4",  license="BSD-3-Clause" },
 { name="pugixml", ref="ee86beb", owner="zeux", path="pugixml", version="1.15",  license="MIT" },
 { name="rtmidi", ref="1e5b499", owner="thestk", path="rtmidi", version="6.0.0",  license="MIT" },
 { name="stb", ref="013ac3b", owner="nothings", path="stblib/stb", license="MIT" },
 { name="wolfssl", ref="b077c81", owner="wolfSSL", path="wolfssl/wolfssl", version="5.8.2",  license="GPLv3" },
 { name="yaml-cpp", ref="51a5d62", owner="RPCS3", path="yaml-cpp/yaml-cpp", version="0.9.0",  license="MIT" },
 { name="zlib", ref="da607da", owner="madler", path="zlib/zlib", version="1.3.2",  license="zlib" },
 { name="zstd", ref="f8745da", owner="facebook", path="zstd/zstd", version="1.5.7",  license="GPLv2" },
}

for i, s in ipairs(externals) do
  si = 100 + i
  print(string.format("Source%d: https://github.com/%s/%s/archive/%s/%s-%s.tar.gz", si, s.owner, s.name, s.ref, s.name, s.ref).."\n")
  if s.bcond and not rpm.isdefined(string.format("with_%s", s.bcond)) then goto continue1 end
  print(string.format("Provides: bundled(%s) = %s", (s.package or s.name), (s.version or "0")).."\n")
  ::continue1::
end

function print_setup_externals()
  for i, s in ipairs(externals) do
    si = 100 + i
    if s.bcond and not rpm.isdefined(string.format("with_%s", s.bcond)) then goto continue2 end
    print(string.format("mkdir -p 3rdparty/%s", (s.path or s.name)).."\n")
    print(string.format("tar -xzf %s --strip-components=1 -C 3rdparty/%s", rpm.expand("%{SOURCE"..si.."}"), (s.path or s.name)).."\n")
    ::continue2::
  end
end
}


BuildRequires:  cmake
BuildRequires:  git
BuildRequires:  ninja-build
BuildRequires:  pkgconfig
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  ffmpeg-free-devel
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qttools-devel
BuildRequires:  libX11-devel
BuildRequires:  libXrandr-devel
BuildRequires:  glew-devel
BuildRequires:  vulkan-devel
BuildRequires:  libudev-devel
BuildRequires:  libusb1-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  openal-soft-devel
BuildRequires:  wayland-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  egl-wayland-devel
BuildRequires:  libwayland-egl
BuildRequires:  libcurl-devel
BuildRequires:  opencv-devel
BuildRequires:  libzstd-devel
BuildRequires:  git-all

%if 0%{?fedora} <= 44
BuildRequires:  rtmidi-devel
%endif

BuildRequires:  alsa-lib-devel
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  glew
BuildRequires:  glew-devel
BuildRequires:  libatomic
BuildRequires:  libevdev-devel
BuildRequires:  libudev-devel
BuildRequires:  openal-soft-devel
# BuildRequires:  openal-devel
BuildRequires:  qt6-qtbase-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  vulkan-devel
BuildRequires:  pipewire-jack-audio-connection-kit-devel
# BuildRequires:  jack-audio-connection-kit-devel
BuildRequires:  qt6-qtmultimedia-devel
BuildRequires:  qt6-qtsvg-devel
BuildRequires:  llvm-devel
BuildRequires:  SDL3-devel
BuildRequires:  doxygen
BuildRequires:  gtest-devel
BuildRequires:  abseil-cpp-devel

%description
PlayStation 3 emulator and debugger

%prep
%autosetup -n rpcs3-%{commit}

%{lua: print_setup_externals()}

sed -i "/^set(RTMIDI_TARGETNAME_UNINSTALL \"uninstall\" CACHE STRING \"Name of 'uninstall' build target\")\$/d" \
    3rdparty/rtmidi/CMakeLists.txt

sed -i '1i#pragma GCC diagnostic push\n#pragma GCC diagnostic ignored "-Wold-style-cast"' \
      rpcs3/Emu/CPU/sse2neon.h
echo '#pragma GCC diagnostic pop' \
      >> rpcs3/Emu/CPU/sse2neon.h


%build
export CXXFLAGS="$CXXFLAGS -Wno-error=old-style-cast -Wno-old-style-cast"

%if %{with clang}
export CC=clang
export CXX=clang++
export LINKER=ld.lld
%else
export CC=gcc
export CXX=g++
export LINKER=gold
%endif
export LINKER_FLAG="-fuse-ld=${LINKER}"

cmake -B build \
      -Wno-dev \
      -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_CXX_FLAGS="$CXXFLAGS" \
      -DLLVM_TARGETS_TO_BUILD=AArch64 \
      -DCMAKE_EXE_LINKER_FLAGS="${LINKER_FLAG}" \
      -DCMAKE_MODULE_LINKER_FLAGS="${LINKER_FLAG}" \
      -DCMAKE_SHARED_LINKER_FLAGS="${LINKER_FLAG}" \
      -DUSE_PRECOMPILED_HEADERS=OFF \
      -DBUILD_RPCS3_TESTS=OFF \
      -DRUN_RPCS3_TESTS=OFF \
      -DUSE_SDL=ON \
      -DUSE_SYSTEM_SDL=ON \
      -DUSE_SYSTEM_FFMPEG=ON \
      -DUSE_NATIVE_INSTRUCTIONS=OFF \
      -DUSE_SYSTEM_CURL=ON \
      -DUSE_SYSTEM_ZSTD=ON \
      -DUSE_SYSTEM_RTMIDI=ON \
      -DUSE_DISCORD_RPC=ON \
      -DUSE_SYSTEM_OPENCV=ON \
      -DDISABLE_LTO=TRUE \
      -DOpenGL_GL_PREFERENCE=LEGACY \
      -DCMAKE_INSTALL_PREFIX=%{_prefix} \
      -DCMAKE_INSTALL_LIBDIR=%{_lib} \
      -DCMAKE_EXE_LINKER_FLAGS="-L/usr/lib64/pipewire-0.3/jack" \
      -DSTATIC_LINK_LLVM=ON \
      -G Ninja

      # -B build \
      # -Wno-dev \
      # -DCMAKE_BUILD_TYPE=Release \
      # -DCMAKE_CXX_FLAGS="$CXXFLAGS" \
      # -DLLVM_TARGETS_TO_BUILD=AArch64 \
      # -DCMAKE_EXE_LINKER_FLAGS="${LINKER_FLAG}" \
      # -DCMAKE_MODULE_LINKER_FLAGS="${LINKER_FLAG}" \
      # -DCMAKE_SHARED_LINKER_FLAGS="${LINKER_FLAG}" \
      # -DDISABLE_LTO=TRUE \
      # -DOpenGL_GL_PREFERENCE=LEGACY \
      # -DCMAKE_INSTALL_PREFIX=%{_prefix} \
      # -DCMAKE_INSTALL_LIBDIR=%{_lib} \
      # -DCMAKE_EXE_LINKER_FLAGS="-L/usr/lib64/pipewire-0.3/jack" \
      # -G Ninja
      #
      # -DUSE_NATIVE_INSTRUCTIONS=OFF "USE_NATIVE_INSTRUCTIONS makes rpcs3 compile with -march=native, which is useful for local builds, but not good for packages." ON)
      # -DWITH_LLVM=ON "Enable usage of LLVM library" ON)
      # -DBUILD_LLVM=ON "Build LLVM from git submodule" OFF)
      # -DSTATIC_LINK_LLVM=ON "Link against LLVM statically. This will get set to ON if you build LLVM from the submodule." OFF)
      # -DUSE_FAUDIO=ON "FAudio audio backend" ON)
      # -DUSE_LIBEVDEV "libevdev-based joystick support" ON)
      # -DUSE_DISCORD_RPC=ON "Discord rich presence integration" OFF)
      # -DUSE_VULKAN=ON "Vulkan render backend" ON)
      # -DUSE_PRECOMPILED_HEADERS=OFF "Use precompiled headers" OFF)
      # -DUSE_SDL=ON "Enables SDL input handler" OFF)
      # -DUSE_SYSTEM_CUBEB "Prefer system cubeb instead of the builtin one" OFF)
      # -DUSE_SYSTEM_CURL=ON "Prefer system Curl instead of the prebuild one" ON)
      # -DUSE_SYSTEM_FAUDIO "Prefer system FAudio instead of the builtin one" OFF)
      # -DUSE_SYSTEM_FFMPEG=ON "Prefer system ffmpeg instead of the prebuild one" OFF)
      # -DUSE_SYSTEM_PROTOBUF "Prefer system protobuf instead of the builtin one" OFF)
      # -DUSE_SYSTEM_GLSLANG "Prefer system glslang instead of the builtin one" OFF)
      # -DUSE_SYSTEM_HIDAPI "Prefer system hidapi instead of the builtin one" OFF)
      # -DUSE_SYSTEM_LIBPNG "Prefer system libpng instead of the builtin one" OFF)
      # -DUSE_SYSTEM_LIBUSB "Prefer system libusb instead of the builtin one" OFF)
      # -DUSE_SYSTEM_MINIUPNPC "Prefer system MiniUPnPc instead of the builtin one" OFF)
      # -DUSE_SYSTEM_MVK "Prefer system MoltenVK instead of the builtin one" OFF)
      # -DUSE_SYSTEM_OPENAL "Prefer system OpenAL instead of the prebuild one" ${USE_SYSTEM_OPENAL_DEFAULT})
      # -DUSE_SYSTEM_OPENCV=ON "Prefer system OpenCV instead of the builtin one" ON)
      # -DUSE_SYSTEM_PUGIXML "Prefer system pugixml instead of the builtin one" OFF)
      # -DUSE_SYSTEM_RTMIDI=ON "Prefer system RtMidi instead of the builtin one" OFF)
      # -DUSE_SYSTEM_SDL=ON "Prefer system SDL instead of the builtin one" ON)
      # -DUSE_SYSTEM_VULKAN_MEMORY_ALLOCATOR "Prefer system Vulkan Memory Allocator instead of the builtin one" OFF)
      # -DUSE_SYSTEM_WOLFSSL "Prefer system wolfSSL instead of the builtin one" OFF)
      # -DUSE_SYSTEM_ZLIB "Prefer system ZLIB instead of the builtin one" ON)
      # -DUSE_SYSTEM_ZSTD=ON "Prefer system zstd instead of the builtin one" OFF)
      # -DHAS_MEMORY_BREAKPOINTS "Add support for memory breakpoints to the interpreter" OFF)
      # -DUSE_LTO "Use LTO for building" ON)
      # -DBUILD_RPCS3_TESTS=OFF "Build RPCS3 unit tests." OFF)
      # -DRUN_RPCS3_TESTS=OFF "Run RPCS3 unit tests. Requires BUILD_RPCS3_TESTS" OFF)
      # -DUSE_GAMEMODE=ON "Choose whether to enable GameMode features or not." ON)




cd build
ninja


%install
cd build
DESTDIR=%{buildroot} ninja install


%files
%license LICENSE
%doc    README.md
%define debug_package %{nil}

%{_bindir}/rpcs3
%{_datadir}/applications/rpcs3.desktop
%{_datadir}/metainfo/rpcs3.metainfo.xml
%{_datadir}/icons/hicolor/48x48/apps/rpcs3.png
%{_datadir}/icons/hicolor/scalable/apps/rpcs3.svg
%{_datadir}/rpcs3


%changelog
* Fri May 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^81.git.c11979d-1
 - Update to commit c11979d1245509478145da11d7fcbe4e8815dd15

* Fri May 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^80.git.3058a71-1
 - Update to commit 3058a71d72fb9f20254b56420c8831f1818e567a

* Thu May 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^79.git.b41b10a-1
 - Update to commit b41b10a031f5e5070f52e20b8228ff4f4d389ebf

* Wed May 27 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^78.git.a87d175-1
 - Update to commit a87d175295cc33df2264939c5437ed3b3f6790e1

* Mon May 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^77.git.dd81c92-1
 - Update to commit dd81c92a02b28ecc2a38ba8af358bb1b9220486d

* Sat May 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^76.git.0a5b88a-1
 - Update to commit 0a5b88ac386d019cd9fbae82968689b6c3b5dcf8

* Fri May 22 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^75.git.f63a34d-1
 - Update to commit f63a34dcc205d9c704eb694e4e9a95ce7d6639bd

* Thu May 21 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^74.git.67464f9-1
 - Update to commit 67464f97df8679d5d540256987551f34fe00d4cc

* Thu May 21 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^73.git.d7da6a7-1
 - Update to commit d7da6a713b31536b7dad8fd07ea5ff04042d3ee4

* Wed May 20 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^72.git.2613d7e-1
 - Update to commit 2613d7eee7de144e80b7c2e866a4c3dd8ad24f33

* Tue May 19 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^71.git.55e17cc-1
 - Update to commit 55e17ccd3b12810e1a9c09587ab93f9dbb595b1c

* Tue May 19 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^70.git.79cb35d-1
 - Update to commit 79cb35daa6562c0ee543eaf95d2c6befb768925e

* Mon May 18 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^69.git.b0c1791-1
 - Update to commit b0c1791a0c2232439677ab8d783384a9ce391d58

* Sun May 17 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^68.git.61a2604-1
 - Update to commit 61a2604824b01382bf57651b85f87b811306c2de

* Sun May 17 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^67.git.08c9266-1
 - Update to commit 08c926622da1c3cd0213ac6b06eda07c31e55c7d

* Fri May 15 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^66.git.b533a56-1
 - Update to commit b533a560e6df6f8aa1c271bfffbd1e39f500bd65

* Fri May 15 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^65.git.5f00b87-1
 - Update to commit 5f00b87a44e09ef37127cb6833ecc2d8fc43b322

* Thu May 14 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^64.git.c860aa2-1
 - Update to commit c860aa2107dd1c4753cd1f56e77446f209833482

* Thu May 14 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^63.git.320e8d6-1
 - Update to commit 320e8d634ae0a0dc0917e9483d12e5156c655160

* Wed May 13 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^62.git.2387af0-1
 - Update to commit 2387af0854a9bbdb39e8da61828c9fe33de04cab

* Wed May 13 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^61.git.021f16f-1
 - Update to commit 021f16f775fadaf5d9f2ed0584972b0bd0e4b6db

* Tue May 12 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^60.git.fb1c1ee-1
 - Update to commit fb1c1eeaefe61aabad521e4ca73afe65e428a285

* Mon May 11 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^59.git.6b5a2f7-1
 - Update to commit 6b5a2f781aae6f87007b4cf7a12375b84882d0ea

* Mon May 11 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^58.git.6b5a2f7-1
 - Update to commit 6b5a2f781aae6f87007b4cf7a12375b84882d0ea

* Sun May 10 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^57.git.29b4577-1
 - Update to commit 29b4577fdb1e9d168097ad6149c2e1772f936cdc

* Sun May 10 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^56.git.b34eba2-1
 - Update to commit b34eba2fb3ca6878a62ac7cbe67aaefd6cadbe0c

* Sat May 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^55.git.6850e2e-1
 - Update to commit 6850e2e5a8524180fb7cb014ff3703ed2bb7b689

* Sat May 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^54.git.4312221-1
 - Update to commit 431222149882e63a30fdfa7fcc6b25db4e1dfc43

* Fri May 08 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^53.git.e2e1cf0-1
 - Update to commit e2e1cf02f4329c78b885c359777bf4de46139da6

* Thu May 07 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^52.git.0262973-1
 - Update to commit 026297334f28500c8cbf6a5f48f395196700d6d7

* Wed May 06 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^51.git.4f47fee-1
 - Update to commit 4f47fee36039f38449830eccf10e72282d680f1a

* Wed May 06 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^50.git.d93d9b2-1
 - Update to commit d93d9b2c5aa859d1cf2f1381cefd204fb022163a

* Tue May 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^49.git.4f23f55-1
 - Update to commit 4f23f5505a0847c368df543536571255956f27be

* Tue May 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^48.git.350e7b0-1
 - Update to commit 350e7b09f52c01fb31b0f0568563aefa008a81af

* Mon May 04 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^47.git.7738081-1
 - Update to commit 773808169e94f2a980db6fa4983b4fcb2a83d16e

* Sun May 03 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^46.git.a6fb0c8-1
 - Update to commit a6fb0c8931b2dcfb02463295d52a3b317e092fc1

* Sat May 02 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^45.git.e8cd6f4-1
 - Update to commit e8cd6f4ef6bb4c4d468c8e4ae29263f5c9b7f733

* Fri May 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^44.git.b6ed420-1
 - Update to commit b6ed4201dfef5d9c3301bf6f30266e4a33674ac5

* Fri May 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^43.git.c25e3e3-1
 - Update to commit c25e3e33acdcf0e62f8b52a201e5c189fbba5b16

* Thu Apr 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^42.git.f3cf1da-1
 - Update to commit f3cf1da7b771d9077e68987dc845aa1eb2952fd1

* Wed Apr 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^41.git.e05d359-1
 - Update to commit e05d35972192f7cb9a3af39dac83d6bd402c6861

* Tue Apr 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^40.git.6d05858-1
 - Update to commit 6d058586c460c95fc2fb71df518621df05ca9ee1

* Tue Apr 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^39.git.3b21833-1
 - Update to commit 3b21833b8e923a8caf48f2b240453bfc56ebc034

* Sun Apr 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^38.git.96f73f4-1
 - Update to commit 96f73f4497fd6fdafd40dc50f24c95c90cd4acc9

* Sat Apr 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^37.git.e1734b5-1
 - Update to commit e1734b51c3e24e60403e46efaf47fe143a3add62

* Fri Apr 24 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^36.git.b3cc013-1
 - Update to commit b3cc01387f753df601ebbf1e771d9103aeab38ae

* Wed Apr 22 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^35.git.e26c80c-1
 - Update to commit e26c80c12908c95301fc7088f778cd499a6fe1ef

* Wed Apr 22 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^34.git.1ca8ab3-1
 - Update to commit 1ca8ab393aacae3e5cd736427b6aea1e57d73ee2

* Tue Apr 21 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^33.git.814821d-1
 - Update to commit 814821d76047209739d1290079b694991fad661b

* Mon Apr 20 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^32.git.b6c8374-1
 - Update to commit b6c8374aa5370a386d069b8f20a85b2323a18e9e

* Sat Apr 18 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^31.git.3b9cc0b-1
 - Update to commit 3b9cc0bc3ae104f86b66de0e013df58151e193f5

* Thu Apr 16 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^30.git.a7c606c-1
 - Update to commit a7c606c8ac8951760868fd3dce2e694631c7bb4f

* Wed Apr 15 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^29.git.7d41bbd-1
 - Update to commit 7d41bbdd2b645655ff8f8bab5237e0df934bbda3

* Tue Apr 14 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^28.git.0b9c53e-1
 - Update to commit 0b9c53e254340db8c7afb4ed0b994d1278b0ead7

* Tue Apr 14 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^27.git.bcd9663-1
 - Update to commit bcd9663349f1e2404976188d9997878ea036bc93

* Sun Apr 12 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^26.git.f826f95-1
 - Update to commit f826f95c70b09565d923b51a6dcb10b34fe1b445

* Fri Apr 10 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^25.git.8121bd4-1
 - Update to commit 8121bd443ca355ab89b894099c19dc02ac535f9d

* Fri Apr 10 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^24.git.a1a140d-1
 - Update to commit a1a140db91ea6617aa85efe2c9111c6a79c59186

* Thu Apr 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^23.git.1d85de6-1
 - Update to commit 1d85de6236ba0e1e7de9a582d5d052221458f505

* Thu Apr 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^22.git.6981e30-1
 - Update to commit 6981e308a07dd61bc1dbc0acee9145ab0b955e19

* Wed Apr 08 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^21.git.beac01d-1
 - Update to commit beac01d5d1bb4ccc67d8f3ab3c86e9cd374c4acf

* Tue Apr 07 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^20.git.34c26ef-1
 - Update to commit 34c26eff68c948ff4a6520e886badcc2b58ddad0

* Mon Apr 06 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^19.git.ce12c29-1
 - Update to commit ce12c29441a3c1755610d427bb23edbbaa169641

* Sun Apr 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^18.git.ec98978-1
 - Update to commit ec989781a345839423b34656beda5e7e62a98c3e

* Sat Apr 04 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^17.git.110ef81-1
 - Update to commit 110ef818b3fbeb50b09f851c9aa80e2fa280a873

* Sat Apr 04 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^16.git.aa841ac-1
 - Update to commit aa841ac332195a58d58c556d7de182b5f7fce3e4

* Fri Apr 03 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^15.git.f63b1b5-1
 - Update to commit f63b1b5dc1b8704278ba896ad536b8a2c3ed77bb

* Wed Apr 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^14.git.ac104a5-1
 - Update to commit ac104a519e80a0960f3b6ce0441aa96c77cabcd2

* Tue Mar 31 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^13.git.122ccca-1
 - Update to commit 122ccca50e3508905aff79200e5ada12308275eb

* Tue Mar 31 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^12.git.1c37f64-1
 - Update to commit 1c37f64a58583b2f80ad9bd12f928b49176b60fd

* Mon Mar 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^11.git.3e60bd2-1
 - Update to commit 3e60bd2aa600c328eebccb7b905f9c5e6d394aef

* Mon Mar 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^10.git.aa7cf5e-1
 - Update to commit aa7cf5ea153ececef87d0dc0982522ea690b281e

* Sun Mar 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^9.git.51ea735-1
 - Update to commit 51ea735cb5fab5f3ab0dda756f19a753aaa07451

* Sat Mar 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^8.git.976cd1c-1
 - Update to commit 976cd1ce6640daf6d19a9618c40b100f89fe9434

* Fri Mar 27 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^7.git.72b872d-1
 - Update to commit 72b872df661abb94e867f3d4e3003d4178ae3ae5

* Fri Mar 27 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^6.git.bb3e268-1
 - Update to commit bb3e2689d4fa7ba43011ac98dae1b10a55807437

* Thu Mar 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^5.git.9b6bc7c-1
 - Update to commit 9b6bc7c1b441a19000925ba79886dddaf6cb0cb7

* Wed Mar 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^4.git.18bd6d6-1
 - Update to commit 18bd6d681e51c2a44394ee9943d4c379c9cef69c

* Wed Mar 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^3.git.a03d4f6-1
 - Update to commit a03d4f69f8a57e44e20adb6f0e33a38dd5479326

* Tue Mar 24 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^2.git.2bcc27d-1
 - Update to commit 2bcc27d581875025610f6f0ad4b34053cd5a470b

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^1.git.36e1d66-1
 - Update to commit 36e1d664ea963391793218550f10fd49f4d2e177

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^0.git.5a90dc0-1
 - Update to 0.0.40

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - v0.0.40^0.git.5a90dc0-1
 - Update to commit 5a90dc005969218aa05b4cfdf7cd24d3aa259986

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^1.git.5a90dc0-1
 - Update to commit 5a90dc005969218aa05b4cfdf7cd24d3aa259986

* Mon Mar 16 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^88.git.297db87-1
 - Update to commit 297db8713fbb02bfb156edb6c03c68850825a83e

* Sun Mar 15 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^87.git.5274210-1
 - Update to commit 5274210ba8307f1c0a45a8398d3ba9e9c8840f19

* Sun Mar 15 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^86.git.1627757-1
 - Update to commit 16277576089e1733987deeac54b627b25d67d800

* Thu Mar 12 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^85.git.e6cf05c-1
 - Update to commit e6cf05cfb73e156818685495814b0b7b8edaa97b

* Wed Mar 11 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^84.git.ee01d11-1
 - Update to commit ee01d1186ffe80042a5f61830a6407ac739d07df

* Sun Mar 08 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^83.git.41db06b-1
 - Update to commit 41db06b53f906fbe2941552008ea8b468fa38482

* Sat Mar 07 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^82.git.ac30fee-1
 - Update to commit ac30feeddb4d53f08397897574649228b8c187d1

* Fri Mar 06 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.40^81.git.c57d611-1
 - Update to commit c57d6110c4c503e8145c9d18e38042d275cd6995

* Thu Mar 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^80.git.d46ddce-1
 - Update to commit d46ddcee5d8db68d7f856c5e7015bffc651b419f

* Tue Mar 03 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^79.git.595e42c-1
 - Update to commit 595e42c4f3bfa11b8585ea029e1aa9d2c9c68fd1

* Mon Mar 02 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^78.git.9288565-1
 - Update to commit 928856567670d123b88b458f450bae0051deecb7

* Sun Mar 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^77.git.00a1c72-1
 - Update to commit 00a1c7278a90d85e5b2e1eb551b9ff80d858b21c

* Sun Mar 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^76.git.5ca19ea-1
 - Update to commit 5ca19eabd548d517b8834e2aa3e08ab90e8d9ebf

* Sun Mar 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^75.git.198c2e9-1
 - Update to commit 198c2e9eb835dbe95c674ad8c98138fb080f1ff4

* Mon Jan 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^74.git.d854ff0-1
 - Update to commit d854ff03febb59d7f37b98ae05d0ffb50d2dca93

* Sun Jan 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^73.git.fbd5bbc-1
 - Update to commit fbd5bbcfa32a83aea9823dae1a34e637f6e56d5e

* Sun Jan 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^70.git.b41c275-1
 - Update to commit b41c2754ce0d49d92dfb7843180abb8682b4a599

* Wed Jan 21 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^69.git.3e49c32-1
 - Update to commit 3e49c32c9c59b2bdf6bb29ec7d1e44074ffad4e5

* Sun Jan 18 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^68.git.0f85e91-1
 - Update to commit 0f85e9123e781b6ec7fa78fa1c54b1de40179a23

* Sat Jan 17 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^67.git.eaebd34-1
 - Update to commit eaebd3426e7050c35beb8f24952d6da4d6a75360

* Wed Jan 14 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^66.git.d7b723c-1
 - Update to commit d7b723cd7c5ddcc785076687772a536a4525918e

* Wed Jan 14 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^65.git.1591b7f-1
 - Update to commit 1591b7f5a6c121ac9cef3e02334e4b07f7d39659

* Wed Jan 14 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^64.git.a0f2f00-1
 - Update to commit a0f2f006b19f9727d882d92bc00446e15d40be3d

* Wed Jan 14 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^63.git.df72f4a-1
 - Update to commit df72f4abed1c838905de5526841605ced5b676ed

* Tue Jan 13 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^62.git.8f8d468-1
 - Update to commit 8f8d4687741d39bc9e2adb3d2d722f9f5f87e08b

* Tue Jan 13 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^61.git.4a12f70-1
 - Update to commit 4a12f70f2cd43ab554da60cc58681df86fe06e58

* Sat Jan 10 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^60.git.a862468-1
 - Update to commit a8624682a770738ffb7d6b0c1ff48dc9c3e6df5b

* Fri Jan 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^59.git.49bcc93-1
 - Update to commit 49bcc930727ced0ea935155f8ef8bf4a4ce4e6e1

* Fri Jan 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^58.git.ef5a4bf-1
 - Update to commit ef5a4bf7e4cd6dddc3dbf10782eba5925b8bd981

* Wed Jan 07 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^57.git.90df8ba-1
 - Update to commit 90df8baa5f296120b1fa02bda6df2f3e33cbc72d

* Tue Jan 06 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^56.git.9fb7c8f-1
 - Update to commit 9fb7c8f52c81e8ed0da55cf9816890bacbf4de04

* Tue Jan 06 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^55.git.9b256d7-1
 - Update to commit 9b256d71a9eb142654de96fdafdcbfda00cf64fe

* Mon Jan 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^54.git.a0e0a6c-1
 - Update to commit a0e0a6c6a6b1b51b51fe58dc356d33916f3ef3f3

* Sun Jan 04 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^53.git.643d110-1
 - Update to commit 643d1102ccedd56f9915b86c53ae9d7251e4c736

* Sat Jan 03 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^52.git.ea6bb77-1
 - Update to commit ea6bb77d57357908706f4fdf7081e2d924c08f1f

* Fri Jan 02 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^51.git.8d55db3-1
 - Update to commit 8d55db334e0416f77188134bf1db128ec440a545

* Thu Jan 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^50.git.ee06dcc-1
 - Update to commit ee06dccdea91814bf7d76b3037371a6477458722

* Thu Jan 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.38^49.git.c551120-1
 - Update to commit c5511200d5a8997b5413b37cb3a4860ab3189a63

* Tue Dec 30 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^48.git.4feb876-1
 - Update to commit 4feb876b7f529e4371a4f4cd5c5c433b33a20c31

* Tue Dec 30 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^47.git.65273dd-1
 - Update to commit 65273dde7621592205fa8251209c7e03f9294a0c

* Mon Dec 29 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^46.git.2579ddf-1
 - Update to commit 2579ddf99603a9d60a76b7d7a545272e6cb008aa

* Sun Dec 28 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^45.git.01fe124-1
 - Update to commit 01fe12483f2c0c7b4b32ce427e9eb7d31c265565

* Thu Dec 25 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^44.git.77aa5d4-1
 - Update to commit 77aa5d4bbfc9ab572b678f872bf8083e0dc0725e

* Wed Dec 24 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^43.git.f81a5a5-1
 - Update to commit f81a5a5cb1cd30678061bff31b2156090abe2a57

* Mon Dec 22 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^42.git.2fb6973-1
 - Update to commit 2fb697322f77fc30969692c63972a567b8bfb573

* Sun Dec 21 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^41.git.f946054-1
 - Update to commit f946054a3781b2ca1aa6c82a21d7ab169cee7823

* Fri Dec 19 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^40.git.cbecb91-1
 - Update to commit cbecb91b943e6a5b304a58e120ce845e413952ec

* Thu Dec 18 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^39.git.5507078-1
 - Update to commit 5507078bd88260a73157d1039a2ba3eca015ffde

* Wed Dec 17 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^38.git.ddfa773-1
 - Update to commit ddfa773675faabee3f58e26cb57c0dce75994585

* Wed Dec 17 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^37.git.b1089ab-1
 - Update to commit b1089ab1a3150bd5810c7bf3956987d2ad438639

* Tue Dec 16 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^36.git.812d84e-1
 - Update to commit 812d84e7f4263905e751f330e3660b8f7ace41af

* Tue Dec 16 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^35.git.cf87f24-1
 - Update to commit cf87f24587754cd3869430d0df6d396985db3165

* Sun Dec 14 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^34.git.c3db85c-1
 - Update to commit c3db85c68e6c1724b239d6b538dd436c404613f6

* Fri Dec 12 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^33.git.f739ce7-1
 - Update to commit f739ce732326bbdff1004fcd8875a5dd1607dd63

* Thu Dec 11 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^32.git.0f1eadc-1
 - Update to commit 0f1eadcab038fa6f2d20cb639fe16d72b97f9b4a

* Wed Dec 10 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^34.git.aff6452-1
 - Update to commit aff645272fb51440276b07fac8d8c219eaee1772

* Tue Dec 09 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^33.git.27f39d2-1
 - Update to commit 27f39d2ac08e40fc705135cba6898bc3166e0e71

* Mon Dec 08 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^32.git.0f1d516-1
 - Update to commit 0f1d516d9ae6a1725e4db5553c99463b1aa6d821

* Sun Dec 07 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^31.git.3f6529f-1
 - Update to commit 3f6529fecbacdf90aa556ae0fd39b478ae28c27f

* Sat Dec 06 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^30.git.54206c6-1
 - Update to commit 54206c62b3968273d927664876adfbd8c1bedfe5

* Fri Dec 05 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^29.git.67f7119-1
 - Update to commit 67f7119717fae25b8b2ecc5469c5fb5db45af1b6

* Thu Dec 04 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^28.git.133b19f-1
 - Update to commit 133b19f2059a8c8bf2a79f8ab04bffd1ad87a89e

* Thu Dec 04 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^27.git.e3f5f2d-1
 - Update to commit e3f5f2d14e44a44eec9f8c0f79f53893ff04fdbc

* Wed Dec 03 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^26.git.b86b4d1-1
 - Update to commit b86b4d15c638644e3ef42ea6fe915733adb7a1bc

* Wed Dec 03 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^25.git.613d428-1
 - Update to commit 613d428ced78c345fd5c0077b0e72d484bce10d5

* Tue Dec 02 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^24.git.3c747b3-1
 - Update to commit 3c747b377f8e7112cfe85ed3b2a8147a9946ca39

* Tue Dec 02 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^23.git.6dd37cb-1
 - Update to commit 6dd37cb2d5db99c7188246df05678b532fff041a

* Tue Dec 02 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^22.git.7e8ed5e-1
 - Update to commit 7e8ed5ecc102609fa0fc80d6a5ffe78d5c21e61e

* Mon Dec 01 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^21.git.25badf9-1
 - Update to commit 25badf9534440e7a723aa14a0f16ddd5aa24b793

* Mon Dec 01 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^20.git.4bda2f9-1
 - Update to commit 4bda2f9b0f81557386ff935c944a596e3c5c1ae1

* Sun Nov 30 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^19.git.c80aba2-1
 - Update to commit c80aba2342a95a84d44cc5559276bf4609924c72

* Sun Nov 30 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^18.git.e938b93-1
 - Update to commit e938b93f487532200d68d75d2bf15af6730e1a08

* Sat Nov 29 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^17.git.d625c1d-1
 - Update to commit d625c1d00416815880183c2edd9173a719c0e4c6

* Fri Nov 28 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^16.git.d9f9130-1
 - Update to commit d9f913016cbbdc32ce43ac02f4e0ef6a8ffd1ae4

* Thu Nov 27 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^15.git.a442cb9-1
 - Update to commit a442cb91a101bf19b1b0912db7fb071d62360369

* Tue Nov 25 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^14.git.5a9083e-1
 - Update to commit 5a9083e4fc0bfb73b09c4c436d8f5e78f8c2702a

* Mon Nov 24 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^13.git.6a398f9-1
 - Update to commit 6a398f994793d6d74d649ec7989d621627e547e1

* Mon Nov 24 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^12.git.89a13b7-1
 - Update to commit 89a13b75f70815f5018c1168b3f5b80ff49d0005

* Sun Nov 23 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^11.git.fcff16b-1
 - Update to commit fcff16b6f711ae7263f883d8efc18a3a3d33e227

* Sun Nov 23 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^10.git.a3f7c0d-1
 - Update to commit a3f7c0d67f7b2aee900201952793fabd15d17903

* Sat Nov 22 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38^9.git.7f68427-1
 - Update to commit 7f6842705ce376587c6062d1471118b7b75ffa76

* Wed Nov 12 2025 Lachlan Marie <lchlnm@pm.me> - git
- Converted to build for git commits

* Mon Aug 11 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.38-1
- Updated to 0.0.38, increased versions of several sources

* Mon Aug 11 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.37-2
- Updated how sources are organised and extracted.

* Sun Jun 08 2025 Lachlan Marie <lchlnm@pm.me> - 0.0.37-1
- Initial RPM packaging of rpcs3
