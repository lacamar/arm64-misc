%global objc_commit a1faad66cee79f29c4ca268b004111edc33a2ae2
%global make_commit d0349cc83a23367acdc53df364f73504c281b26c
%global base_commit 3d7013e144b153abcd6c088dc8d6c64ebd43bc4b
%global toolchain clang
%global privlib %{_libdir}/%{name}
%global __provides_exclude_from ^%{privlib}/.*$
%global __requires_exclude ^lib(objc|gnustep-base)\\.so.*$

Name:           mil-hwx-compiler
Version:        0.3.4
Release:        1%{?dist}
Summary:        Core ML MIL to Apple Neural Engine program compiler
License:        MIT AND LGPL-2.1-or-later
URL:            https://github.com/joshuaswarren/mil-hwx-compiler
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        https://github.com/gnustep/libobjc2/archive/%{objc_commit}/libobjc2-%{objc_commit}.tar.gz
Source2:        https://github.com/gnustep/tools-make/archive/%{make_commit}/tools-make-%{make_commit}.tar.gz
Source3:        https://github.com/gnustep/libs-base/archive/%{base_commit}/libs-base-%{base_commit}.tar.gz
ExclusiveArch:  aarch64

BuildRequires:  clang
BuildRequires:  lld
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  make
BuildRequires:  patchelf
BuildRequires:  python3
BuildRequires:  robin-map-devel
BuildRequires:  pkgconfig(libffi)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(zlib)

Suggests:       omarchy-ane

%description
mil-hwxc compiles textual Core ML MIL into ANEC packages for the H13 (M1)
and H14 (M2) Neural Engine, runnable with omarchy-ane-run.

%prep
%autosetup -n %{name}-%{version}
tar xf %{SOURCE1}
tar xf %{SOURCE2}
tar xf %{SOURCE3}

%build
gs=$PWD/gs
export CC=clang CXX=clang++ OBJC=clang OBJCXX=clang++
export CFLAGS="-O2 -g" CXXFLAGS="-O2 -g" OBJCFLAGS="-O2 -g"
export LDFLAGS="-fuse-ld=lld"
cmake -S libobjc2-%{objc_commit} -B objc-build -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=$gs \
    -DCMAKE_INSTALL_LIBDIR=lib \
    -DTESTS=OFF
cmake --build objc-build %{?_smp_mflags}
cmake --install objc-build
export PATH=$gs/bin:$PATH
export LD_LIBRARY_PATH=$gs/lib
export PKG_CONFIG_PATH=$gs/lib/pkgconfig
export CPPFLAGS="-I$gs/include"
export LDFLAGS="-L$gs/lib -fuse-ld=lld"
(cd tools-make-%{make_commit} && ./configure --prefix=$gs --with-layout=fhs \
    --with-library-combo=ng-gnu-gnu --with-runtime-abi=gnustep-2.0 \
    --enable-objc-arc --enable-native-objc-exceptions && make %{?_smp_mflags} && make install)
export GNUSTEP_CONFIG_FILE=$gs/etc/GNUstep/GNUstep.conf
. $gs/share/GNUstep/Makefiles/GNUstep.sh
(cd libs-base-%{base_commit} && ./configure --prefix=$gs --disable-tls --disable-xslt \
    --disable-zeroconf --disable-libdispatch --disable-nsurlsession && make %{?_smp_mflags} && make install)
make build/mil-hwxc CXX=clang++ GNUSTEP_PREFIX=$gs GNUSTEP_CONFIG=$gs/bin/gnustep-config \
    FRAMEWORKS="$($gs/bin/gnustep-config --base-libs) -fuse-ld=lld -Wl,-rpath,%{privlib}"

%install
install -Dm755 build/mil-hwxc %{buildroot}%{_bindir}/mil-hwxc
install -d %{buildroot}%{privlib}
cp -P gs/lib/libobjc.so.* gs/lib/libgnustep-base.so.* %{buildroot}%{privlib}/
for f in %{buildroot}%{privlib}/*.so.*; do
    [ -L "$f" ] || patchelf --set-rpath %{privlib} "$f"
done
patchelf --set-rpath %{privlib} %{buildroot}%{_bindir}/mil-hwxc

%check
export LD_LIBRARY_PATH=%{buildroot}%{privlib}
python3 tests/test_h14_parity.py build/mil-hwxc
python3 tests/test_h14_fixture_programs.py build/mil-hwxc

%files
%license LICENSE
%doc README.md
%{_bindir}/mil-hwxc
%{privlib}/

%changelog
* Fri Nov 27 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.4-1
- Initial package
