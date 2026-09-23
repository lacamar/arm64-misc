## START: Set by rpmautospec
## (rpmautospec version 0.8.5)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 6;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

%define debug_package %{nil}
Name:           lutris
Version:        0.5.22
Release:        %autorelease
Summary:        Install and play any video game easily

# Automatically converted from old format: GPLv3 - review is highly recommended.
License:        GPL-3.0-only
URL:            http://%{name}.net
Source0:        https://github.com/%{name}/%{name}/archive/refs/tags/v%{version}.tar.gz

# Check for deprecated attributes in GnomeDesktop
# https://github.com/lutris/lutris/pull/6833
Patch0:         6833.patch
Patch1:         system-runtime.patch

BuildRequires:  desktop-file-utils
BuildRequires:  python3-devel
Requires:       cabextract
Requires:       gtk3, psmisc
Requires:       hicolor-icon-theme
# According to the INSTALL.rst upstream docs, lutris requires either (xorg-x11-server-Xephyr, xrandr)
# or gnome-desktop3. Considering we are mainly using Wayland now, gnome-desktop3 should be sufficient.
Requires:       gnome-desktop3
Requires:       python3-distro
Requires:       python3-cairo

# Tests
BuildRequires:  python3dist(pytest)
BuildRequires:  pkgconfig(gdk-3.0)
BuildRequires:  pkgconfig(webkit2gtk-4.1)
BuildRequires:  pkgconfig(py3cairo)
BuildRequires:  libX11-devel

%if 0%{?fedora} || 0%{?rhel} < 10
%ifarch x86_64
Recommends:     mesa-dri-drivers(x86-32)
Recommends:     mesa-vulkan-drivers(x86-32)
Recommends:     vulkan-loader(x86-32)
Recommends:     mesa-libGL(x86-32)
Recommends:     libXScrnSaver(x86-32)
Recommends:     pipewire(x86-32)
Recommends:     libFAudio(x86-32)
Recommends:     wine-pulseaudio(x86-32)
Recommends:     wine-core(x86-32)
%endif
%endif

Requires:       libXScrnSaver
Requires:       mesa-vulkan-drivers
Requires:       mesa-dri-drivers
Requires:       vulkan-loader
Requires:       mesa-libGL
Requires:       glx-utils
Requires:       gvfs
Requires:       webkit2gtk4.1
Requires:       protobuf
Recommends: 	p7zip, curl
Recommends:	fluid-soundfont-gs
Recommends:     wine-core
Recommends:	p7zip-plugins
Recommends:	gamemode
Recommends:     libFAudio
Recommends:     gamescope
BuildRequires:  fdupes
BuildRequires:  libappstream-glib
BuildRequires:  meson, gettext

%description
Lutris is a gaming platform for GNU/Linux. Its goal is to make
gaming on Linux as easy as possible by taking care of installing
and setting up the game for the user. The only thing you have to
do is play the game. It aims to support every game that is playable
on Linux.

%prep
%autosetup -n %{name}-%{version} -p1

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel
%meson
%meson_build

%install
%pyproject_install
%pyproject_save_files lutris
%meson_install
appstream-util validate-relax --nonet %{buildroot}/%{_datadir}/metainfo/net.%{name}.Lutris.metainfo.xml
%fdupes %{buildroot}%{python3_sitelib}
desktop-file-install --dir=%{buildroot}%{_datadir}/applications share/applications/net.%{name}.Lutris.desktop
desktop-file-install --dir=%{buildroot}%{_datadir}/applications share/applications/net.%{name}.Lutris1.desktop
%find_lang %{name} --with-man

%check
# Tests disabled for now. Let's retry next patch.

# Python tests: Disabled because either they are querying hardware (Don't work in mock) or they're
# trying to spawn processes, which is also blocked.
#%%pytest --ignore=tests/test_dialogs.py --ignore=tests/test_installer.py --ignore=tests/test_api.py -k "not GetNvidiaDriverInfo and not GetNvidiaGpuInfo and not import_module and not options"

%files -f %{pyproject_files} -f %{name}.lang
%{_bindir}/%{name}
%{_datadir}/%{name}/
%{_datadir}/applications/net.%{name}.Lutris.desktop
%{_datadir}/applications/net.%{name}.Lutris1.desktop
%{_datadir}/icons/hicolor/scalable/apps/net.lutris.Lutris.svg
%{_datadir}/icons/hicolor/16x16/apps/net.lutris.Lutris.png
%{_datadir}/icons/hicolor/22x22/apps/net.lutris.Lutris.png
%{_datadir}/icons/hicolor/24x24/apps/net.lutris.Lutris.png
%{_datadir}/icons/hicolor/32x32/apps/net.lutris.Lutris.png
%{_datadir}/icons/hicolor/48x48/apps/net.lutris.Lutris.png
%{_datadir}/icons/hicolor/64x64/apps/net.lutris.Lutris.png
%{_datadir}/icons/hicolor/128x128/apps/net.lutris.Lutris.png
%{_datadir}/icons/hicolor/128x128/mimetypes/application-x-lutris.png
%{_datadir}/icons/hicolor/16x16/mimetypes/application-x-lutris.png
%{_datadir}/icons/hicolor/22x22/mimetypes/application-x-lutris.png
%{_datadir}/icons/hicolor/24x24/mimetypes/application-x-lutris.png
%{_datadir}/icons/hicolor/32x32/mimetypes/application-x-lutris.png
%{_datadir}/icons/hicolor/48x48/mimetypes/application-x-lutris.png
%{_datadir}/icons/hicolor/64x64/mimetypes/application-x-lutris.png
%{_datadir}/icons/hicolor/scalable/mimetypes/application-x-lutris.svg
%{_datadir}/mime/packages/application-x-lutris.xml
%{_datadir}/man/man1/%{name}.1.gz
%{_metainfodir}/net.lutris.Lutris.metainfo.xml
%pycached %{python3_sitelib}/%{name}/optional_settings.py

%changelog
## START: Generated by rpmautospec
* Wed Sep 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.5.22-6
- Add system DXVK/VKD3D version using Wine builtins

* Fri Sep 11 2026 Steve Cossette <farchord@gmail.com> - 0.5.22-5
- Fix for running on newer gnome versions

* Wed Jul 22 2026 Python Maint <python-maint@redhat.com> - 0.5.22-4
- Rebuilt for Python 3.15.0b4 ABI change

* Thu Jul 16 2026 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.22-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_45_Mass_Rebuild

* Wed Jun 03 2026 Python Maint <python-maint@redhat.com> - 0.5.22-2
- Rebuilt for Python 3.15

* Thu Feb 26 2026 Steve Cossette <farchord@gmail.com> - 0.5.22-1
- 0.5.22

* Tue Feb 24 2026 Steve Cossette <farchord@gmail.com> - 0.5.21-1
- 0.5.21

* Mon Feb 16 2026 Steve Cossette <farchord@gmail.com> - 0.5.20-1
- 0.5.20

* Fri Jan 30 2026 Steve Cossette <farchord@gmail.com> - 0.5.19-9
- Some cleanup, to get ready for epel10

* Fri Jan 16 2026 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.19-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_44_Mass_Rebuild

* Wed Nov 05 2025 Steve Cossette <farchord@gmail.com> - 0.5.19-7
- Added a patch to fix the installation of games

* Fri Sep 19 2025 Python Maint <python-maint@redhat.com> - 0.5.19-6
- Rebuilt for Python 3.14.0rc3 bytecode

* Fri Aug 15 2025 Python Maint <python-maint@redhat.com> - 0.5.19-5
- Rebuilt for Python 3.14.0rc2 bytecode

* Thu Jul 24 2025 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.19-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_43_Mass_Rebuild

* Thu Jul 10 2025 Steve Cossette <farchord@gmail.com> - 0.5.19-3
- Slight optimization of the %%files section

* Tue Jun 17 2025 Python Maint <python-maint@redhat.com> - 0.5.19-2
- Rebuilt for Python 3.14

* Sun Feb 23 2025 Steve Cossette <farchord@gmail.com> - 0.5.19-1
- Update to v0.5.19

* Mon Feb 17 2025 Christian Birk <mail@birkc.de> - 0.5.18-4
- fix runtime error for updated dependency evdev

* Tue Jan 21 2025 Steve Cossette <farchord@gmail.com> - 0.5.18-3
- Fixed the spec using the whole folder, updated build requirements'
  package names

* Fri Jan 17 2025 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.18-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Wed Dec 04 2024 Steve Cossette <farchord@gmail.com> - 0.5.18-1
- Update to 0.5.18

* Wed Nov 20 2024 Steve Cossette <farchord@gmail.com> - 0.5.17-9
- Added libXScrnSaver as a Requires for the web runner

* Sat Oct 12 2024 Steve Cossette <farchord@gmail.com> - 0.5.17-8
- Added protobuf dependancy for battle.net

* Mon Sep 09 2024 Yaakov Selkowitz <yselkowi@redhat.com> - 0.5.17-7
- Exclude multilib dependencies on RHEL 10

* Mon Jul 29 2024 Miroslav Suchý <msuchy@redhat.com> - 0.5.17-6
- convert GPLv3 license to SPDX

* Thu Jul 18 2024 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.17-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Sat Jun 08 2024 Python Maint <python-maint@redhat.com> - 0.5.17-4
- Rebuilt for Python 3.13

* Mon May 27 2024 Steve Cossette <farchord@gmail.com> - 0.5.17-3
- Added cairo as runtime dependancy

* Thu Apr 11 2024 Steve Cossette <farchord@gmail.com> - 0.5.17-2
- Skipped the API test as it seems to (...sometimes?) try to download from
  the internet

* Thu Apr 11 2024 Steve Cossette <farchord@gmail.com> - 0.5.17-1
- v0.5.17

* Thu Feb 29 2024 Steve Cossette <farchord@gmail.com> - 0.5.16-4
- Added tests

* Thu Jan 25 2024 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.16-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Sun Jan 21 2024 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.16-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_40_Mass_Rebuild

* Tue Jan 16 2024 Steve Cossette <farchord@gmail.com> - 0.5.16-1
- 0.5.16 (And a patch)

* Sat Jan 13 2024 Steve Cossette <farchord@gmail.com> - 0.5.15-1
- Update to 0.5.15

* Fri Oct 20 2023 Steve Cossette <farchord@gmail.com> - 0.5.14-1
- Update to 0.5.14

* Sun Aug 20 2023 Steve Cossette <farchord@gmail.com> - 0.5.13-5
- Changed the webkit2gtk3 dependancy to webkit2gtk4.1

* Thu Jul 20 2023 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.13-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_39_Mass_Rebuild

* Thu Jun 15 2023 Python Maint <python-maint@redhat.com> - 0.5.13-3
- Rebuilt for Python 3.12

* Fri May 19 2023 Steve Cossette <farchord@gmail.com> 0.5.13-2
- Applied a fix for a bug where Lutris may no longer start on 0.5.13 if the user was running a deprecated runner.

* Tue May 16 2023 Steve Cossette <farchord@gmail.com> 0.5.13-1
- Update to 0.5.13

* Sun Apr 16 2023 Steve Cossette <farchord@gmail.com> 0.5.12-4
- Added gamescope as a recommendation (Helps with game compatibility, and is supported by lutris)

* Wed Feb 15 2023 Chris King <bunnyapocalypse@protonmail.com> 0.5.12-3
- Fix missing depends by using both meson and py3 macros

* Sun Feb 5 2023 Chris King <bunnyapocalypse@protonmail.com> 0.5.12-2
- Fix locale support by switching to meson

* Wed Dec 21 2022 Steve Cossette <farchord@gmail.com> - 0.5.12-1
- Add support for Xbox games with the xemu runner
- Fix authentication issue with Origin
- Fix authentication issue with EGS
- Fix authentication issue with Ubisoft Connect when 2FA is enabled
- Fix integration issue with GOG
- Add Discord Rich Presence integration
- Add ability to extract icons from Windows executables
- Allow setting custom cover art
- Re-style configuration dialogs

* Thu Aug 25 2022 Steve Cossette <farchord@gmail.com> - 0.5.11-1
- Update to 0.5.11:
- Fix for some installers commands exiting with return code 256
- Change shortcut for show/hide installed games to Ctrl + i
- Show/hide hidden games is assigned to Ctrl + h
- Install game launcher before login for services that use one.
- Add Amazon Games integration
- Added SheepShaver, BasiliskII and Mini vMac runners
- Don't perform runtime updates when a game is launched via a shortcut
- Support variables in script URLs
- Fix crash when Lutris is unable to read the screen resolution
- Enable Gamescope on Nvidia >= 515
- Fixes for Steam shortcuts
- Add Gnome Console and Deepin Terminal to supported terminal emulators
- Fix crash when Mangohud is used alongside Gamescope
- Translation updates

* Wed Jun 29 2022 Steve Cossette <farchord@gmail.com> - 0.5.10.1-4
- Added some missing GUI package recommended packages:
- Recommendations: p7zip, curl, fluid-soundfont-gs (For MIDI playback -- other soundfonts can be substituted)

* Sun Jun 26 2022 Steve Cossette <farchord@gmail.com> - 0.5.10.1-3
- Added recommends for gamemode

* Sun Jun 19 2022 Steve Cossette <farchord@gmail.com> - 0.5.10.1-2
- Added a Recommends for p7zip-plugins (Required by some game installers)

* Thu May 26 2022 Steve Cossette <farchord@gmail.com> - 0.5.10.1-1
- small realease with QOL changes

* Fri Apr 01 2022 Steve Cossette <farchord@gmail.com> - 0.5.10-1
- Initial release of version 0.5.10. Changelog:
- Add new window to add games to Lutris, with searches from the website, scanning a folder for previously installed games, installing a Windows game from a setup file, installing from a YAML script or configuring a single game manually.
- Move the search for Lutris installers from a tab in the Lutris service to the window for adding games.
- Add option to add a Lutris game to Steam
- Add a coverart format
- Add integration with EA Origin
- Add integration with Ubisoft Connect
- Download missing media on startup
- Remove Winesteam runner (install Steam for Windows in Lutris instead)
- PC (Linux and Windows) games have their own dedicated Nvidia shader cache
- Add dgvoodoo2 option
- Add option to enable BattleEye anti-cheat support
- Default to Retroarch cores in ~/.config/retroarch/cores if available
- Add support for downloading patches and DLC for GOG games
- Add --export and --import command line flags to export a game a lutris game and re-import it (requires --dest for the destination path, feature still experimental)
- Add command line flags to manage runners: --install-runner, --uninstall-runners, --list-runners, --list-wine-versions
- Change behavior of the "Stop" button, remove "Kill all Wine processes" action
- Gamescope option is now disabled on Nvidia GPUs
- Enable F-Sync by default

* Thu Nov 04 2021 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.9.1-3
- Add 32 bit wine pulseaudio support

* Wed Oct 20 2021 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.9.1-2
- Add 32 bit pipewire as requirement

* Sun Oct 17 2021 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.9.1-1
- New version

* Fri Oct 15 2021 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.8.4-2
- Revert 0.5.9 on advice of Lutris devs

* Tue Oct 12 2021 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.9-1
- New version

* Thu Jul 22 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.8.3-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_35_Mass_Rebuild

* Fri Jun 04 2021 Python Maint <python-maint@redhat.com> - 0.5.8.3-6
- Rebuilt for Python 3.10

* Mon May  3 2021 Daniel Rusek <mail@asciiwolf.com> - 0.5.8.3-5
- Adding 32-bit wine-core weak dependency

* Thu Apr  8 2021 Anders Lind <smitna@gmail.com> - 0.5.8.3-4
- Adding python3-dbus dependency

* Thu Jan 28 2021 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.8.3-3
- Adding python3-lmxl dependency

* Tue Jan 26 2021 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.8.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Sat Jan 23 2021 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.8.3-1
- New Version

* Tue Jan 05 2021 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.8.2-1
- New version

* Sun Nov 29 2020 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.8.1-2
- Patch to remove python-magic as a requirement to fix some issues

* Sun Nov 29 2020 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.8.1-1
- New Version

* Wed Nov 18 2020 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.8-1
- New Version

* Tue Jul 28 2020 Adam Jackson <ajax@redhat.com> - 0.5.7.1-3
- Require xrandr not xorg-x11-server-utils

* Tue Jul 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.7.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Fri Jul 24 2020 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.7.1-1
- New Version

* Sun Jul 5 2020 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.7-1
- New Version

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 0.5.6-2
- Rebuilt for Python 3.9

* Thu Apr 16 2020 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.6-1
- New Version

* Sun Apr 05 2020 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.5-2
- Removed unecessary comments

* Sun Apr 05 2020 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.5-1
- New Version

* Fri Mar 13 2020 Artem Polishchuk <ego.cordatus@gmail.com> - 0.5.4-3
- Backport upstream patch. Fix #1806132

* Wed Jan 29 2020 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.4-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sun Jan 26 2020 Tomas Tomecek <ttomecek@redhat.com> - 0.5.4-1
- new upstream release: 0.5.4

* Sun Sep 8 2019 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.3-1
- New Version

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 0.5.2.1-3
- Rebuilt for Python 3.8

* Thu Jul 25 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.5.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Wed Apr 10 2019 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.2.1-1
- New version

* Mon Apr 8 2019 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.2-1
- New version

* Mon Feb 25 2019 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.1.2-1
- New version

* Mon Feb 25 2019 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.1.1-1
- New version

* Sun Feb 24 2019 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.1-1
- New version

* Tue Feb 19 2019 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.0.1-5
- More additional depends

* Sun Feb 3 2019 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.0.1-2
- Forgot to add additional depends

* Sun Feb 3 2019 Christopher King <bunnyapocalypse@protonmail.com> - 0.5.0.1-1
- Updating version

* Fri Feb 01 2019 Fedora Release Engineering <releng@fedoraproject.org> - 0.4.23-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Jan 3 2019 Christopher King <bunnyapocalypse@protonmail.com> - 0.4.23-8
- Forgot mesa-libGL drivers

* Sun Dec 30 2018 Christopher King <bunnyapocalypse@protonmail.com> - 0.4.23-7
- Forgot 64 bit mesa-dri drivers

* Sun Dec 30 2018 Christopher King <bunnyapocalypse@protonmail.com> - 0.4.23-6
- Changing depends again, specifying arches

* Fri Dec 28 2018 Christopher King <bunnyapocalypse@protonmail.com> - 0.4.23-5
- Changing the format of those previously added dependencies so that they work

* Thu Dec 20 2018 Christopher King <bunnyapocalypse@protonmail.com> - 0.4.23-4
- Adding some mesa depends to make Lutris work on more systems more reliably

* Fri Nov 16 2018 Christopher King <bunnyapocalypse@protonmail.com> - 0.4.23-3
- Turns out that I hadn't actually made a mistake, reverting most of the changes

* Thu Nov 15 2018 Christopher King <bunnyapocalypse@protonmail.com> - 0.4.23-2
- Updating this spec to actually install the appdata file

* Wed Nov 7 2018 Christopher King <bunnyapocalypse@protonmail.com> - 0.4.23
- New version

* Mon Nov 5 2018 Christopher King <bunnyapocalypse@protonmail.com> - 0.4.22
- New version

* Fri Nov 2 2018 Christopher King <bunnyapocalypse@protonmail.com> - 0.4.21.1
- New version

* Sat Oct 20 2018 Christopher King <bunnyapocalypse@protonmail.com> - 0.4.21
- New version

* Wed Oct 10 2018 Christopher King <bunnyapocalypse@protonmail.com> - 0.4.20
- Edit the SUSE build service spec file to be fedora specific

* Tue Nov 29 2016 Mathieu Comandon <strycore@gmail.com> - 0.4.3
- Ensure correct Python3 dependencies
- Set up Python macros for building (Thanks to Pharaoh_Atem on #opensuse-buildservice)

* Sat Oct 15 2016 Mathieu Comandon <strycore@gmail.com> - 0.4.0
- Update to Python 3
- Bump version to 0.4.0

* Sat Dec 12 2015 Rémi Verschelde <akien@mageia.org> - 0.3.7-2
- Remove ownership of system directories
- Spec file cleanup

* Fri Nov 27 2015 Mathieu Comandon <strycore@gmail.com> - 0.3.7-1
- Bump to version 0.3.7

* Thu Oct 30 2014 Mathieu Comandon <strycore@gmail.com> - 0.3.6-1
- Bump to version 0.3.6
- Add OpenSuse compatibility (contribution by @malkavi)

* Fri Sep 12 2014 Mathieu Comandon <strycore@gmail.com> - 0.3.5-1
- Bump version to 0.3.5

* Thu Aug 14 2014 Travis Nickles <nickles.travis@gmail.com> - 0.3.4-3
- Edited Requires to include pygobject3.

* Wed Jun 04 2014 Travis Nickles <nickles.travis@gmail.com> - 0.3.4-2
- Changed build and install step based on template generated by
  rpmdev-newspec.
- Added Requires.
- Ensure package can be built using mock.

* Tue Jun 03 2014 Travis Nickles <nickles.travis@gmail.com> - 0.3.4-1
- Initial version of the package

## END: Generated by rpmautospec
