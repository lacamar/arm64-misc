%global commit d4d2a832baf47d1cf43d989879950ac2aec45f47
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global snapdate    20261021

Name:           macos-adi-emulator
Version:        0.1.0^%{snapdate}git%{shortcommit}
Release:        2%{?dist}
Summary:        Unicorn emulator for Apple's macOS ADI library

License:        MIT
URL:            https://github.com/sacca97/os-findmy-e
Source0:        %{url}/archive/%{commit}/os-findmy-e-%{shortcommit}.tar.gz

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Runs Apple's macOS CoreADI under Unicorn to produce anisette data. The
CoreADI binary is downloaded at runtime by its users.}

%description %_description

%package -n python3-macos-adi-emulator
Summary:        %{summary}

%description -n python3-macos-adi-emulator %_description

%prep
%autosetup -n os-findmy-e-%{commit}

%generate_buildrequires
cd macOS-ADI-emulator
%pyproject_buildrequires

%build
cd macOS-ADI-emulator
%pyproject_wheel

%install
cd macOS-ADI-emulator
%pyproject_install
%pyproject_save_files -L macos_adi_emulator

%check
%pyproject_check_import

%files -n python3-macos-adi-emulator -f %{pyproject_files}
%license LICENSE
%{_bindir}/macos-adi-emulator

%changelog
* Thu Nov 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0^20261021gitd4d2a83-2
- Update to commit d4d2a832baf47d1cf43d989879950ac2aec45f47

* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0^20261021git374d838-2
- Fix license handling

* Sun Oct 25 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0^20261021git374d838-1
- Initial package
