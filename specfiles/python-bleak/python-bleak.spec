Name:           python-bleak
Version:        3.1.0
Release:        5%{?dist}
Summary:        Cross-platform Bluetooth Low Energy client

License:        MIT
URL:            https://github.com/hbldh/bleak
Source0:        %{pypi_source bleak}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Cross-platform Bluetooth Low Energy client.}

%description %_description

%package -n python3-bleak
Summary:        %{summary}

%description -n python3-bleak %_description

%prep
%autosetup -n bleak-%{version}
sed -i 's/"uv_build>=[^"]*"/"uv_build>=0.10.9"/' pyproject.toml

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l bleak

%check
%pyproject_check_import -e 'bleak.backends.winrt*' -e 'bleak.backends.p4android*' -e 'bleak.backends.corebluetooth*'

%files -n python3-bleak -f %{pyproject_files}

%changelog
* Sat Nov 14 2026 Lachlan Marie <lchlnm@pm.me> - 3.1.0-5
- Update to 3.1.0

* Fri Nov 06 2026 Lachlan Marie <lchlnm@pm.me> - 3.0.2-5
- Keep build-backend intact

* Fri Nov 06 2026 Lachlan Marie <lchlnm@pm.me> - 3.0.2-4
- Relax uv_build upper bound for F45

* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 3.0.2-3
- Fix subpackage name
- Skip non-Linux imports
