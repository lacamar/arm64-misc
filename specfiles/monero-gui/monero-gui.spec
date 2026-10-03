%global tag 0.18.5.2

Name: monero-gui
Version: %{tag}
Release: 1%{?dist}
Summary: Monero: the secure, private, untraceable cryptocurrency

License: Monero Project
URL: https://github.com/monero-project/monero-gui
Source0: https://github.com/monero-project/monero-gui/archive/refs/tags/v%{version}.tar.gz

Patch0: net_ssl-openssl-const.patch

%{lua:
local externals = {
  { name="monero",        ref="4f92268", owner="monero-project", path="", version="0.18.5.1", license="BSD-3-Clause" },
  { name="quirc",         ref="927d680", owner="dlbeer", path="../external/quirc", license="ISC License" },
  { name="miniupnp",      ref="544e6fc", owner="miniupnp", path="external/miniupnp", version="2.2.1", license="BSD-3-Clause" },
  { name="RandomX",       ref="6c4340b", owner="tevador", path="external/randomx", version="1.2.2", license="BSD-3-Clause" },
  { name="rapidjson",     ref="129d19b", owner="Tencent", path="external/rapidjson", version="1.1.0", license="MIT" },
  { name="supercop",      ref="633500a", owner="monero-project", path="external/supercop" },
  { name="trezor-common", ref="bff7fdf", owner="trezor", path="external/trezor-common", license="LGPLv3" },
}

for i, s in ipairs(externals) do
  print(string.format("Source%d: https://github.com/%s/%s/archive/%s/%s-%s.tar.gz", 100 + i, s.owner, s.name, s.ref, s.name, s.ref).."\n")
  print(string.format("Provides: bundled(%s) = %s", s.name, (s.version or "0")).."\n")
end

function print_setup_externals()
  for i, s in ipairs(externals) do
    print(string.format("mkdir -p monero/%s", s.path).."\n")
    print(string.format("tar -xzf %s --strip-components=1 -C monero/%s", rpm.expand("%{SOURCE"..(100 + i).."}"), s.path).."\n")
  end
end
}

BuildRequires:  make
BuildRequires:  automake
BuildRequires:  cmake
BuildRequires:  gcc-c++
BuildRequires:  boost-devel
BuildRequires:  miniupnpc-devel
BuildRequires:  graphviz
BuildRequires:  doxygen
BuildRequires:  unbound-devel
BuildRequires:  libunwind-devel
BuildRequires:  pkgconfig
BuildRequires:  openssl-devel
BuildRequires:  libcurl-devel
BuildRequires:  hidapi-devel
BuildRequires:  zeromq-devel
BuildRequires:  libgcrypt-devel
BuildRequires:  git
BuildRequires:  libX11-devel
BuildRequires:  libXScrnSaver-devel
BuildRequires:  libXxf86vm-devel
BuildRequires:  libxkbfile-devel
BuildRequires:  libXv-devel
BuildRequires:  qt5-qtbase-devel
BuildRequires:  qt5-qtsvg-devel
BuildRequires:  qt5-qttools-devel
BuildRequires:  qt5-qtdeclarative-devel
BuildRequires:  readline-devel
BuildRequires:  protobuf-devel
BuildRequires:  qt5-linguist

Requires:   systemd
Requires:   qt5-qtquickcontrols
Requires:   qt5-qtquickcontrols2
Requires:   qt5-qtxmlpatterns

%description
Monero is a private, secure, untraceable, decentralised digital currency. You are your bank, you control your funds, and nobody can trace your transfers unless you allow them to do so.

%prep
%autosetup -N

%{lua: print_setup_externals()}

%patch -P0 -p1


%build
cmake -B %{__cmake_builddir} \
  -DCMAKE_INSTALL_PREFIX=%{_prefix} \
  -DCMAKE_INSTALL_LIBDIR=%{_libdir} \
  -D CMAKE_BUILD_TYPE=Release \
  -Wno-dev \
  -D CMAKE_POLICY_DEFAULT_CMP0077=NEW \
  -D CMAKE_POLICY_DEFAULT_CMP0148=OLD \
  -D CMAKE_POLICY_DEFAULT_CMP0167=NEW
%cmake_build


%install
%cmake_install
mv %{buildroot}%{_prefix}/lib %{buildroot}%{_libdir}
install -Dpm0644 -t %{buildroot}%{_datadir}/applications share/org.getmonero.Monero.desktop


%files
%license LICENSE*
%doc    README*

%{_bindir}/monero*
%{_datadir}/applications/*

%{_includedir}/wallet/api/*.h
%{_libdir}/libepee.a
%{_libdir}/libepee_readline.a
%{_libdir}/libeasylogging.a
%{_libdir}/liblmdb.a


%changelog
* Fri Jul 17 2026 Lachlan Marie <lchlnm@pm.me> - 0.18.5.2-1
 - Update to 0.18.5.2

* Thu Jul 09 2026 Lachlan Marie <lchlnm@pm.me> - 0.18.5.1-1
 - Update to 0.18.5.1

 - Added a patch to fix a build error related to OpenSSL

* Mon Jun 22 2026 Lachlan Marie <lchlnm@pm.me> - 0.18.5.0-1
 - Update to 0.18.5.0

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 0.18.4.6-1
 - Update to 0.18.4.7

* Wed Nov 19 2025 Lachlan Marie <lchlnm@pm.me> - 0.18.4.4-1
- Increased version to 0.18.4.4.

* Mon Aug 11 2025 Lachlan Marie <lchlnm@pm.me> - 0.18.4.1-1
- Increased version to 0.18.4.1, updated source gathering process.

* Mon Jun 23 2025 Lachlan Marie <lchlnm@pm.me> - 0.18.4.0-1
- Initial RPM packaging of monero-gui
