Name:           python-anisette
Version:        1.2.4
Release:        5%{?dist}
Summary:        Apple anisette data provider

License:        MIT
URL:            https://github.com/malmeloo/Anisette.py
Source0:        https://files.pythonhosted.org/packages/source/a/anisette/anisette-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Apple anisette data provider.}

%description %_description

%package -n python3-anisette
Summary:        %{summary}

%description -n python3-anisette %_description

%prep
%autosetup -n anisette-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
rm %{buildroot}%{_bindir}/ani*
%pyproject_save_files -l anisette

%check
%pyproject_check_import -e anisette.cli -e anisette.__main__

%files -n python3-anisette -f %{pyproject_files}

%changelog
* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.2.4-5
- Fix subpackage name
- Lowercase source URL
- Skip CLI import check
- Drop CLI scripts
