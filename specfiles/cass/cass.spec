%global debug_package %{nil}
%global _smp_ncpus_max 4
%global rustflags_debuginfo 0
%global rustflags_codegen_units 16

Name:           cass
Version:        0.9.0
Release:        1%{?dist}
Summary:        Unified TUI search over local coding agent histories

License:        MIT
URL:            https://github.com/Dicklesworthstone/coding_agent_session_search
Source0:        %{url}/archive/v%{version}/coding_agent_session_search-%{version}.tar.gz

BuildRequires:  cargo
BuildRequires:  anda-srpm-macros
BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc
BuildRequires:  openssl-devel

%description
Coding Agent Session Search: index and search conversation histories of
Claude Code, Codex, Cursor, Gemini and other coding agents from one TUI/CLI.

%prep
%autosetup -n coding_agent_session_search-%{version}
rm rust-toolchain.toml

%build
%cargo_prep_online
export OPENSSL_NO_VENDOR=1
export CARGO_PROFILE_RPM_LTO=thin
%cargo_build -- --bin %{name}

%install
install -Dpsm0755 target/rpm/%{name} %{buildroot}%{_bindir}/%{name}
target/rpm/%{name} completions bash > %{name}.bash
target/rpm/%{name} completions zsh > _%{name}
target/rpm/%{name} completions fish > %{name}.fish
target/rpm/%{name} man > %{name}.1
install -Dpm0644 %{name}.bash %{buildroot}%{bash_completions_dir}/%{name}
install -Dpm0644 _%{name} %{buildroot}%{zsh_completions_dir}/_%{name}
install -Dpm0644 %{name}.fish %{buildroot}%{fish_completions_dir}/%{name}.fish
install -Dpm0644 %{name}.1 %{buildroot}%{_mandir}/man1/%{name}.1

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}
%{bash_completions_dir}/%{name}
%{zsh_completions_dir}/_%{name}
%{fish_completions_dir}/%{name}.fish
%{_mandir}/man1/%{name}.1*

%changelog
* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.9.0-1
- Initial package
