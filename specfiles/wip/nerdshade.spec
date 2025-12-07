Name: nerdshade
Version:  1.3.0
Release:  %autorelease
Summary:  Hyprsunset client to smoothly transition color temperature during sunrise/sunset

License:  MIT
URL:      https://github.com/sstark/nerdshade
Source0:  https://github.com/sstark/nerdshade/archive/refs/tags/nerdshade-rel-1.3.0.tar.gz

BuildRequires:  go
BuildRequires:  go-rpm-macros
BuildRequires:  git

Requires: hyprsunset
Requires: hyprland

%description
Hyprsunset client to smoothly transition color temperature during sunrise/sunset

%prep
%autosetup -n nerdshade-rel-1.3.0
export GO111MODULE=on
go mod tidy
go mod vendor

%build
export GO111MODULE=on
export GOFLAGS="-mod=vendor"
%gobuild -o %{name} ./cmd/%{name}

%install
install -Dpm 0755 %{name} %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md
%define debug_package %{nil}

%{_bindir}/nerdshade

%changelog
* Sun Nov 16 2025 Lachlan Marie <lchlnm@pm.me> - 1.3.0-1
- Initial RPM packaging of nerdshade
