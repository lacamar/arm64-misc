%global debug_package %{nil}
%global _smp_ncpus_max 4
%global rustflags_debuginfo 0
%global rustflags_codegen_units 16

Name:           xf
Version:        0.4.2
Release:        1%{?dist}
Summary:        Search and query X (Twitter) data archives

License:        MIT
URL:            https://github.com/Dicklesworthstone/xf
Source0:        %{url}/archive/v%{version}/xf-%{version}.tar.gz

BuildRequires:  cargo
BuildRequires:  anda-srpm-macros
BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  openssl-devel
BuildRequires:  git-core

%description
xf: fast CLI to index, search and query X (Twitter) data archive exports with
lexical and semantic search.

%prep
%autosetup -n xf-%{version}
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
* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.4.2-1
- Initial package
