%global tag 0.3.9
%global bumpver 0
%global commit 32c3cf73970f885c0a588623208232db72a74a58
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

%global toolchain clang
%global debug_package %{nil}
%undefine _auto_set_build_flags

Name:           opengoal
Version:        %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:        1%{?dist}
Summary:        Native PC port of the Jak and Daxter trilogy (GOAL compiler, runtime, decompiler)
License:        ISC
URL:            https://github.com/open-goal/jak-project
Source0:        %{url}/archive/%{commit}/jak-project-%{commit}.tar.gz
# Linux aarch64 build fixes on top of the upstream arm64 backend
Patch0:         0001-native-linux-aarch64.patch

ExclusiveArch:  aarch64

BuildRequires:  clang
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  openssl-devel
BuildRequires:  mesa-libGL-devel
BuildRequires:  mesa-libEGL-devel
BuildRequires:  wayland-devel
BuildRequires:  wayland-protocols-devel
BuildRequires:  libxkbcommon-devel
BuildRequires:  libdecor-devel
BuildRequires:  libX11-devel
BuildRequires:  libXext-devel
BuildRequires:  libXrandr-devel
BuildRequires:  libXcursor-devel
BuildRequires:  libXi-devel
BuildRequires:  libXfixes-devel
BuildRequires:  libusb1-devel
BuildRequires:  systemd-devel
BuildRequires:  dbus-devel
BuildRequires:  ibus-devel
BuildRequires:  pulseaudio-libs-devel
BuildRequires:  alsa-lib-devel

Recommends:     opengoal-launcher

%description
OpenGOAL: a native port of Jak and Daxter, Jak II and Jak 3. Contains the
GOAL compiler (goalc), the game runtime (gk) and the extractor, laid out as a
launcher tooling version in %{_libdir}/%{name}. Requires your own game discs.

%prep
%autosetup -n jak-project-%{commit} -p1
# Fedora ships no static OpenSSL
sed -i '/set(OPENSSL_USE_STATIC_LIBS TRUE)/d' CMakeLists.txt

%build
cmake -B build -G Ninja \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_C_COMPILER=clang \
    -DCMAKE_CXX_COMPILER=clang++ \
    -DSTATICALLY_LINK=ON
cmake --build build --target gk goalc extractor

%install
.github/scripts/releases/extract_build_unix.sh %{buildroot}%{_libdir}/%{name} build .
echo v%{tag} > %{buildroot}%{_libdir}/%{name}/VERSION

%files
%license LICENSE
%doc README.md
%{_libdir}/%{name}

%changelog
* Sat Oct 17 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.9^0.git.32c3cf7-1
- Update to 0.3.9

* Mon Oct 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.8^3.git.efb21c3-1
- Initial package
- Native Linux aarch64 build
