%global debug_package %{nil}
%global _smp_ncpus_max 4
%global rustflags_debuginfo 0
%global rustflags_codegen_units 16

Name:           dcg
Version:        0.14.4
Release:        1%{?dist}
Summary:        Block destructive commands run by AI coding agents

License:        MIT
URL:            https://github.com/Dicklesworthstone/destructive_command_guard
Source0:        %{url}/archive/v%{version}/destructive_command_guard-%{version}.tar.gz

BuildRequires:  cargo
BuildRequires:  anda-srpm-macros
BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc
BuildRequires:  gcc-c++

%description
Destructive Command Guard: a pre-execution hook for Claude Code, Codex and
other coding agents that blocks destructive shell, git and database commands.

%prep
%autosetup -n destructive_command_guard-%{version}
rm rust-toolchain.toml

%build
%cargo_prep_online
export CARGO_PROFILE_RPM_LTO=thin
%cargo_build

%install
install -Dpsm0755 target/rpm/%{name} %{buildroot}%{_bindir}/%{name}
target/rpm/%{name} completions bash > %{name}.bash
target/rpm/%{name} completions zsh > _%{name}
target/rpm/%{name} completions fish > %{name}.fish
install -Dpm0644 %{name}.bash %{buildroot}%{bash_completions_dir}/%{name}
install -Dpm0644 _%{name} %{buildroot}%{zsh_completions_dir}/_%{name}
install -Dpm0644 %{name}.fish %{buildroot}%{fish_completions_dir}/%{name}.fish

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}
%{bash_completions_dir}/%{name}
%{zsh_completions_dir}/_%{name}
%{fish_completions_dir}/%{name}.fish

%changelog
* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.14.4-1
- Initial package
