%global debug_package %{nil}
%global goipath github.com/Dicklesworthstone/coding_agent_account_manager

Name:           caam
Version:        0.1.18
Release:        2%{?dist}
Summary:        Instant auth switching for AI coding CLIs

License:        MIT
URL:            https://%{goipath}
Source0:        %{url}/archive/v%{version}/coding_agent_account_manager-%{version}.tar.gz

Patch0:         0001-honor-CLAUDE_CONFIG_DIR.patch
Patch1:         0002-claude-email-from-state-file.patch

BuildRequires:  golang >= 1.26
BuildRequires:  git-core

%description
Coding Agent Account Manager: back up and swap subscription logins for
Claude Code, Codex, Gemini and Grok CLIs when hitting usage limits.

%prep
%autosetup -p1 -n coding_agent_account_manager-%{version}

%build
export GOTOOLCHAIN=local
export CGO_ENABLED=0
go build -trimpath -buildmode=pie -o %{name} \
    -ldflags "-s -w -X %{goipath}/internal/version.Version=%{version}" \
    ./cmd/caam

%install
install -Dpm0755 %{name} %{buildroot}%{_bindir}/%{name}
./%{name} completion bash > caam.bash
./%{name} completion zsh > _caam
./%{name} completion fish > caam.fish
install -Dpm0644 caam.bash %{buildroot}%{bash_completions_dir}/caam
install -Dpm0644 _caam %{buildroot}%{zsh_completions_dir}/_caam
install -Dpm0644 caam.fish %{buildroot}%{fish_completions_dir}/caam.fish

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}
%{bash_completions_dir}/caam
%{zsh_completions_dir}/_caam
%{fish_completions_dir}/caam.fish

%changelog
* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.18-2
- Read Claude email from .claude.json

* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.18-1
- Initial package
- Honor CLAUDE_CONFIG_DIR for vault switching
- Swap only account keys in .claude.json on activate
