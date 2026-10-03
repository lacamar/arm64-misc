%global debug_package %{nil}
%global goipath github.com/Dicklesworthstone/slb

Name:           slb
Version:        0.5.2
Release:        1%{?dist}
Summary:        Two-person rule for dangerous commands run by AI coding agents

License:        MIT
URL:            https://%{goipath}
Source0:        %{url}/archive/v%{version}/slb-%{version}.tar.gz

BuildRequires:  golang >= 1.24
BuildRequires:  git-core

%description
Simultaneous Launch Button: requires peer approval before AI coding agents
run destructive commands.

%prep
%autosetup -p1 -n slb-%{version}

%build
export GOTOOLCHAIN=local
export CGO_ENABLED=0
go build -trimpath -buildmode=pie -o %{name} \
    -ldflags "-s -w -X %{goipath}/internal/cli.version=%{version}" \
    ./cmd/slb

%install
install -Dpm0755 %{name} %{buildroot}%{_bindir}/%{name}
./%{name} completion bash | install -Dm0644 /dev/stdin %{buildroot}%{bash_completions_dir}/slb
./%{name} completion zsh | install -Dm0644 /dev/stdin %{buildroot}%{zsh_completions_dir}/_slb
./%{name} completion fish | install -Dm0644 /dev/stdin %{buildroot}%{fish_completions_dir}/slb.fish

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}
%{bash_completions_dir}/slb
%{zsh_completions_dir}/_slb
%{fish_completions_dir}/slb.fish

%changelog
* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.5.2-1
- Initial package
