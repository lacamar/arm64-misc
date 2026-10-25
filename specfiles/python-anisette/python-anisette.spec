%global commit      627c9c663062bd872182b653113759c9d66b7e13
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate    20261021

Name:           python-anisette
Version:        1.2.4^%{snapdate}git%{shortcommit}
Release:        3%{?dist}
Summary:        Apple anisette data provider

License:        MIT
URL:            https://github.com/malmeloo/Anisette.py
Source0:        https://github.com/sacca97/Anisette.py/archive/%{commit}/Anisette.py-%{shortcommit}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Apple anisette data provider using the macOS ADI backend (PR 6).}

%description %_description

%package -n python3-anisette
Summary:        %{summary}

%description -n python3-anisette %_description

%prep
%autosetup -n Anisette.py-%{commit}
sed -i -e '/"typer>=/d;/"rich>=/d;/"fastapi>=/d;/"granian>=/d' \
    -e 's|"websockets>=16[^"]*"|"websockets>=15"|;s|"macOS-ADI-emulator @ git+[^"]*"|"macos-adi-emulator"|' pyproject.toml

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
rm -r %{buildroot}%{python3_sitelib}/anisette/cli %{buildroot}%{python3_sitelib}/anisette/__main__.py
rm -f %{buildroot}%{_bindir}/ani*
%pyproject_save_files -l anisette

%check
%pyproject_check_import -e 'anisette.cli*' -e anisette.__main__

%files -n python3-anisette -f %{pyproject_files}

%changelog
* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.2.4^20261021git627c9c6-3
- Skip CLI import check

* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.2.4^20261021git627c9c6-2
- Relax websockets pin

* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.2.4^20261021git627c9c6-1
- Update to PR 6 head (macOS ADI backend)
- Add macos-adi-emulator dependency
- Drop CLI and server deps
