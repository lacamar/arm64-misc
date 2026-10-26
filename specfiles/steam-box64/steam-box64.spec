Name:           steam-box64
Version:        0
Release:        1%{?dist}
Summary:        Steam wrapper running x86 Steam via box64 on Fedora Asahi Remix

License:        MIT
URL:            https://github.com/lacamar/arm64-misc
Source0:        steam-box64
Source1:        steam-muvm
Source2:        box64-binfmt
Source3:        binfmt-dispatcher.toml
Source4:        wine-ec
Source5:        compatibilitytool.vdf
Source6:        toolmanifest.vdf
Source7:        steam.reg
Source8:        realign.py
Source9:        steam-box64.desktop
Source10:       steam-box64.svg
Source11:       LICENSE

BuildArch:      noarch

BuildRequires:  desktop-file-utils

Requires:       bash
Requires:       binfmt-dispatcher
# needs box64 d58d619 or later; plain box64 1:0.4.5.1 predates it
Requires:       box64-asahi > 1:0.4.5.1
Requires:       bubblewrap
Requires:       curl
Requires:       hicolor-icon-theme
Requires:       iproute
Requires:       muvm
Requires:       python3
Requires:       tar
Requires:       util-linux-core
Requires:       xz
Requires:       zenity

%description
This package provides a wrapper to download, install and run x86 Steam on
Fedora Asahi Remix through box64 on the host, without muvm. It also provides
steam-muvm, a launch option that runs a game in muvm with Steam DRM working,
and a "Wine (arm64ec)" compatibility tool using the system wine.

%prep
%autosetup -c -T
cp -p %{SOURCE11} .

%build

%install
install -Dpm0755 -t %{buildroot}%{_bindir} %{SOURCE0} %{SOURCE1}
install -Dpm0755 -t %{buildroot}%{_libexecdir}/%{name} %{SOURCE2}
install -Dpm0644 -t %{buildroot}%{_datadir}/%{name}/binfmt-dispatcher %{SOURCE3}
install -Dpm0755 -t %{buildroot}%{_datadir}/steam/compatibilitytools.d/wine-ec %{SOURCE4}
install -Dpm0644 -t %{buildroot}%{_datadir}/steam/compatibilitytools.d/wine-ec \
  %{SOURCE5} %{SOURCE6} %{SOURCE7} %{SOURCE8}
desktop-file-install --dir=%{buildroot}%{_datadir}/applications %{SOURCE9}
install -Dpm0644 -t %{buildroot}%{_datadir}/icons/hicolor/scalable/apps %{SOURCE10}

%files
%license LICENSE
%{_bindir}/steam-box64
%{_bindir}/steam-muvm
%{_libexecdir}/%{name}
%{_datadir}/%{name}
%dir %{_datadir}/steam
%dir %{_datadir}/steam/compatibilitytools.d
%{_datadir}/steam/compatibilitytools.d/wine-ec
%{_datadir}/applications/steam-box64.desktop
%{_datadir}/icons/hicolor/scalable/apps/steam-box64.svg

%changelog
* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0-1
- Initial package, based on @asahi/steam 0-14
- Run x86 Steam on the host via box64 instead of muvm/FEX
- Add steam-muvm launch option and Wine (arm64ec) compat tool
