Name:           python-findmy
Version:        0.10.2
Release:        2%{?dist}
Summary:        Apple Find My library

License:        MIT
URL:            https://github.com/malmeloo/FindMy.py
Source0:        https://files.pythonhosted.org/packages/source/f/findmy/findmy-%{version}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Apple Find My library.}

%description %_description

%package -n python3-python-findmy
Summary:        %{summary}

%description -n python3-python-findmy %_description

%prep
%autosetup -n findmy-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l findmy

%check
%pyproject_check_import

%files -n python3-python-findmy -f %{pyproject_files}

%changelog
* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.10.2-2
- Lowercase source URL
