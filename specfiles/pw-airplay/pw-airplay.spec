%global commit ff12df8f64fba33e77dacc9e7ed93901e353f928
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global owntone_version 29.3
%global engine %{_libexecdir}/pw-airplay

Name:           pw-airplay
Version:        0^20261017git%{shortcommit}
Release:        1%{?dist}
Summary:        AirPlay 2 output for PipeWire
License:        GPL-2.0-or-later
URL:            https://github.com/superlemon57/pw-airplay
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
Source1:        https://github.com/owntone/owntone-server/archive/%{owntone_version}/owntone-server-%{owntone_version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  libtool
BuildRequires:  gettext-devel
BuildRequires:  gperf
BuildRequires:  bison
BuildRequires:  flex
BuildRequires:  systemd-rpm-macros
BuildRequires:  pkgconfig(libpipewire-0.3)
BuildRequires:  pkgconfig(libcurl)
BuildRequires:  pkgconfig(json-c)
BuildRequires:  pkgconfig(avahi-client)
BuildRequires:  pkgconfig(libsystemd)
BuildRequires:  pkgconfig(zlib)
BuildRequires:  pkgconfig(libconfuse)
BuildRequires:  pkgconfig(libsodium)
BuildRequires:  pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(sqlite3)
BuildRequires:  pkgconfig(libevent)
BuildRequires:  pkgconfig(libplist-2.0)
BuildRequires:  pkgconfig(libavcodec)
BuildRequires:  pkgconfig(libavformat)
BuildRequires:  pkgconfig(libavfilter)
BuildRequires:  pkgconfig(libavutil)
BuildRequires:  pkgconfig(libswscale)
BuildRequires:  pkgconfig(gnutls)
BuildRequires:  pkgconfig(libwebsockets)
BuildRequires:  pkgconfig(alsa)
BuildRequires:  pkgconfig(libgcrypt)
BuildRequires:  libunistring-devel

Requires:       pipewire
Requires:       avahi

%description
AirPlay 2 speakers appear as PipeWire outputs. Uses a patched OwnTone as
the sender engine and airptpd as PTP clock.

%prep
%autosetup -n %{name}-%{commit}
mkdir owntone
tar -xzf %{SOURCE1} -C owntone --strip-components=1
patch -p1 -d owntone <engine/owntone-%{owntone_version}.patch

%build
cd owntone
autoreconf -fi
%configure --prefix=%{engine} --sbindir=%{engine}/sbin --sysconfdir=%{_sysconfdir} \
    --localstatedir=%{_localstatedir} --disable-chromecast --disable-spotify --disable-mpd
%make_build
(cd src/libairptp && %configure --prefix=%{engine} --sbindir=%{engine}/sbin --enable-daemon && %make_build)
cd ..
CFLAGS="%{build_cflags}" LDFLAGS="%{build_ldflags}" %make_build

%install
install -Dm755 owntone/src/owntone %{buildroot}%{engine}/sbin/owntone
install -Dm755 owntone/src/libairptp/daemon/airptpd %{buildroot}%{engine}/sbin/airptpd
install -Dm755 pw-airplayd %{buildroot}%{_bindir}/pw-airplayd
install -Dm644 config/pw-airplay.conf %{buildroot}%{_datadir}/%{name}/pw-airplay.conf
install -Dm644 config/50-pw-airplay-no-raop.conf %{buildroot}%{_sysconfdir}/pipewire/pipewire.conf.d/50-pw-airplay-no-raop.conf
for u in pw-airplay-engine pw-airplay; do
    sed -e 's|@PREFIX@|%{_prefix}|g' -e 's|@ENGINE@|%{engine}/sbin/owntone|g' \
        systemd/$u.service | install -Dm644 /dev/stdin %{buildroot}%{_userunitdir}/$u.service
done
sed -e 's|/usr/local/sbin/airptpd|%{engine}/sbin/airptpd|' -e '/^After=/a Conflicts=nqptp.service' \
    systemd/airptpd.service | install -Dm644 /dev/stdin %{buildroot}%{_unitdir}/airptpd.service

%post
%systemd_post airptpd.service
%systemd_user_post pw-airplay-engine.service pw-airplay.service

%preun
%systemd_preun airptpd.service
%systemd_user_preun pw-airplay-engine.service pw-airplay.service

%postun
%systemd_postun_with_restart airptpd.service

%files
%license LICENSE
%license owntone/COPYING
%doc README.md
%{_bindir}/pw-airplayd
%{engine}/
%{_datadir}/%{name}/
%{_unitdir}/airptpd.service
%{_userunitdir}/pw-airplay-engine.service
%{_userunitdir}/pw-airplay.service
%config(noreplace) %{_sysconfdir}/pipewire/pipewire.conf.d/50-pw-airplay-no-raop.conf

%changelog
* Mon Oct 26 2026 Lachlan Marie <lchlnm@pm.me> - 0^20261017gitff12df8-1
- Initial package
- Bundle patched OwnTone 29.3 engine and airptpd
