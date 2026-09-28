%global debug_package %{nil}
%global __strip /bin/true

Name:           s2p
Version:        0.3.4
Release:        1%{?dist}
Summary:        TUI for combining source files into LLM-ready prompts

License:        MIT
URL:            https://github.com/Dicklesworthstone/source_to_prompt_tui
Source0:        %{url}/archive/v%{version}/source_to_prompt_tui-%{version}.tar.gz

BuildRequires:  nodejs-npm

Conflicts:      perl-App-s2p

%description
Source to Prompt TUI: select files from a project tree and combine them into
a single prompt with token counting, presets and minification.

%prep
%autosetup -n source_to_prompt_tui-%{version}

%build
npm install --no-save --prefix .bun bun
export PATH=$PWD/.bun/node_modules/.bin:$PATH
bun install --frozen-lockfile
bun build src/index.tsx --compile --minify --outfile %{name}

%install
install -Dpm0755 %{name} %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md CHANGELOG.md
%{_bindir}/%{name}

%changelog
* Mon Sep 28 2026 Lachlan Marie <lchlnm@pm.me> - 0.3.4-1
- Initial package
