%global commit      f2d24c86c3357f93cc19dd605fa9dc34d6d1b1c6
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate    20261021

Name:           python-findmy
Version:        0.10.2^%{snapdate}git%{shortcommit}
Release:        3%{?dist}
Summary:        Apple Find My library

License:        MIT
URL:            https://github.com/malmeloo/FindMy.py
Source0:        https://github.com/sacca97/FindMy.py/archive/%{commit}/FindMy.py-%{shortcommit}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Apple Find My library (PR 279, macOS anisette backend).}

%description %_description

%package -n python3-findmy
Summary:        %{summary}

%description -n python3-findmy %_description

%prep
%autosetup -n FindMy.py-%{commit}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l findmy

%check
%pyproject_check_import

%files -n python3-findmy -f %{pyproject_files}

%changelog
* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.10.2^20261021gitf2d24c8-3
- Rebuild against new anisette

* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.10.2^20261021gitf2d24c8-2
- Rebuild against new anisette

* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.10.2^20261021gitf2d24c8-1
- Update to PR 279 head (macOS anisette)

* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.10.2-3
- Fix subpackage name
- Lowercase source URL
