%global bumpver 20

%global tag 0.0.43
%global commit df090aa12797b5c5f4a6f2567f1578ec3e85409d
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:       rpcs3-git
Version:    %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:    1%{dist}
Summary:    PlayStation 3 emulator and debugger

Conflicts:      rpcs3
Provides:       rpcs3

License:  GPLv2
URL:      https://github.com/RPCS3/rpcs3
Source0:  https://github.com/RPCS3/rpcs3/archive/%{commit}/rpcs3-%{shortcommit}.tar.gz

%{lua:
local externals = {
 { name="7zip", ref="f9d78af", owner="ip7z", path="7zip/7zip", version="26.02",  license="GNU-LGPL" },
 { name="FAudio", ref="c54eb8f", owner="FNA-XNA", path="FAudio", version="26.08",  license="zlib" },
 { name="VulkanMemoryAllocator", ref="1d8f600", owner="GPUOpen-LibrariesAndSDKs", path="GPUOpen/VulkanMemoryAllocator", version="3.3.0",  license="MIT" },
 { name="openal-soft", ref="b2c48f7", owner="kcat", path="OpenAL/openal-soft", version="1.25.2",  license="PFFFT" },
 { name="soundtouch", ref="a0fba77", owner="RPCS3", path="SoundTouch/soundtouch/", version="2.4.1",  license="LGPLv2.1" },
 { name="asmjit", ref="416f735", owner="asmjit", path="asmjit/asmjit/", license="zlib" },
 { name="cubeb", ref="4848575", owner="mozilla", path="cubeb/cubeb", version="2026.01.22", license="ISC" },
 { name="discord-rpc", ref="3dc2c32", owner="Vestrel", path="discord-rpc/discord-rpc", license="MIT" },
 { name="gamemode", ref="c54d6d4", owner="FeralInteractive", path="feralinteractive/feralinteractive", version="1.8.2", license="BSD-3-Clause" },
 { name="Fusion", ref="015d684", owner="xioTechnologies", path="fusion/fusion", version="1.3.2",  license="MIT" },
 { name="glslang", ref="f0bd025", owner="KhronosGroup", path="glslang/glslang", version="16.2.0",  license="BSD-3-Clause" },
 { name="hidapi", ref="d6b2a97", owner="RPCS3", path="hidapi/hidapi", version="0.15.0",  license="GPLv3, BSD" },
 { name="libpng", ref="3061454", owner="pnggroup", path="libpng/libpng", version="1.6.58",  license="PNGRLLv2" },
 { name="libusb", ref="87a5563", owner="libusb", path="libusb/libusb", version="1.0.30",  license="LGPLv2.1" },
 { name="miniupnp", ref="d66872e", owner="miniupnp", path="miniupnp/miniupnp", version="2.3.9",  license="BSD-3-Clause" },
 { name="protobuf", ref="edaa823", owner="protocolbuffers", path="protobuf/protobuf", version="33.4",  license="BSD-3-Clause" },
 { name="pugixml", ref="c8033ce", owner="zeux", path="pugixml", version="1.16",  license="MIT" },
 { name="rtmidi", ref="1e5b499", owner="thestk", path="rtmidi", version="6.0.0",  license="MIT" },
 { name="stb", ref="013ac3b", owner="nothings", path="stblib/stb", license="MIT" },
 { name="wolfssl", ref="ac01707", owner="wolfSSL", path="wolfssl/wolfssl", version="5.9.2",  license="GPLv3" },
 { name="yaml-cpp", ref="51a5d62", owner="RPCS3", path="yaml-cpp/yaml-cpp", version="0.9.0",  license="MIT" },
}

for i, s in ipairs(externals) do
  print(string.format("Source%d: https://github.com/%s/%s/archive/%s/%s-%s.tar.gz", 100 + i, s.owner, s.name, s.ref, s.name, s.ref).."\n")
  print(string.format("Provides: bundled(%s) = %s", s.name, (s.version or "0")).."\n")
end

function print_setup_externals()
  for i, s in ipairs(externals) do
    print(string.format("mkdir -p 3rdparty/%s", s.path).."\n")
    print(string.format("tar -xzf %s --strip-components=1 -C 3rdparty/%s", rpm.expand("%{SOURCE"..(100 + i).."}"), s.path).."\n")
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
BuildRequires:  libxkbcommon-x11-devel

%if 0%{?fedora} <= 44
BuildRequires:  rtmidi-devel
%endif

BuildRequires:  alsa-lib-devel
BuildRequires:  libatomic
BuildRequires:  libevdev-devel
BuildRequires:  qt6-qtbase-private-devel
BuildRequires:  pipewire-jack-audio-connection-kit-devel
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

cmake -B build -G Ninja \
      -Wno-dev \
      -DCMAKE_BUILD_TYPE=Release \
      -DLLVM_TARGETS_TO_BUILD=AArch64 \
      -DCMAKE_EXE_LINKER_FLAGS="-L/usr/lib64/pipewire-0.3/jack" \
      -DCMAKE_MODULE_LINKER_FLAGS="-fuse-ld=gold" \
      -DCMAKE_SHARED_LINKER_FLAGS="-fuse-ld=gold" \
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
      -DSTATIC_LINK_LLVM=ON
%ninja_build -C build


%install
%ninja_install -C build


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
* Sat Oct 31 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^20.git.df090aa-1
- Update to commit df090aa12797b5c5f4a6f2567f1578ec3e85409d

* Fri Oct 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^19.git.8e26652-1
- Update to commit 8e26652c85bb5658965fa5731d9a0309ca10b42b

* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^18.git.6c44fff-1
- Update to commit 6c44fff7549e941389a4ce072a95c5ff9db7237c

* Wed Oct 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^17.git.744126c-1
- Update to commit 744126caff4daf91d31ae81fc5ab19ff65f87b32

* Tue Oct 27 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^16.git.c365ea7-1
- Update to commit c365ea76a552961ff078ea1a46da9d4b07729674

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^15.git.e8979d3-1
- Update to commit e8979d31b3a22c8bc9a6eae6bdc31756eac8ee89

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^14.git.d00d802-1
- Update to commit d00d80231af3f9b0286f38fd72f7513583f1a9d4

* Sat Oct 24 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^13.git.46b7fb6-1
- Update to commit 46b7fb670b280d08036c7670270b713daef912c2

* Sat Oct 24 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^12.git.aa9ebd2-1
- Update to commit aa9ebd2f8643d28e592169fffbb76e379c6d7620

* Thu Oct 22 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^11.git.e53ac18-1
- Update to commit e53ac18f8ddd4cfd0e92a57d15740d4170c1e744

* Wed Oct 21 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^10.git.4024ea3-1
- Update to commit 4024ea31e049f3205ae406eb3f37fe7625e1bc98

* Tue Oct 20 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^9.git.3284e84-1
- Update to commit 3284e84abaac91516b180413136373ff6af58b5b

* Mon Oct 19 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^8.git.bd179ff-1
 - Update to commit bd179ffd2329f70de6949247aadfc2e7c9f621e1

* Sat Oct 17 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^7.git.8b76207-1
 - Update to commit 8b76207aa888a283a9fe75c56517cc854972af59

* Sat Oct 17 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^6.git.3beb650-1
- Update to commit 3beb6504de8d81b1d3cb6291cdd35dccea077907

* Fri Oct 16 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^5.git.a710aba-1
- Update to commit a710aba42f6c5b323d507a4818c1837ce6d5dc35

* Fri Oct 16 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^4.git.f94e9f8-1
- Update to commit f94e9f8647aeae07ea064dbafe407a41a922f485

* Fri Oct 16 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^3.git.17543d2-1
- Update to commit 17543d27371d0c4fb20b14ef671bd31c213d406b

* Sun Oct 11 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^2.git.2ba2f75-1
- Update to commit 2ba2f75bcea7ef6bdd687046c7fcfb790faf9853

* Sat Oct 10 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^1.git.8f2fe1a-1
- Update to commit 8f2fe1a99caef5d6e1eb9e4579f1d6169cf4b771

* Thu Oct 08 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.43^0.git.304d544-1
- Update to 0.0.43

* Tue Sep 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.42^36.git.3e9d881-1
- Update to commit 3e9d881aa681f4ade80f86e9ff7fba73d5098a9b

* Tue Sep 29 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.42^35.git.1707d7f-1
- Update to commit 1707d7fc883ef48ff21bdcbb0141a3211ae09cb2

* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.42^34.git.1f08048-1
- Update to commit 1f080485b95db2700c5cf244b1314f73b6cf564e

* Sun Sep 27 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.42^33.git.3fa07db-1
- Update to commit 3fa07db78b44f8705d1ee8cd3f41b42bad725bf7

* Sat Sep 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.0.42^32.git.77cb942-1
- Update to commit 77cb9423dbf3406c0b7ecf0ca73f773d7185f9a0
