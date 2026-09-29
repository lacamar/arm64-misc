%global __brp_mangle_shebangs_exclude_from ^%{_prefix}/lib/%{name}/node_modules/.*$
%global __requires_exclude_from ^%{_prefix}/lib/%{name}/node_modules/.*$
%global __provides_exclude_from ^%{_prefix}/lib/%{name}/node_modules/.*$

%global tag 0.1.2
%global firefox_app_id \{ec8030f7-c20a-464f-9b0e-13a3a9e97384\}
%global zen_dir /opt/zen
%global commit 4de1d80837c5cbd4ca30e6225b6b99608b969030
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:           zen-control
Version:        %{tag}^git.%{shortcommit}
Release:        1%{?dist}
Summary:        MCP bridge and WebExtension to drive the Zen browser from Claude Code

License:        LicenseRef-Not-specified
URL:            https://github.com/zjones2142/zen-control
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

BuildArch:      noarch

BuildRequires:  nodejs >= 18
BuildRequires:  nodejs-npm
Requires:       nodejs >= 18
Requires:       zen-browser

%description
Lets Claude Code drive the Zen browser (Firefox-based) through a local MCP
server and a WebExtension connected over ws://127.0.0.1:17373. The unsigned
extension is sideloaded system-wide and needs xpinstall.signatures.required
set to false.

%prep
%autosetup -n %{name}-%{commit}

%build
export npm_config_cache=$PWD/.npm-cache
npm ci --omit=dev --ignore-scripts --no-audit --no-fund
node build-xpi.mjs

%install
install -dm0755 %{buildroot}%{_prefix}/lib/%{name}
cp -a package.json server node_modules %{buildroot}%{_prefix}/lib/%{name}/
install -Dpm0644 zen-control.xpi %{buildroot}%{_datadir}/mozilla/extensions/%{firefox_app_id}/zen-control@local.xpi
# Rescan system add-ons each startup so package upgrades are picked up
install -dm0755 %{buildroot}%{zen_dir}/defaults/pref
echo 'pref("extensions.startupScanScopes", 8);' > %{buildroot}%{zen_dir}/defaults/pref/zen-control.js
install -dm0755 %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/%{name} <<'EOS'
#!/bin/sh
exec /usr/bin/node %{_prefix}/lib/%{name}/server/index.js "$@"
EOS
chmod 0755 %{buildroot}%{_bindir}/%{name}

%files
%doc README.md
%{_bindir}/%{name}
%{_prefix}/lib/%{name}
%{_datadir}/mozilla/extensions/%{firefox_app_id}/zen-control@local.xpi
%{zen_dir}/defaults/pref/zen-control.js

%changelog
* Wed Sep 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.2^git.4de1d80-1
- Initial package
