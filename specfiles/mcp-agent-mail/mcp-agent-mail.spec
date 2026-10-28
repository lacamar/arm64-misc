%global debug_package %{nil}

Name:           mcp-agent-mail
Version:        0.3.39
Release:        1%{?dist}
Summary:        Mail-like coordination layer for coding agents over MCP

License:        MIT
URL:            https://github.com/Dicklesworthstone/mcp_agent_mail_rust
Source0:        %{url}/releases/download/v%{version}/%{name}-aarch64-unknown-linux-gnu.tar.xz
Source1:        agent-mail.service

ExclusiveArch:  aarch64
BuildRequires:  systemd-rpm-macros

%description
Shared mailbox for coding agents: messages, per-agent inboxes and advisory
file reservations over MCP, with a local web UI. Ships the mcp-agent-mail
server and the am operator CLI.

%prep
%autosetup -c %{name}-%{version}

%install
install -Dm755 mcp-agent-mail %{buildroot}%{_bindir}/mcp-agent-mail
install -Dm755 am %{buildroot}%{_bindir}/am
install -Dm644 %{SOURCE1} %{buildroot}%{_userunitdir}/agent-mail.service

%files
%license LICENSE
%doc README.md
%{_bindir}/mcp-agent-mail
%{_bindir}/am
%{_userunitdir}/agent-mail.service

%post
%systemd_user_post agent-mail.service

%preun
%systemd_user_preun agent-mail.service

%postun
%systemd_user_postun_with_restart agent-mail.service

%changelog
* Wed Oct 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.39-1
- Switch to upstream Rust edition, prebuilt aarch64 binaries
- Drop Python venv build
- Ship am CLI and agent-mail user service

* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.4-2
- Pin venv to Python 3.14

* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.4-1
- Initial package
