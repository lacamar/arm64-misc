%global debug_package %{nil}
%global goipath github.com/Dicklesworthstone/beads_viewer

Name:           bv
Version:        0.29.0
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
# upstream pins a go patch release; Fedora may lag, vendored deps need only 1.26
sed -i 's/^go 1\.26\.[0-9]*$/go 1.26/' go.mod

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
* Fri Nov 27 2026 Lachlan Marie <lchlnm@pm.me> - 0.29.0-1
- Update to 0.29.0

* Tue Nov 24 2026 Lachlan Marie <lchlnm@pm.me> - 0.28.0-1
- Update to 0.28.0

* Sun Nov 22 2026 Lachlan Marie <lchlnm@pm.me> - 0.27.0-2
- Relax go.mod patch-level go requirement

* Sun Nov 22 2026 Lachlan Marie <lchlnm@pm.me> - 0.27.0-1
- Update to 0.27.0

* Thu Nov 05 2026 Lachlan Marie <lchlnm@pm.me> - 0.26.0-1
- Update to 0.26.0

* Thu Oct 08 2026 Lachlan Marie <lchlnm@pm.me> - 0.25.2-1
 - Update to 0.25.2

* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.25.0-1
- Initial package
