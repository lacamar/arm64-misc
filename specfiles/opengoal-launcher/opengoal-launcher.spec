%global tag 2.11.1
%global bumpver 1
%global commit 7e1c23b495f2e15dbe61e4c0ef938be4ca47b4bf
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

%global debug_package %{nil}
%global appid OpenGOAL-Launcher

Name:           opengoal-launcher
Version:        %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:        2%{?dist}
Summary:        Launcher for OpenGOAL (Jak and Daxter trilogy PC port)
License:        ISC
URL:            https://github.com/open-goal/launcher
Source0:        %{url}/archive/%{commit}/launcher-%{commit}.tar.gz
# Use system opengoal tooling, hide x86 downloads, native wayland for gk
Patch0:         0001-linux-aarch64.patch

ExclusiveArch:  aarch64

BuildRequires:  cargo
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  rust
BuildRequires:  nodejs-npm
BuildRequires:  pkgconfig(webkit2gtk-4.1)
BuildRequires:  pkgconfig(gtk+-3.0)
BuildRequires:  pkgconfig(libsoup-3.0)
BuildRequires:  pkgconfig(openssl)
BuildRequires:  pkgconfig(librsvg-2.0)
BuildRequires:  desktop-file-utils

Requires:       opengoal
Requires:       webkit2gtk4.1

%description
Official launcher for OpenGOAL. Uses the system opengoal package as its
tooling version.

%prep
%autosetup -n launcher-%{commit} -p1

%build
npm install --no-save --prefix .yarnbin yarn@1
export PATH=$PWD/.yarnbin/node_modules/.bin:$PATH YARN_CACHE_FOLDER=$PWD/.yarn-cache
yarn install --frozen-lockfile
yarn tauri build --no-bundle

%install
install -Dpm0755 src-tauri/target/release/%{appid} %{buildroot}%{_bindir}/%{name}
for s in 32 128; do
  install -Dpm0644 src-tauri/icons/${s}x${s}.png %{buildroot}%{_datadir}/icons/hicolor/${s}x${s}/apps/%{appid}.png
done
install -Dpm0644 src-tauri/icons/128x128@2x.png %{buildroot}%{_datadir}/icons/hicolor/256x256/apps/%{appid}.png
install -Dpm0644 src-tauri/icons/icon.png %{buildroot}%{_datadir}/icons/hicolor/512x512/apps/%{appid}.png
install -dm0755 %{buildroot}%{_datadir}/applications
cat > %{buildroot}%{_datadir}/applications/%{appid}.desktop <<EOF
[Desktop Entry]
Type=Application
Name=OpenGOAL Launcher
Comment=%{summary}
Exec=%{name}
Icon=%{appid}
Categories=Game;
StartupWMClass=%{appid}
EOF
desktop-file-validate %{buildroot}%{_datadir}/applications/%{appid}.desktop

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_datadir}/applications/%{appid}.desktop
%{_datadir}/icons/hicolor/*/apps/%{appid}.png

%changelog
* Mon Oct 05 2026 Lachlan Marie <lchlnm@pm.me> - 2.11.1^1.git.7e1c23b-2
- Bootstrap yarn via npm

* Mon Oct 05 2026 Lachlan Marie <lchlnm@pm.me> - 2.11.1^1.git.7e1c23b-1
- Initial package
- Use system opengoal tooling
- Native wayland for gk
