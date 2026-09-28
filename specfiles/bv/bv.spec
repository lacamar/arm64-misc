%global debug_package %{nil}
%global goipath github.com/Dicklesworthstone/beads_viewer

Name:           bv
Version:        0.25.0
Release:        1%{?dist}
Summary:        Terminal UI and graph analytics for Beads issue trackers

License:        MIT
URL:            https://%{goipath}
Source0:        %{url}/archive/v%{version}/beads_viewer-%{version}.tar.gz

BuildRequires:  golang >= 1.26
BuildRequires:  git-core

%description
Beads Viewer: keyboard-driven TUI for browsing Beads issues, with dependency
graph analysis and a robot mode for AI coding agents.

%prep
%autosetup -p1 -n beads_viewer-%{version}

%build
export GOTOOLCHAIN=local
export CGO_ENABLED=0
export GOWORK=off
go build -mod=vendor -trimpath -buildmode=pie -o %{name} \
    -ldflags "-s -w -X %{goipath}/pkg/version.version=v%{version}" \
    ./cmd/bv

%install
install -Dpm0755 %{name} %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}

%changelog
* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.25.0-1
- Initial package
