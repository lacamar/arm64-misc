%global bumpver 38

%global commit b8c995cbb4f02826057d0f5b34112fdd8a645511
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:       xray-16
Version:        2921.2025.1
Release:    3%{?dist}
Summary:    Open Source XRay engine for S.T.A.L.K.E.R.

License:    MIT License
URL:        https://github.com/OpenXRay/xray-16
Source0:    https://github.com/OpenXRay/xray-16/archive/%{shortcommit}/xray-16-%{shortcommit}.tar.gz

%{lua:
local externals = {
  { name="AGS_SDK", ref="5d8812d", owner="GPUOpen-LibrariesAndSDKs", path="AGS_SDK", version="6.3.0",  license="AMD" },
  { name="GameSpy", ref="3e43480", owner="OpenXRay", path="GameSpy",  license="IGN" },
  { name="LuaJIT", ref="5a5cd82", owner="OpenXRay", path="LuaJIT", version="2.1",  license="MIT" },
  { name="gli", ref="779b99a", owner="g-truc", path="gli", version="0.8.2.0",  license="MIT" },
  { name="imgui", ref="3fb22b8", owner="ocornut", path="imgui", version="v.1.92.5",  license="MIT" },
  { name="luabind-deboostified", ref="8da131b", owner="OpenXRay", path="luabind", version="0.9",  license="MIT" },
  { name="sse2neon", ref="3b70b37", owner="DLTcollab", path="sse2neon", version="1.8.0",  license="MIT" },
  { name="sse2rvv", ref="f1ab916", owner="pattonkan", path="sse2rvv", version="git",  license="MIT" },
  { name="xrLuaFix", ref="0e89050", owner="OpenXRay", path="xrLuaFix", version="git",  license="BSD-3" },
  { name="jenkins-ctest-plugin", ref="63a4a82", owner="rpavlik", path="luabind/test/jenkins-ctest-plugin", version="git",  license="MIT" },
  { name="luafilesystem", ref="314c0d0", owner="OpenXRay", path="xrLuaFix/lfs", version="git",  license="MIT" },
  { name="lua-marshal", ref="983a3bf", owner="OpenXRay", path="xrLuaFix/lua-marshal", version="git",  license="MIT" },
  { name="lua-pack", ref="c1e5a14", owner="OpenXRay", path="xrLuaFix/lua-pack", version="2.0.0",  license="MIT" },
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
    print(string.format("mkdir -p Externals/%s", (s.path or s.name)).."\n")
    print(string.format("tar -xzf %s --strip-components=1 -C Externals/%s", rpm.expand("%{SOURCE"..si.."}"), (s.path or s.name)).."\n")
    ::continue2::
  end
end
}

BuildRequires:  git
BuildRequires:  cmake
BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  openal-soft-devel
BuildRequires:  cryptopp-devel
BuildRequires:  openal-soft-devel
BuildRequires:  SDL2-devel
BuildRequires:  libjpeg-turbo-devel
BuildRequires:  mimalloc-devel
BuildRequires:  libvorbis-devel
BuildRequires:  libtheora-devel
BuildRequires:  libogg-devel
BuildRequires:  lzo-devel


%description
Improved version of the X-Ray Engine, the game engine used in the world-famous S.T.A.L.K.E.R. game series by GSC Game World. Join OpenXRay!

%prep
%autosetup -n xray-16-%{commit}

%{lua: print_setup_externals()}


%build
%set_build_flags
export CXXFLAGS="%{build_cxxflags} -Wno-error=overloaded-virtual"
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo
%cmake_build

%install
%cmake_install


%files

%license License.txt
%doc README.md

%{_bindir}/xr_3da

%{_datadir}/applications/openxray_*.desktop
%{_datadir}/pixmaps/openxray_*.png
%{_datadir}/icons/hicolor/*/apps/openxray_*.png

%{_datadir}/bash-completion/completions/xr_3da

%{_libdir}/xr*.so

%dir %{_datadir}/openxray
%{_datadir}/openxray/*

%changelog
* Sat Sep 26 2026 Lachlan Marie <lchlnm@pm.me> - 2921.2025.1-3
 - Update to commit b8c995cbb4f02826057d0f5b34112fdd8a645511

* Sat Sep 26 2026 Lachlan Marie <lchlnm@pm.me> - 2921.2025.1-3
 - Update to commit eda9503dd4056e52fa9cee58dfae53f530cd5b9a

* Tue Sep 22 2026 Lachlan Marie <lchlnm@pm.me> - 2921.2025.1-3
 - Update to commit a7055a4b9583d0111ea4026313e1b5a3828d7b4d

* Mon Sep 21 2026 Lachlan Marie <lchlnm@pm.me> - 2921.2025.1-3
 - Update to 2921.2025.1

* Sun Sep 20 2026 Lachlan Marie <lchlnm@pm.me> - git^35.git.247d727-3
 - Update to commit 247d72764eb7ec33cbaf02d59786617ab63751fd

* Fri Sep 18 2026 Lachlan Marie <lchlnm@pm.me> - git^34.git.42e6641-3
 - Update to commit 42e6641258603a6605d8d9a16cdc44b4d86fb8b7

* Thu Jul 09 2026 Lachlan Marie <lchlnm@pm.me> - git^33.git.29030f8-3
 - Update to commit 29030f81b137f6ea5365b3d71f2b588490832f5b

* Fri May 08 2026 Lachlan Marie <lchlnm@pm.me> - git^32.git.11b8c4e-3
 - Update to commit 11b8c4ecac4f249cf8b856389bd722cb421df787

* Wed Apr 01 2026 Lachlan Marie <lchlnm@pm.me> - git^31.git.7368d4b-3
 - Update to commit 7368d4b0ec7dabad6f7108655d66cfbe34d5364c

* Tue Mar 31 2026 Lachlan Marie <lchlnm@pm.me> - git^30.git.c2b9a28-3
 - Update to commit c2b9a28649120fd527a6863800f1b9f7560b58cf

* Mon Mar 16 2026 Lachlan Marie <lchlnm@pm.me> - git^29.git.3526a63-3
 - Update to commit 3526a63218498b2ea7fb761d43ebc0b751f9d8bc

* Wed Mar 11 2026 Lachlan Marie <lchlnm@pm.me> - git^28.git.5f16507-3
 - Update to commit 5f16507038ab05c7fd9bdcdad8fe7a38357cff44

* Sat Mar 07 2026 Lachlan Marie <lchlnm@pm.me> - git^27.git.ef47a17-3
 - Update to commit ef47a17b7d444c92fb216b7565c6d4f47e6dbca2

* Sun Mar 01 2026 Lachlan Marie <lchlnm@pm.me> - git^26.git.564b340-3
 - Update to commit 564b340f23ab728bc8416380cd9cac4152bbe2ad

* Sat Feb 28 2026 Lachlan Marie <lchlnm@pm.me> - git^25.git.4c22279-3
 - Update to commit 4c22279821da375c61c84e76e45a52d6a5d3b19f

* Tue Jan 13 2026 Lachlan Marie <lchlnm@pm.me> - git^24.git.ffdf858-3
 - Update to commit ffdf858645d179186d84244dfe18556297cf3bad

* Mon Dec 29 2025 Lachlan Marie <lchlnm@pm.me> - git^23.git.83e0253-3
 - Update to commit 83e025372bfc92c628a83ff341156146b8183e15

* Mon Dec 29 2025 Lachlan Marie <lchlnm@pm.me> - git^22.git.0ed3e8f-3
 - Update to commit 0ed3e8f9220d7a71bdcd53798647c3cf78c7ee56

* Sun Dec 28 2025 Lachlan Marie <lchlnm@pm.me> - git^21.git.1881ea9-3
 - Update to commit 1881ea90030f797f715f20698e95090fc914d2db

* Sat Dec 27 2025 Lachlan Marie <lchlnm@pm.me> - git^20.git.bf27fba-3
 - Update to commit bf27fba43d15ee5df042c6a2c1d7d375de197a08

* Thu Dec 25 2025 Lachlan Marie <lchlnm@pm.me> - git^19.git.dc3c07a-3
 - Update to commit dc3c07ac29550e5c3c64c09975131f7e153d32a2

* Thu Dec 25 2025 Lachlan Marie <lchlnm@pm.me> - git^18.git.8907fb9-3
 - Update to commit 8907fb958b038f45f1eac719455c77ea2ef6d368

* Wed Dec 24 2025 Lachlan Marie <lchlnm@pm.me> - git^17.git.57a8246-3
 - Update to commit 57a82460278a4f42b4a64273b87abe174ac17731

* Mon Dec 22 2025 Lachlan Marie <lchlnm@pm.me> - git^16.git.5c4a40f-3
 - Update to commit 5c4a40fd9fce9e6c3469506442fefe2bb37e707d

* Sun Dec 21 2025 Lachlan Marie <lchlnm@pm.me> - git^15.git.75f99a7-3
 - Update to commit 75f99a7db0d1eb17ad53c83263cedb71b8ec278f

* Sat Dec 20 2025 Lachlan Marie <lchlnm@pm.me> - git^14.git.5fa524d-3
 - Update to commit 5fa524ddc1dafbbdca8a4774a8af2562121e4423

* Tue Dec 16 2025 Lachlan Marie <lchlnm@pm.me> - git^13.git.bf1c14f-3
 - Update to commit bf1c14f0fe1670766008e57b0db188e78541f052

* Tue Dec 16 2025 Lachlan Marie <lchlnm@pm.me> - git^12.git.db06c3b-3
 - Update to commit db06c3ba7d19d9cb9379a10141a8d2e0fdfd4770

* Sun Dec 14 2025 Lachlan Marie <lchlnm@pm.me> - git^11.git.debb091-3
 - Update to commit debb0911206e4090ee984528bdf4e1baef7fcf99

* Thu Dec 04 2025 Lachlan Marie <lchlnm@pm.me> - git^10.git.bb6b153-3
 - Update to commit bb6b1539a0d31a8ee48ed7a75d2c593ae62b2db3

* Fri Nov 21 2025 Lachlan Marie <lchlnm@pm.me> - git^9.git.831186f-3
- Shortened commit length in xray source URL.

* Thu Nov 06 2025 Lachlan Marie <lchlnm@pm.me> - git^2.git.9f0475d-2
- Updated xray-16 git commit

* Wed Nov 05 2025 Lachlan Marie <lchlnm@pm.me> - git^1.git.0ed27d4-2
- Updated xray-16 git commit

* Wed Nov 05 2025 Lachlan Marie <lchlnm@pm.me> - git^0.git.55a888c-2
- Changed to spec to follow git commits

* Fri Jul 25 2025 Lachlan Marie <lchlnm@pm.me> - git-1
- Initial RPM packaging of OpenXRay
