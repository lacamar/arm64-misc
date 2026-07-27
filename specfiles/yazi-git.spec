%undefine __brp_mangle_shebangs

%global bumpver 39
%global _name yazi
%global tag 26.1.22
%global commit cd6e61666d14d49b12a112d78f1b6b260c29d73a
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name: %{_name}-git
Version: %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release: 2%{?dist}
Conflicts: %{_name}
Provides: %{_name} = %{version}-%{release}

Summary: Blazing fast terminal file manager written in Rust, based on async I/O
URL: https://yazi-rs.github.io/
Source0: https://github.com/sxyazi/%{_name}/archive/%{commit}/%{_name}-%{commit}.tar.gz

License: MIT AND (MIT OR Apache-2.0) AND NCSA AND Unicode-3.0 AND (0BSD OR MIT OR Apache-2.0) AND Apache-2.0 AND ISC AND (Apache-2.0 OR BSL-1.0) AND (Apache-2.0 OR MIT) AND (Apache-2.0 WITH LLVM-exception OR Apache-2.0 OR MIT) AND BSD-2-Clause AND BSD-3-Clause AND (BSD-2-Clause OR Apache-2.0 OR MIT) AND (BSD-3-Clause OR Apache-2.0) AND BSL-1.0 AND CC0-1.0 AND (CC0-1.0 OR Apache-2.0) AND ISC AND (MIT OR Apache-2.0 OR BSD-1-Clause) AND (MIT OR Apache-2.0 OR CC0-1.0) AND (MIT OR Apache-2.0 OR LGPL-2.1-or-later) AND (MIT OR Apache-2.0 OR Zlib) AND (MIT OR Zlib OR Apache-2.0) AND MPL-2.0 AND (Unlicense OR MIT) AND Zlib AND (Zlib OR Apache-2.0 OR MIT)

BuildRequires: cargo
BuildRequires: anda-srpm-macros
BuildRequires: cargo-rpm-macros
BuildRequires: mold

Packager: Owen Zimmerman owen@fyralabs.com

%description
Yazi (means "duck") is a terminal file manager written in Rust, based on non-blocking async I/O.

%prep
%autosetup -n %{_name}-%{commit}
%cargo_prep_online

git init
git config user.email "builder@example.invalid"
git config user.name "RPM Builder"
git add .
git commit -qm "snapshot"

export VERGEN_GIT_SHA=%{shortcommit}

%build
export VERGEN_GIT_SHA=%{shortcommit}
%cargo_build

%install
rm -rf %{buildroot}

install -Dm755 target/rpm/ya %{buildroot}%{_bindir}/ya
install -Dm755 target/rpm/yazi %{buildroot}%{_bindir}/yazi

install -Dm644 assets/logo.png \
  %{buildroot}%{_hicolordir}/1024x1024/apps/yazi.png

install -Dm644 assets/yazi.desktop \
  %{buildroot}%{_appsdir}/yazi.desktop

%files
%license LICENSE LICENSE-ICONS
%doc README.md CODE_OF_CONDUCT.md CONTRIBUTING.md

%{_bindir}/ya
%{_bindir}/yazi

%{_hicolordir}/1024x1024/apps/yazi.png
%{_appsdir}/yazi.desktop


%changelog
* Mon Jul 27 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^39.git.cd6e616-2
 - Update to commit cd6e61666d14d49b12a112d78f1b6b260c29d73a

* Sun Jul 26 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^38.git.e7fa4d2-2
 - Update to commit e7fa4d215ae0773e6a60b04ea7aa7aae0d6beaf7

* Sun Jul 26 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^37.git.d30866d-2
 - Update to commit d30866dbb22e9ee50226bb65c6cec72dbce5ad98

* Fri Jul 24 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^36.git.58f1013-2
 - Update to commit 58f1013348c969538352e3105f58e8d8e870a092

* Wed Jul 22 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^35.git.9accf92-2
 - Update to commit 9accf929f47e11dc4b0a7b574308b945301165ca

* Tue Jul 21 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^34.git.6aa7559-2
 - Update to commit 6aa75594dbea287001c823853235e6a4f9d45997

* Sun Jul 19 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^33.git.60d9460-2
 - Update to commit 60d94608cb050f68c5ce85b7e236f0e5b121538d

* Thu Jul 16 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^32.git.52640fc-2
 - Update to commit 52640fcecea337d2a17307201f71fd4a7c7a61b0

* Mon Jul 13 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^31.git.b25ae9f-2
 - Update to commit b25ae9f82d415da7fbd4d4e4b09397a194540a09

* Mon Jul 13 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^30.git.ddc6632-2
 - Update to commit ddc6632505064ab8b393e247a19b62a4668ed9eb

* Mon Jul 13 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^29.git.6d84921-2
 - Update to commit 6d84921e7004eb8d49ba13a4acc97c6cfeb094b4

* Thu Jul 09 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^28.git.dbb0cc0-2
 - Update to commit dbb0cc0d556d73935ebdc1e3d61a2a8aa27059d2

* Tue Jul 07 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^27.git.aa850f9-2
 - Update to commit aa850f9a3bece5fa353b45adea9eee59fc7e6996

* Mon Jul 06 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^26.git.c92c4ab-2
 - Update to commit c92c4aba884c16d318a92f6bc0517ee0d2bcc414

* Thu Jul 02 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^25.git.b8ceaea-2
 - Update to commit b8ceaea9407b96a05eafbb752a877290ad50317b

* Sun Jun 28 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^24.git.21550a7-2
 - Update to commit 21550a7eb5086ba34f8eabf8aaab85f601d34a74

* Sun Jun 28 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^23.git.b23ad81-2
 - Update to commit b23ad8114d9a4f08f247832fad59a03316278241

* Sat Jun 27 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^22.git.39527f4-2
 - Update to commit 39527f488f6514a13d0edd88a94147931ddcbb2a

* Fri Jun 26 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^21.git.bf12743-2
 - Update to commit bf1274315dbcef858b46a55f212cfa34b916c3d3

* Thu Jun 25 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^20.git.ef654f4-2
 - Update to commit ef654f442060c3a4feae6d89f8b9ddf300d54ecc

* Tue Jun 23 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^19.git.581886a-2
 - Update to commit 581886a3552e9e9ea0b3f7bc173f7127ecfd6a22

* Sun Jun 21 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^18.git.4f45ddb-2
 - Update to commit 4f45ddb514c3db558da0c5fffabaaa44f18cc18e

* Sat Jun 20 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^17.git.0ba1811-2
 - Update to commit 0ba1811af39e26fa3a8b78059a1e9bf053d0eb30

* Sat Jun 20 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^16.git.ef5db6e-2
 - Update to commit ef5db6e257134963a52ca2e43a5b3ada4caaf7fe

* Sat Jun 20 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^15.git.84a5be0-2
 - Update to commit 84a5be0b6a05464b2601f6194c74c0ea8160e6a9

* Fri Jun 19 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^14.git.ab8d634-2
 - Update to commit ab8d634f8e8a1f1d45d91f19942efb41bb93ab2e

* Fri Jun 19 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^13.git.85132ff-2
 - Update to commit 85132ff343327c8873117e5e3588857e3e22b66d

* Thu Jun 18 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^12.git.446a572-2
 - Update to commit 446a5721bf5c607e67e92e44b461f7fd4c62f488

* Wed Jun 17 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^11.git.f1e93d7-2
 - Update to commit f1e93d7f528b22fdeaf66b198c73e32a7040a90c

* Thu Jun 11 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^10.git.9b920ed-1
 - Update to commit 9b920ed2e3ebc126cf8ba3e51acfc5be8b8cbf56

* Wed Jun 10 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^9.git.07a5deb-1
 - Update to commit 07a5deb1095321917e172770fc1630a57dedce52

* Wed Jun 10 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^8.git.9cfeb67-1
 - Update to commit 9cfeb67db70241992bad181c3969dbae5f5fd019

* Sun Jun 07 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^7.git.f6113d3-1
 - Update to commit f6113d386539a07d4ae23d24595e603bc0be0343

* Sat Jun 06 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^6.git.ea7fa21-1
 - Update to commit ea7fa2127cc032b669a4825157ace244f06cf31c

* Wed Jun 03 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^5.git.8e80798-1
 - Update to commit 8e80798984864799cd72b3625b21edc33b1ba1e5

* Sun May 10 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^4.git.247f925-1
 - Update to commit 247f925e532236aa4e0dc6ac1a3e0a0263083ce6

* Sat May 09 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^3.git.92b9ea3-1
 - Update to commit 92b9ea37945ed128a79ea96d58e182d9d09b7fd1

* Fri May 08 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^2.git.3968c47-1
 - Update to commit 3968c4799cde1d97af3ad512acc33ea891298da5

* Wed May 06 2026 Lachlan Marie <lchlnm@pm.me> - 26.1.22^1.git.aa52643-1
 - Update to commit aa526434f00bb44e2e902d9a4ac5f810da1018b9

* Sat Dec 27 2025 Owen Zimmerman <owen@fyralabs.com>
- Initial commit
