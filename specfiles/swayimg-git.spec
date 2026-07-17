%global _name swayimg
%global tag 5.4
%global bumpver 5

%global commit 133455f08147fcc9349f52d071058f4277190610
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:           %{_name}-git
Version:        %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:        1%{?dist}
Conflicts:      %{_name}
Provides:       %{_name} = %{version}-%{release}
Summary:        Lightweight image viewer for Wayland display servers

License:        MIT
URL:            https://github.com/artemsen/%{_name}
Source:         %{url}/archive/%{shortcommit}/%{_name}-%{shortcommit}.tar.gz

# Patch0:          #{url}/commit/5c2d958.patch#/swayimg-5.0-missing-includes.patch

# Exclude x86 and all the platforms where luajit is not available
ExcludeArch:    %{ix86} riscv64 ppc64 ppc64le

BuildRequires:  desktop-file-utils
BuildRequires:  gcc-c++
%if %{with tests}
BuildRequires:  glibc-langpack-en
%endif
BuildRequires:  meson >= 1.1

BuildRequires:  giflib-devel
# BuildRequires:  pkgconfig(OpenEXR) >= 3.4
BuildRequires:  pkgconfig(bash-completion)
BuildRequires:  pkgconfig(exiv2)
BuildRequires:  pkgconfig(fontconfig)
BuildRequires:  pkgconfig(freetype2)
%if %{with tests}
BuildRequires:  pkgconfig(gtest)
%endif
BuildRequires:  pkgconfig(libavif)
BuildRequires:  pkgconfig(libdrm)
BuildRequires:  pkgconfig(libheif)
BuildRequires:  pkgconfig(libjpeg)
BuildRequires:  pkgconfig(libjxl)
BuildRequires:  pkgconfig(libpng)
BuildRequires:  pkgconfig(libraw)
BuildRequires:  pkgconfig(librsvg-2.0) >= 2.46
BuildRequires:  pkgconfig(libsixel)
BuildRequires:  pkgconfig(libtiff-4)
BuildRequires:  pkgconfig(libwebp)
BuildRequires:  pkgconfig(libwebpdemux)
BuildRequires:  pkgconfig(luajit)
BuildRequires:  pkgconfig(wayland-client)
BuildRequires:  pkgconfig(wayland-protocols) >= 1.35
BuildRequires:  pkgconfig(wayland-scanner)
BuildRequires:  pkgconfig(xkbcommon)

Requires:       hicolor-icon-theme

# src/external/json: MIT
Provides:       bundled(json) = 3.12.0
# src/external/luabridge: MIT
Provides:       bundled(luabridge) = 3.0~rc4^20240929g713c1f5

%description
Swayimg is a lightweight image viewer for Wayland display servers.


%prep
%autosetup -n %{_name}-%{commit}
#patch -P 0 -p1 -F3


%build
%meson \
    -Dexr=disabled \
    -Dlicense=false \
    -Dtests=%[%{with tests}?"enabled":"disabled"] \
    -Dversion=%{version}
%meson_build


%install
%meson_install


%check
desktop-file-validate %{buildroot}%{_datadir}/applications/swayimg.desktop
%if %{with tests}
%ifarch s390x
# A few tests fail on s390x (endianness?)
%global gtest_exclude ImageLoadTest.*
%else
# HEIF test requires libheif-freeworld from rpmfusion
%global gtest_exclude ImageLoadTest.heif
%endif

export LANG=en_US.UTF-8 # ImageListTest.SortAlphaUnicode fails with LANG=C
%meson_test --test-args='--gtest_filter=-%{gtest_exclude}'
%endif


%files
%license LICENSE
%doc %{_datadir}/doc/%{_name}/*.md
%{_bindir}/swayimg
%{_mandir}/man1/swayimg.1*
%{_datadir}/applications/swayimg.desktop
%{_datadir}/icons/hicolor/*/apps/swayimg.png
%dir %{_datadir}/swayimg
%{_datadir}/swayimg/*.lua
%{bash_completions_dir}/swayimg
%{zsh_completions_dir}/_swayimg


%changelog
* Fri Jul 17 2026 Lachlan Marie <lchlnm@pm.me> - 5.4^5.git.133455f-1
 - Update to commit 133455f08147fcc9349f52d071058f4277190610

* Thu Jul 16 2026 Lachlan Marie <lchlnm@pm.me> - 5.4^4.git.c071ad6-1
 - Update to commit c071ad65f0424ee3acfeb3c36842afeeafdde7f0

* Fri Jul 10 2026 Lachlan Marie <lchlnm@pm.me> - 5.4^3.git.0ab573f-1
 - Update to commit 0ab573ff325bf1b39bf82d66d7e1c2a9685a0c7f

* Mon Jul 06 2026 Lachlan Marie <lchlnm@pm.me> - 5.4^2.git.44cc0f3-1
 - Update to commit 44cc0f33b89dd21a0605e064ab2764771ba5d178

* Sat Jun 27 2026 Lachlan Marie <lchlnm@pm.me> - 5.4^1.git.b248414-1
 - Update to commit b2484145c78e41d6dcbb862d7b1f58f60a70e583

* Sun Jun 21 2026 Lachlan Marie <lchlnm@pm.me> - 5.4^0.git.1d76a11-1
 - Update to 5.4

* Fri Jun 19 2026 Lachlan Marie <lchlnm@pm.me> - 5.3^1.git.a7c7ef8-1
 - Update to commit a7c7ef8c0c02407cfc2af343edf67026888e44f6

* Fri Jun 19 2026 Lachlan Marie <lchlnm@pm.me> - 5.3^0.git.f1aa000-1
 - Update to 5.3

* Wed Jun 17 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^30.git.f1aa000-1
 - Update to commit f1aa0005cf90ac40b4d89d4ee189dadfb631a048

* Tue Jun 16 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^29.git.daa1815-1
 - Update to commit daa1815b79d97bb434332449eb427a3c4227a43f

* Mon Jun 15 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^28.git.2b2f953-1
 - Update to commit 2b2f953014fe8529cbd43c78353cbb4b4d5bde46

* Mon Jun 15 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^27.git.e58f50f-1
 - Update to commit e58f50f56cf2c44b2ad27e4d9f108d80f6da63ce

* Sat Jun 13 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^26.git.c3bff68-1
 - Update to commit c3bff680aa8a9b916563960b266b8e0594ac7f25

* Fri Jun 12 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^25.git.20960c5-1
 - Update to commit 20960c531c30cefe65f34f86e67e23cf57f4d264

* Fri Jun 12 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^24.git.35f47b4-1
 - Update to commit 35f47b45d30cbb31cad98f6971a049100306c344

* Thu Jun 11 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^23.git.977ed0f-1
 - Update to commit 977ed0fefb605f48cdd392e1f405fb844994d972

* Wed Jun 10 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^22.git.65bed89-1
 - Update to commit 65bed89a84d35365a69cdc0d7aee95212c25c04c

* Mon Jun 08 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^21.git.a1eee74-1
 - Update to commit a1eee744ace797f7a03269d1b75688de8a120a4f

* Sat Jun 06 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^20.git.f75c080-1
 - Update to commit f75c080863587a0ffbce3dee4da51307c002520a

* Fri Jun 05 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^19.git.808217d-1
 - Update to commit 808217da92709fb3d4c896688e729130d6fe3115

* Fri Jun 05 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^18.git.9f83e2b-1
 - Update to commit 9f83e2b74ebad85af695dd0badd60b3c35050ab6

* Wed Jun 03 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^17.git.7ba2540-1
 - Update to commit 7ba2540879e56fddfebae3afe3875d9f2e093bfe

* Tue Jun 02 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^16.git.ecc930d-1
 - Update to commit ecc930d3a1eadf6c0ed623188620e4b367dd39ef

* Tue Jun 02 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^15.git.c9f5d75-1
 - Update to commit c9f5d759365f6bca4687c161d1421d78abf8e9ef

* Mon Jun 01 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^14.git.bd9a9fb-1
 - Update to commit bd9a9fb69cecb9dd29f889691a77c93a03175ca3

* Sun May 31 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^13.git.8c9bb52-1
 - Update to commit 8c9bb52f1ad8a28c5315fa8eea2358cf5a23775f

* Sat May 30 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^12.git.efcee16-1
 - Update to commit efcee169bcc8179899a1d55d05e94c4f99c44f67

* Fri May 29 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^11.git.8e7b13f-1
 - Update to commit 8e7b13f79855f775fb09779eb830e0bd52a40e97

* Thu May 28 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^10.git.2e14662-1
 - Update to commit 2e14662aa7f20e0dc03ac74e36da268790f0afae

* Wed May 27 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^9.git.bdd4312-1
 - Update to commit bdd4312760a315fc0a4d7b210bad6187fa2292ac

* Tue May 26 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^8.git.58375f7-1
 - Update to commit 58375f7513c1280f146b606a19e0d3cbc3b481c1

* Mon May 25 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^7.git.7dbcb8c-1
 - Update to commit 7dbcb8c975ca9de7a5fdaaad6b9a3b89030d4d1e

* Sun May 24 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^6.git.7c491d4-1
 - Update to commit 7c491d4c716fa4dde614e8be58d6cb308802da48

* Thu May 21 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^5.git.da9870a-1
 - Update to commit da9870a08a4a145542cf803eeb7779758136a186

* Sat May 09 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^4.git.225d378-1
 - Update to commit 225d37833c1bfdeb67e8729f72b360f32f87c5f1

* Mon May 04 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^3.git.b67a587-1
 - Update to commit b67a587fbad8d07c3cf9150575b4b4b06b8a3031

* Sun May 03 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^2.git.f8564b0-1
 - Update to commit f8564b06a19b2e8ee03b8cf3b592bf0f15253cff

* Thu Apr 30 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^1.git.164e22e-1
 - Update to commit 164e22ee920411617d890078b51402a08220e975

* Thu Apr 30 2026 Lachlan Marie <lchlnm@pm.me> - 5.2^2.git.164e22e-1
 - Update to commit 164e22ee920411617d890078b51402a08220e975

* Thu Apr 09 2026 Lachlan Marie <lchlnm@pm.me> - 5.2-1
 - Update to 5.2

* Wed Mar 25 2026 Lachlan Marie <lchlnm@pm.me> - 5.1-1
 - Update to 5.1
