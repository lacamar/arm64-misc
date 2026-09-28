%global debug_package %{nil}
%global _smp_ncpus_max 4
%global rustflags_debuginfo 0
%global rustflags_codegen_units 16

Name:           ms
Version:        0.2.2
Release:        1%{?dist}
Summary:        Mine coding agent sessions into Claude Code skills

License:        MIT
URL:            https://github.com/Dicklesworthstone/meta_skill
Source0:        %{url}/archive/v%{version}/meta_skill-%{version}.tar.gz

BuildRequires:  cargo
BuildRequires:  anda-srpm-macros
BuildRequires:  cargo-rpm-macros
BuildRequires:  gcc
BuildRequires:  openssl-devel
BuildRequires:  git-core

%description
Meta Skill: a CLI to mine CASS coding agent sessions and manage, search and
generate Claude Code skills.

%prep
%autosetup -n meta_skill-%{version}
rm rust-toolchain.toml

%build
%cargo_prep_online
export CARGO_PROFILE_RPM_LTO=thin
export OPENSSL_NO_VENDOR=1
%cargo_build

%install
install -Dpsm0755 target/rpm/%{name} %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}

%changelog
* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.2.2-1
- Initial package
