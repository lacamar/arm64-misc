%global debug_package %{nil}
%global __requires_exclude_from ^%{_libdir}/%{name}/.*$
%if 0%{?fedora} >= 45
%global dotnet_ver 10.0
%else
%global dotnet_ver 9.0
%endif

Name:           steamless
Version:        3.1.0.5
Release:        2%{?dist}
Summary:        SteamStub DRM remover (CLI)

License:        CC-BY-NC-ND-4.0
URL:            https://github.com/atom0s/Steamless
Source0:        %{url}/archive/v%{version}/Steamless-%{version}.tar.gz

Patch0:         0001-linux-cli-build.patch
Patch1:         0002-variant21-no-code-section-info.patch

ExclusiveArch:  aarch64 x86_64

BuildRequires:  dotnet-sdk-%{dotnet_ver}
Requires:       dotnet-runtime-%{dotnet_ver}

%description
Steamless removes the SteamStub DRM layer applied via the Steamworks SDK
DRM tool. Command line interface built for .NET on Linux.

%prep
%autosetup -p1 -n Steamless-%{version}
sed -i 's/net9\.0/net%{dotnet_ver}/' linux/Directory.Build.props

%build
export DOTNET_CLI_HOME=$PWD/.dotnet
export DOTNET_NOLOGO=1
export DOTNET_CLI_TELEMETRY_OPTOUT=1
export DOTNET_SKIP_FIRST_TIME_EXPERIENCE=1
dotnet build -c Release linux/Steamless.Linux.sln

%install
install -d %{buildroot}%{_libdir}/%{name}/Plugins
install -pm0644 linux/bin/*.dll linux/bin/*.json %{buildroot}%{_libdir}/%{name}/
install -pm0755 linux/bin/Steamless.CLI %{buildroot}%{_libdir}/%{name}/
install -pm0644 linux/bin/Plugins/*.dll linux/bin/Plugins/*.json %{buildroot}%{_libdir}/%{name}/Plugins/
install -d %{buildroot}%{_bindir}
ln -s ../%{_lib}/%{name}/Steamless.CLI %{buildroot}%{_bindir}/%{name}

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_libdir}/%{name}

%changelog
* Mon Nov 16 2026 Lachlan Marie <lchlnm@pm.me> - 3.1.0.5-2
- Build with .NET 10 on f45+

* Wed Sep 30 2026 Lachlan Marie <lchlnm@pm.me> - 3.1.0.5-1
- Initial package
- Linux CLI build
- Fix Variant 2.1 stubs without code section info
