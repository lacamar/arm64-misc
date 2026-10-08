%global debug_package %{nil}
%global goipath github.com/Dicklesworthstone/coding_agent_account_manager

Name:           caam
Version:        0.1.23
Release:        2%{?dist}
Summary:        Instant auth switching for AI coding CLIs

License:        MIT
URL:            https://%{goipath}
Source0:        %{url}/archive/v%{version}/coding_agent_account_manager-%{version}.tar.gz

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
./%{name} completion bash | install -Dm0644 /dev/stdin %{buildroot}%{bash_completions_dir}/caam
./%{name} completion zsh | install -Dm0644 /dev/stdin %{buildroot}%{zsh_completions_dir}/_caam
./%{name} completion fish | install -Dm0644 /dev/stdin %{buildroot}%{fish_completions_dir}/caam.fish

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}
%{bash_completions_dir}/caam
%{zsh_completions_dir}/_caam
%{fish_completions_dir}/caam.fish

%changelog
* Fri Oct 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.23-2
 - Update to 0.1.23

* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.18-2
- Read Claude email from .claude.json

* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.18-1
- Initial package
- Honor CLAUDE_CONFIG_DIR for vault switching
- Swap only account keys in .claude.json on activate
