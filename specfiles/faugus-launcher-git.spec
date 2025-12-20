%global bumpver 7
%global _name faugus-launcher

%global commit 950240e3b88e8aef46d5fad318f92f1a6e61c414
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:           faugus-launcher-git
Conflicts:      faugus-launcher
Provides:       faugus-launcher
Version:        1.11.7%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:        1%{?dist}
Summary:        A simple and lightweight app for running Windows games using UMU-Launcher

License:        MIT
URL:            https://github.com/Faugus/%{_name}
Source0:        https://github.com/Faugus/%{_name}/archive/%{shortcommit}/%{_name}-%{shortcommit}.tar.gz

BuildArch:      noarch
BuildRequires:  meson gtk-update-icon-cache
Requires:       python3
Requires:       python3-gobject
Requires:       python3-requests
Requires:       python3-icoextract
Requires:       python3-pillow
Requires:       python3-filelock
Requires:       python3-vdf
Requires:       python3-psutil
Requires:       umu-launcher
Requires:       ImageMagick
Requires:       libayatana-appindicator-gtk3
Requires:       mangohud
Requires:       gamemode

%description
A simple and lightweight app for running Windows games using UMU-Launcher/UMU-Proton.

%prep
%autosetup -n %{_name}-%{commit}

%build
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%{_bindir}/faugus-launcher
%{_bindir}/faugus-run
%{_bindir}/faugus-proton-manager
%{_bindir}/faugus-components
%{_bindir}/faugus-proton-downloader
%{_datadir}/applications/*.desktop
%{_datadir}/icons/hicolor/256x256/apps/*.png
%{_datadir}/icons/hicolor/256x256/apps/faugus-mono.svg
%{_datadir}/icons/hicolor/scalable/actions/*.svg
%{_datadir}/faugus-launcher/*
%{_datadir}/locale/*/LC_MESSAGES/*.mo
%{_datadir}/metainfo/faugus-launcher.metainfo.xml
%{_datadir}/licenses/faugus-launcher/LICENSE

%changelog
* Sun Dec 21 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.7^7.git.950240e-1
 - Update to commit 950240e3b88e8aef46d5fad318f92f1a6e61c414

* Fri Dec 19 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.6^6.git.791896e-1
 - Update to commit 791896e5245d37e64eee05d844fc3a605d71f109

* Fri Dec 19 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.6^5.git.b7bd230-1
 - Update to commit b7bd230a84d199b8bfcda6f87992ced231c1f6e9

* Thu Dec 18 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.5^4.git.80d5545-1
 - Update to commit 80d5545aafb597334533ebaf23ae4c413abe94fc

* Tue Dec 16 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.4^3.git.35a8c76-1
 - Update to commit 35a8c76963fd5ebf4e5a4f2528a8d8906ee2fbbf

* Sun Dec 14 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.3^2.git.34fa1fd-1
 - Update to commit 34fa1fd977191d7d6b7f6f58d015c92f3a36ac12

* Sun Dec 14 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.3^1.git.2482afe-1
 - Update to commit 2482afe5fdcce4ea72eac852ce38675b055396ae

* Thu Dec 11 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.1^3.git.10e4718-1
 - Update to commit 10e471840ca2014d3664d02426f73d9ca562d584

* Tue Dec 09 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.1^2.git.7c86c8e-1
 - Update to commit 7c86c8e51d4991c18671bf0196c13f284fbe4014

* Mon Dec 08 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.1^1.git.c9a1e1e-1
 - Update to commit c9a1e1e99c14e22ff5d86c9a9dbba32188609578

* Sun Dec 07 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.1^0.git.3b962c6-1
 - Adapted specfile from faugus copr
 - Changed build from project git commits
 - Update to commit 3b962c60c9b5e6be38d60644f1a0c8020d89b121
