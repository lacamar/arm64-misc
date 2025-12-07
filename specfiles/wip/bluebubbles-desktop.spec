Name:       bluebubbles-desktop
Version:    1.15.5
Release:    1%{?dist}
Summary:    Messaging client for iMessage

License:    Apache v2
URL:        https://github.com/BlueBubblesApp/bluebubbles-app
Source0:    https://github.com/BlueBubblesApp/bluebubbles-app/archive/92939908be75edb1afbc952a50db23d7c4354b58.tar.gz
Source1:    flutter-3.39.0-1.0.pre-267.tar.xz
Source2:    bluebubbles-desktop-pub-cache-1.15.5.tar.xz

BuildRequires:   git
BuildRequires:   chromium

%description
A cross-platform app ecosystem, bringing iMessage to Android, PC (Windows, Linux, & even macOS), and Web!

%prep
%autosetup -n bluebubbles-app-92939908be75edb1afbc952a50db23d7c4354b58

export CHROME_EXECUTABLE=/usr/bin/chromium

tar -xJf %{SOURCE1} -C %{_builddir}
export PATH="%{_builddir}/flutter/bin:$PATH"


tar -xJf %{SOURCE2} -C %{_builddir}/bluebubbles-app-92939908be75edb1afbc952a50db23d7c4354b58
export PUB_CACHE=%{_builddir}/bluebubbles-app-92939908be75edb1afbc952a50db23d7c4354b58/flutter_cache
ls "$PUB_CACHE"

flutter pub get --offline


# linux/flutter/ephemeral/.plugin_symlinks/tray_manager/linux/CMakeLists.txt

# After the add_library(tray_manager_plugin ...) line, add:

sed -e s//target_compile_options(tray_manager_plugin PRIVATE -Wno-deprecated-declarations)/ linux/flutter/ephemeral/.plugin_symlinks/tray_manager/linux/CMakeLists.txt

%build
tar -xf %{SOURCE0}

%install
#############


%files
%license LICENSE
%doc README.md
%define debug_package %{nil}

%{_bindir}/bluebubbles
%{_libdir}/bluebubbles/*
%{_datadir}/data/*


%changelog
* Mon Nov 24 2025 Lachlan Marie <lchlnm@pm.me> - 1.15.5
- Initial RPM packaging of bluebubbles-desktop
