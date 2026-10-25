Name:           python-bleak
Version:        3.0.2
Release:        2%{?dist}
Summary:        Cross-platform Bluetooth Low Energy client

License:        MIT
URL:            https://github.com/hbldh/bleak
Source0:        %{pypi_source bleak}

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Cross-platform Bluetooth Low Energy client.}

%description %_description

%package -n python3-python-bleak
Summary:        %{summary}

%description -n python3-python-bleak %_description

%prep
%autosetup -n bleak-%{version}

%generate_buildrequires
%pyproject_buildrequires

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -l bleak

%check
%pyproject_check_import -e 'bleak.backends.winrt*' -e 'bleak.backends.p4android*' -e 'bleak.backends.corebluetooth*'

%files -n python3-python-bleak -f %{pyproject_files}

%changelog
* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 3.0.2-2
- Skip non-Linux imports
