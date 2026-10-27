Name:           python-opendrop
Version:        0.13.0
Release:        10%{?dist}
Summary:        Open Apple AirDrop implementation

License:        GPL-3.0-or-later
URL:            https://github.com/seemoo-lab/opendrop
Source0:        %{pypi_source opendrop}
Patch0:         opendrop-no-pkg-resources.patch
Patch1:         opendrop-chunked-requests.patch
Patch2:         opendrop-receive-dir.patch
Patch3:         opendrop-dvzip-raw-blocks.patch
Patch4:         opendrop-awdl-robust.patch
Patch5:         opendrop-dvzip-stored-flag.patch
Patch6:         opendrop-drain-body.patch
Patch7:         opendrop-send-ios.patch
Source1:        opendrop-receive.service

BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  systemd-rpm-macros

%global _description %{expand:
Send and receive files over AirDrop. Needs an awdl0 interface (see awdld).}

%description %_description

%package -n python3-opendrop
Summary:        %{summary}
Requires:       awdld
Requires:       iproute
Requires:       python3-dbus-next

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
install -Dm644 %{SOURCE1} %{buildroot}%{_userunitdir}/opendrop-receive.service

%files -n python3-opendrop -f %{pyproject_files}
%{_bindir}/opendrop
%{_userunitdir}/opendrop-receive.service

%changelog
* Tue Oct 27 2026 Lachlan Marie <lchlnm@pm.me> - 0.13.0-10
- Restart receiver when awdl0 is recreated

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.13.0-9
- Fix sending on Python 3.12+ and Pillow 10+
- Send x-dvzip uploads with TransferID
- Wake iOS receivers over BLE via BlueZ
- Report epub as org.idpf.epub-container

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.13.0-8
- Bound upload drain to 2 s, reply without terminal chunk
- Lingering close (20 s) after upload reply

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.13.0-7
- Drain upload body before replying (iOS reported failure)

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.13.0-6
- Handle stored x-dvzip blocks (videos, large photos)

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.13.0-5
- Stream x-dvzip uploads
- Threaded server, 60 s socket timeout
- AWDL UUID host name (matches awdld ARPA)
- Announce dummy A record
- Stop at terminal chunk of chunked uploads

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.13.0-4
- Save to XDG download dir, flatten NSIRD folders
- Drop ._ AppleDouble files
- Persist service id
- Config under XDG data dir
- Add -o/--output
- Add opendrop-receive user unit
- Accept stored dvzip blocks

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.13.0-3
- Receive x-dvzip uploads

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.13.0-2
- Accept chunked Discover/Ask requests

* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0.13.0-1
- Initial package
- Drop pkg_resources
