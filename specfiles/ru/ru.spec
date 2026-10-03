Name:           ru
Version:        1.4.0
Release:        1%{?dist}
Summary:        Sync and maintain many GitHub repositories at once

License:        MIT
URL:            https://github.com/Dicklesworthstone/repo_updater
Source0:        %{url}/archive/v%{version}/repo_updater-%{version}.tar.gz

Patch0:         0001-disable-self-update.patch

BuildArch:      noarch

Requires:       curl
Requires:       gh
Requires:       git-core
Requires:       jq
Recommends:     gum
Suggests:       python3

%description
Repo Updater: clone, pull and report status across a list of GitHub
repositories, with optional AI-driven review and commit sweeps.

%prep
%autosetup -p1 -n repo_updater-%{version}

%install
install -Dpm0755 ru %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}

%changelog
* Tue Sep 29 2026 Lachlan Marie <lchlnm@pm.me> - 1.4.0-1
 - Update to 1.4.0

* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 1.3.1-1
- Initial package
- Disable self-update
