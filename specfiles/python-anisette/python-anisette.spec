Name:           python-anisette
Version:        1.2.4
Release:        1%{?dist}
Summary:        Apple anisette data provider

License:        MIT
URL:            https://github.com/malmeloo/Anisette.py
Source0:        %{pypi_source Anisette}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Apple anisette data provider.}

%description %_description

%package -n python3-python-anisette
Summary:        %{summary}

%description -n python3-python-anisette %_description

%prep
%autosetup -n Anisette-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l anisette

%check
%pyproject_check_import

%files -n python3-python-anisette -f %{pyproject_files}

%changelog
* sø. okt. 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.2.4-1
- Initial package
