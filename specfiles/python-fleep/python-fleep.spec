Name:           python-fleep
Version:        1.0.1
Release:        1%{?dist}
Summary:        File format determination library

License:        MIT
URL:            https://github.com/floyernick/fleep-py
Source0:        %{pypi_source fleep}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Determines file format from file signatures.}

%description %_description

%package -n python3-fleep
Summary:        %{summary}

%description -n python3-fleep %_description

%prep
%autosetup -n fleep-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -L fleep

%check
%pyproject_check_import

%files -n python3-fleep -f %{pyproject_files}

%changelog
* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 1.0.1-1
- Initial package
