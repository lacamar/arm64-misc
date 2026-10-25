Name:           python-srp
Version:        1.0.22
Release:        4%{?dist}
Summary:        Secure Remote Password protocol for Python

License:        MIT
URL:            https://github.com/cocagne/pysrp
Source0:        %{pypi_source srp}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Secure Remote Password protocol for Python.}

%description %_description

%package -n python3-srp
Summary:        %{summary}

%description -n python3-srp %_description

%prep
%autosetup -n srp-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l srp

%check
%pyproject_check_import -e 'srp.doc*' -e srp.test_srp

%files -n python3-srp -f %{pyproject_files}

%changelog
* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.0.22-4
- Fix subpackage name
- Initial package
