# With _package_note_file enabled, the editor fails to link (RPM_ARCH not defined)
%undefine _package_note_file
%global debug_package %{nil}

%global godot_ref gdre-wb-f964fa714f5
%global godot_commit 850c331d6f9f379c2c69a77f22701918271a6fe6
%ifarch aarch64
%global godot_arch arm64
%else
%global godot_arch %{_target_cpu}
%endif

Name:           gdsdecomp
Version:        2.7.4
Release:        1%{?dist}
Summary:        Godot reverse engineering tools (GDRE Tools)
License:        MIT AND AML-glslang AND Apache-2.0 AND BSD-2-Clause AND BSD-3-Clause AND BSL-1.0 AND CC0-1.0 AND CC-BY-4.0 AND MPL-2.0 AND OFL-1.1 AND Unlicense AND X11 AND Zlib
URL:            https://github.com/GDRETools/gdsdecomp
Source0:        https://github.com/nikitalita/godot/archive/%{godot_commit}/godot-%{godot_commit}.tar.gz
Source1:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz

ExclusiveArch:  aarch64 x86_64

BuildRequires:  gcc-c++
BuildRequires:  python3-scons
BuildRequires:  cargo
BuildRequires:  rust
BuildRequires:  dotnet-sdk-10.0
BuildRequires:  clang
BuildRequires:  lld
BuildRequires:  desktop-file-utils
BuildRequires:  miniupnpc-devel
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(dbus-1)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
BuildRequires:  pkgconfig(gl)
BuildRequires:  pkgconfig(graphite2)
BuildRequires:  pkgconfig(icu-i18n)
BuildRequires:  pkgconfig(icu-uc)
BuildRequires:  pkgconfig(libbrotlicommon)
BuildRequires:  pkgconfig(libbrotlidec)
BuildRequires:  pkgconfig(libdecor-0)
BuildRequires:  pkgconfig(libpcre2-32)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libpulse)
BuildRequires:  pkgconfig(libturbojpeg)
BuildRequires:  pkgconfig(libudev)
BuildRequires:  pkgconfig(libwslay)
BuildRequires:  pkgconfig(libzstd)
BuildRequires:  pkgconfig(openxr)
BuildRequires:  pkgconfig(sdl3)
BuildRequires:  pkgconfig(speech-dispatcher)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-cursor)
BuildRequires:  pkgconfig(wayland-egl)
BuildRequires:  pkgconfig(x11)
BuildRequires:  pkgconfig(xcursor)
BuildRequires:  pkgconfig(xext)
BuildRequires:  pkgconfig(xi)
BuildRequires:  pkgconfig(xinerama)
BuildRequires:  pkgconfig(xkbcommon)
BuildRequires:  pkgconfig(xrandr)
BuildRequires:  pkgconfig(xrender)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  embree-devel >= 4

Requires:       hicolor-icon-theme

%description
Reverse engineering tools for Godot Engine games: PCK/APK extraction,
GDScript decompilation, resource conversion and full project recovery.

%prep
%setup -q -n godot-%{godot_commit} -a1
mv %{name}-%{version} modules/gdsdecomp
patch -p1 < modules/gdsdecomp/patches/main-cli-parse-inject.patch
sed -i 's/version_info = "unknown"/version_info = "%{version}"/' modules/gdsdecomp/build/versioning.py

%build
# gdsdecomp includes bundled libogg, libtheora, libvorbis, libwebp and mbedtls headers directly
to_unbundle="brotli embree freetype graphite icu4c libjpeg_turbo libpng miniupnpc openxr pcre2 sdl wslay zlib zstd"
system_libs="use_sowrap=no "
rm -rf thirdparty/linuxbsd_headers
for lib in $to_unbundle; do
    system_libs+="builtin_"$lib"=no "
    rm -rf thirdparty/$lib
done

export BUILD_NAME="fedora"
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_NOLOGO=1
scons %{?_smp_mflags} "CCFLAGS=%{?build_cflags}" "LINKFLAGS=%{?build_ldflags}" \
    arch=%{godot_arch} $system_libs use_static_cpp=no progress=no \
    p=linuxbsd target=editor production=yes debug_symbols=no \
    ignore_godot_branch_check=yes module_text_server_fb_enabled=yes \
    minizip=yes deprecated=yes accesskit=no

export HOME=$PWD/.home XDG_CONFIG_HOME=$PWD/.home/.config XDG_DATA_HOME=$PWD/.home/.local/share XDG_CACHE_HOME=$PWD/.home/.cache
godot=$PWD/bin/godot.linuxbsd.editor.%{godot_arch}
$godot --headless --path modules/gdsdecomp/standalone --import
$godot --headless --path modules/gdsdecomp/standalone --export-pack "Linux/X11" $PWD/bin/gdre_tools.pck

%install
install -Dm755 bin/godot.linuxbsd.editor.%{godot_arch} %{buildroot}%{_libdir}/%{name}/gdre_tools
install -m755 bin/libGodotMonoDecompNativeAOT.so %{buildroot}%{_libdir}/%{name}/
install -m644 bin/gdre_tools.pck %{buildroot}%{_libdir}/%{name}/
install -d %{buildroot}%{_bindir}
ln -s ../%{_lib}/%{name}/gdre_tools %{buildroot}%{_bindir}/gdre_tools
install -Dm644 modules/gdsdecomp/standalone/gdre_icon.svg %{buildroot}%{_datadir}/icons/hicolor/scalable/apps/gdre_tools.svg

cat > gdre_tools.desktop <<'DESKTOP'
[Desktop Entry]
Type=Application
Name=GDRE Tools
Comment=Godot reverse engineering tools
Exec=gdre_tools
Icon=gdre_tools
Categories=Development;
DESKTOP
desktop-file-install --dir=%{buildroot}%{_datadir}/applications gdre_tools.desktop

%files
%license modules/gdsdecomp/LICENSE LICENSE.txt COPYRIGHT.txt
%doc modules/gdsdecomp/README.md
%{_bindir}/gdre_tools
%{_libdir}/%{name}/
%{_datadir}/applications/gdre_tools.desktop
%{_datadir}/icons/hicolor/scalable/apps/gdre_tools.svg

%changelog
* Thu Oct 29 2026 Lachlan Marie <lchlnm@pm.me> - 2.7.4-1
- Initial package
