# modules are sha256-pinned at runtime
%global __brp_mangle_shebangs_exclude_from ^%{_datadir}/%{name}/

Name:           ubs
Version:        5.4.15
Release:        1%{?dist}
Summary:        Ultimate Bug Scanner, multi-language static bug finder

License:        MIT
URL:            https://github.com/Dicklesworthstone/ultimate_bug_scanner
Source0:        %{url}/archive/v%{version}/ultimate_bug_scanner-%{version}.tar.gz

Patch0:         0001-disable-self-update.patch
Patch1:         0002-force-C-numeric-locale.patch

BuildArch:      noarch

Requires:       bash
Requires:       coreutils
Requires:       curl
Requires:       git-core
Requires:       jq
Requires:       python3
Requires:       ripgrep
Requires:       tar
Requires:       unzip

%description
Scans JavaScript/TypeScript, Python, C/C++, Rust, Go, Java, Kotlin, Ruby,
Swift, C#, Elixir and Bash code for bugs commonly introduced by AI coding
agents.

%prep
%autosetup -p1 -n ultimate_bug_scanner-%{version}

%install
install -Dpm0755 ubs %{buildroot}%{_datadir}/%{name}/ubs
install -pm0644 VERSION detectors.yml %{buildroot}%{_datadir}/%{name}/
cp -a modules %{buildroot}%{_datadir}/%{name}/
rm -f %{buildroot}%{_datadir}/%{name}/modules/README.md
install -d %{buildroot}%{_bindir}
ln -s ../share/%{name}/ubs %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}
%{_datadir}/%{name}

%changelog
* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 5.4.15-1
- Initial package
- Disable self-update
- Fix EPOCHREALTIME parsing in decimal-comma locales
