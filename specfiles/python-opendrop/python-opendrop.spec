Name:           python-opendrop
Version:        0.13.0
Release:        3%{?dist}
Summary:        Open Apple AirDrop implementation

License:        GPL-3.0-or-later
URL:            https://github.com/seemoo-lab/opendrop
Source0:        %{pypi_source opendrop}
Patch0:         opendrop-no-pkg-resources.patch
Patch1:         opendrop-chunked-requests.patch

BuildArch:      noarch
BuildRequires:  python3-devel

%global _description %{expand:
Send and receive files over AirDrop. Needs an awdl0 interface (see awdld).}

%description %_description

%package -n python3-opendrop
Summary:        %{summary}
Requires:       awdld

%description -n python3-opendrop %_description

%prep
%autosetup -p1 -n opendrop-%{version}

%generate_buildrequires
%pyproject_buildrequires -R

%build
%pyproject_wheel

%install
%pyproject_install
%pyproject_save_files -L opendrop

%files -n python3-opendrop -f %{pyproject_files}
%{_bindir}/opendrop

%changelog
* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.13.0-3
- Receive x-dvzip uploads

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.13.0-2
- Accept chunked Discover/Ask requests

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.13.0-1
- Initial package
- Drop pkg_resources
