Name:           giil
Version:        3.2.1
Release:        1%{?dist}
Summary:        Download full-resolution images from cloud photo share links

License:        MIT
URL:            https://github.com/Dicklesworthstone/giil
Source0:        %{url}/archive/v%{version}/giil-%{version}.tar.gz

BuildArch:      noarch

Requires:       curl
Requires:       gum
Requires:       nodejs >= 18
Requires:       npm
Recommends:     ImageMagick

%description
Get Image [from] Internet Link: fetch full-resolution images from iCloud,
Dropbox, Google Photos and Google Drive share links. Playwright and
Chromium are installed on first run into $XDG_CACHE_HOME/giil.

%prep
%autosetup -n giil-%{version}

%install
install -Dpm0755 giil %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}

%changelog
* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 3.2.1-1
- Initial package
