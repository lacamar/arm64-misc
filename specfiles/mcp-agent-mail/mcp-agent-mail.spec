%global debug_package %{nil}
%global __brp_mangle_shebangs_exclude_from ^%{_libdir}/%{name}/.*$
%global __requires_exclude_from ^%{_libdir}/%{name}/.*$
%global __provides_exclude_from ^%{_libdir}/%{name}/.*$

Name:           mcp-agent-mail
Version:        0.3.4
Release:        2%{?dist}
Summary:        Mail-like coordination MCP server for coding agents

License:        MIT
URL:            https://github.com/Dicklesworthstone/mcp_agent_mail
Source0:        %{url}/archive/v%{version}/mcp_agent_mail-%{version}.tar.gz

Patch0:         0001-xdg-default-paths.patch

BuildRequires:  python3.14-devel
BuildRequires:  uv
BuildRequires:  gcc
Requires:       /usr/bin/python3.14
Requires:       git-core

%description
MCP Agent Mail: asynchronous, mail-like coordination layer for coding agents,
with identities, inboxes, searchable threads and advisory file reservations
backed by Git and SQLite.

%prep
%autosetup -p1 -n mcp_agent_mail-%{version}

%install
export UV_PYTHON_DOWNLOADS=never UV_LINK_MODE=copy UV_NO_CACHE=1
export UV_PROJECT_ENVIRONMENT=%{buildroot}%{_libdir}/%{name}
uv sync --frozen --no-dev --no-editable --no-install-project --python /usr/bin/python3.14
uv pip install --python %{buildroot}%{_libdir}/%{name}/bin/python --no-deps .
rm -f %{buildroot}%{_libdir}/%{name}/bin/{activate*,deactivate*,*.bat}
grep -rlF %{buildroot} %{buildroot}%{_libdir}/%{name} | xargs -r sed -i 's|%{buildroot}||g'
%py_byte_compile /usr/bin/python3.14 %{buildroot}%{_libdir}/%{name}/lib
install -dm0755 %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'EOS'
#!/bin/sh
exec %{_libdir}/%{name}/bin/python -P -m mcp_agent_mail "$@"
EOS
chmod 0755 %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}
%{_libdir}/%{name}

%changelog
* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.4-2
- Pin venv to Python 3.14

* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.4-1
- Initial package
