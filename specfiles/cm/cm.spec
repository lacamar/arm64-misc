%global debug_package %{nil}
%global __strip /bin/true

Name:           cm
Version:        0.3.0
Release:        1%{?dist}
Summary:        Procedural memory for AI coding agents

License:        MIT
URL:            https://github.com/Dicklesworthstone/cass_memory_system
Source0:        %{url}/archive/v%{version}/cass_memory_system-%{version}.tar.gz

BuildRequires:  nodejs-npm

%description
cass-memory: distills coding agent session history into a playbook of rules
and retrieves relevant context for new tasks.

%prep
%autosetup -n cass_memory_system-%{version}

%build
npm install --no-save --prefix .bun bun
export PATH=$PWD/.bun/node_modules/.bin:$PATH
bun install --frozen-lockfile
bun build src/cm.ts --compile --outfile %{name}

%install
install -Dpm0755 %{name} %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}

%changelog
* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.0-1
- Initial package
