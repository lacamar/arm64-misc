%global debug_package %{nil}
%global goipath github.com/Dicklesworthstone/ntm

Name:           ntm
Version:        1.35.1
Release:        1%{?dist}
Summary:        Named Tmux Manager for orchestrating AI coding agents

License:        MIT
URL:            https://%{goipath}
Source0:        %{url}/archive/v%{version}/ntm-%{version}.tar.gz

BuildRequires:  golang >= 1.26.8
BuildRequires:  git-core
Requires:       tmux

%description
Named Tmux Manager: spawn, tile and coordinate multiple AI coding agents
(Claude Code, Codex, Gemini) across tmux panes.

%prep
%autosetup -p1 -n ntm-%{version}

%build
export GOTOOLCHAIN=local
export CGO_ENABLED=0
go build -trimpath -buildmode=pie -tags=ensemble_experimental -o %{name} \
    -ldflags "-s -w -X %{goipath}/internal/cli.Version=%{version} -X %{goipath}/internal/cli.BuiltBy=rpm" \
    ./cmd/ntm

%install
install -Dpm0755 %{name} %{buildroot}%{_bindir}/%{name}
./%{name} completion bash | install -Dm0644 /dev/stdin %{buildroot}%{bash_completions_dir}/ntm
./%{name} completion zsh | install -Dm0644 /dev/stdin %{buildroot}%{zsh_completions_dir}/_ntm
./%{name} completion fish | install -Dm0644 /dev/stdin %{buildroot}%{fish_completions_dir}/ntm.fish

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}
%{bash_completions_dir}/ntm
%{zsh_completions_dir}/_ntm
%{fish_completions_dir}/ntm.fish

%changelog
* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 1.35.1-1
- Initial package
