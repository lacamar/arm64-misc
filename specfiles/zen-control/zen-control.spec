%global __brp_mangle_shebangs_exclude_from ^%{_prefix}/lib/%{name}/node_modules/.*$
%global __requires_exclude_from ^%{_prefix}/lib/%{name}/node_modules/.*$
%global __provides_exclude_from ^%{_prefix}/lib/%{name}/node_modules/.*$

%global tag 0.1.2
%global bumpver 0
%global commit 4de1d80837c5cbd4ca30e6225b6b99608b969030
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:           zen-control
Version:        %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:        2%{?dist}
Summary:        MCP bridge and WebExtension to drive the Zen browser from Claude Code

License:        LicenseRef-Not-specified
URL:            https://github.com/zjones2142/zen-control
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz

Patch0:         0001-chrome-parity-tools.patch

BuildArch:      noarch

BuildRequires:  nodejs >= 18
BuildRequires:  nodejs-npm
Requires:       nodejs >= 18
Requires:       zen-browser

%description
Lets Claude Code drive the Zen browser (Firefox-based) through a local MCP
server and a WebExtension connected over ws://127.0.0.1:17373. The unsigned
extension is installed through an enterprise policy and needs xpinstall.signatures.required
set to false.

%prep
%autosetup -p1 -n %{name}-%{commit}

%build
export npm_config_cache=$PWD/.npm-cache
npm ci --omit=dev --ignore-scripts --no-audit --no-fund
node build-xpi.mjs

%install
install -dm0755 %{buildroot}%{_prefix}/lib/%{name}
cp -a package.json server node_modules %{buildroot}%{_prefix}/lib/%{name}/
install -Dpm0644 zen-control.xpi %{buildroot}%{_datadir}/%{name}/zen-control.xpi
# Zen is built without sideloading; this file replaces /opt/zen/distribution/policies.json
install -dm0755 %{buildroot}%{_sysconfdir}/zen/policies
cat > %{buildroot}%{_sysconfdir}/zen/policies/policies.json <<'EOS'
{
  "policies": {
    "DisableAppUpdate": true,
    "ExtensionSettings": {
      "zen-control@local": {
        "installation_mode": "normal_installed",
        "install_url": "file://%{_datadir}/%{name}/zen-control.xpi"
      }
    }
  }
}
EOS
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
%{_datadir}/%{name}
%dir %{_sysconfdir}/zen
%dir %{_sysconfdir}/zen/policies
%config(noreplace) %{_sysconfdir}/zen/policies/policies.json

%changelog
* Wed Sep 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.2^0.git.4de1d80-2
- Add file and image upload
- Add network request log
- Add GIF recording
- Add window resize
- Add batch actions and shortcuts
- Add multi-browser selection
- Add per-site permissions

* Wed Sep 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.2^0.git.4de1d80-1
- Use bumpver counter so commit updates sort correctly

* Wed Sep 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.2^git.4de1d80-2
- Install extension via enterprise policy
- Drop system-scope sideload

* Wed Sep 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.2^git.4de1d80-1
- Initial package
