%global tag 1.7.0
Name: wasistlos
Version: %{tag}
Release: 7%{?dist}
Summary: An unofficial WhatsApp desktop application for Linux.

License: GNU GPL v3
URL:     https://github.com/xeco23/WasIstLos
Source0: %{url}/archive/v%{version}/wasistlos-%{version}.tar.gz
Patch0:  0001-export-chat-transcript.patch
Patch1:  0002-continuous-chat-export.patch
Patch2:  0003-paste-image-clipboard.patch
Patch3:  0004-voice-note-transcription.patch

BuildRequires: cmake
BuildRequires: pkgconfig
BuildRequires: gcc
BuildRequires: gcc-c++
BuildRequires: gtk-layer-shell-devel
BuildRequires: gtkmm3.0-devel
BuildRequires: webkit2gtk4.1-devel
BuildRequires: libayatana-appindicator-gtk3-devel
BuildRequires: libcanberra-devel
BuildRequires: whisper-cpp-devel

Requires: /usr/bin/ffmpeg
Requires: /usr/bin/curl


%description
An unofficial WhatsApp desktop application for Linux.


%prep
%autosetup -n WasIstLos-1.7.0 -p1


%build
%cmake
%cmake_build


%install
%cmake_install
%find_lang %{name}


%files -f %{name}.lang
%license LICENSE
%doc    README.md

%{_bindir}/wasistlos

%{_datadir}/applications/com.github.xeco23.WasIstLos.desktop
%{_datadir}/metainfo/com.github.xeco23.WasIstLos.appdata.xml

%{_datadir}/icons/hicolor/*/apps/com.github.xeco23.WasIstLos.png
%{_datadir}/icons/hicolor/*/status/com.github.xeco23.WasIstLos-tray*.png



%changelog
* Thu Sep 24 2026 Lachlan Marie <lchlnm@pm.me> - 1.7.0-7
 - Transcribe voice notes into continuous export

* Fri Sep 18 2026 Lachlan Marie <lchlnm@pm.me> - 1.7.0-6
 - Backfill full chat history on continuous export enable
 - Add "Fetch Full History" option
 - Sort export by timestamp
 - Fix replies exporting quoted text

* Mon Sep 14 2026 Lachlan Marie <lchlnm@pm.me> - 1.7.0-5
 - Fix continuous chat export only ever writing whatever window of messages WhatsApp Web currently has rendered (it virtualizes the list) instead of the full history: native code now merges each scrape into the existing export file instead of overwriting it
 - Add patch to place a clipboard image into the currently open chat's compose box (menu item "Paste Image from Clipboard"), since WebKitGTK does not reliably expose native clipboard image data to a page's paste event the way Chrome/Firefox do

* Sat Sep 12 2026 Lachlan Marie <lchlnm@pm.me> - 1.7.0-4
 - Fix continuous chat export silently going stale for any chat that isn't the one currently on screen: resync the visible chat immediately on chat switch instead of waiting on the debounce, and force a resync when the app window regains focus

* Wed Sep 02 2026 Lachlan Marie <lchlnm@pm.me> - 1.7.0-3
 - Add patch to continuously export a chat to a self-updating markdown file as new messages arrive, with a per-chat destination configurable from the menu

* Wed Sep 02 2026 Lachlan Marie <lchlnm@pm.me> - 1.7.0-2
 - Add patch to export the full chat transcript (sender, timestamp, text, in order) to a text file

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 1.7.0-1
 - Update to 1.7.0

* Wed Jul 23 2025 Lachlan Marie <lchlnm@pm.me> - 1.7.0-1
- Initial RPM packaging of wasistlos
