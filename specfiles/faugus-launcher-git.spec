%global bumpver 3
%global _name faugus-launcher

%global tag 1.22.4

%global commit 7f6fc9b6f0ac4b03c22f1db129e53d450e1f459d
%{?commit:%global shortcommit %(c=%{commit}; echo ${c:0:7})}

Name:           faugus-launcher-git
Conflicts:      faugus-launcher
Provides:       faugus-launcher
Version:        %{tag}%{?bumpver:^%{bumpver}.git.%{shortcommit}}
Release:        1%{?dist}
Summary:        A simple and lightweight app for running Windows games using UMU-Launcher

License:        MIT
URL:            https://github.com/Faugus/%{_name}
Source0:        https://github.com/Faugus/%{_name}/archive/%{shortcommit}/%{_name}-%{shortcommit}.tar.gz

BuildArch:      noarch

BuildRequires:  meson
BuildRequires:  gtk-update-icon-cache
BuildRequires:  python3-devel
BuildRequires:  python3-rpm-macros

Requires:       python3
Requires:       python3-gobject
Requires:       python3-requests
Requires:       python3-icoextract
Requires:       python3-pillow
Requires:       python3-filelock
Requires:       python3-vdf
Requires:       python3-psutil
Requires:       umu-launcher
Requires:       ImageMagick
Requires:       libayatana-appindicator-gtk3
Requires:       mangohud
Requires:       gamemode

%description
A simple and lightweight app for running Windows games using UMU-Launcher/UMU-Proton.

%prep
%autosetup -n %{_name}-%{commit}

%build
%meson
%meson_build

%install
%meson_install

%files
%license LICENSE
%{_bindir}/faugus-launcher
%{_bindir}/faugus-run
#{_bindir}/faugus-proton-manager
#{_bindir}/faugus-shortcut
%{python3_sitelib}/faugus
%{_datadir}/applications/*.desktop
#{_datadir}/icons/hicolor/256x256/apps/*.png
#{_datadir}/icons/hicolor/256x256/apps/faugus-mono.svg
%{_datadir}/icons/hicolor/scalable/apps/faugus-launcher.svg
%{_datadir}/icons/hicolor/scalable/apps/faugus-mono.svg
%{_datadir}/icons/hicolor/scalable/apps/io.github.Faugus.faugus-launcher.svg
%{_datadir}/icons/hicolor/scalable/actions/*.svg
%{_datadir}/faugus-launcher/*
%{_datadir}/locale/*/LC_MESSAGES/*.mo
%{_datadir}/metainfo/faugus-launcher.metainfo.xml
%{_datadir}/licenses/faugus-launcher/LICENSE

%changelog
* Tue Jun 23 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.4^3.git.7f6fc9b-1
 - Update to commit 7f6fc9b6f0ac4b03c22f1db129e53d450e1f459d

* Mon Jun 22 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.4^2.git.105fd85-1
 - Update to commit 105fd859b2e493e19fbc7a25ae0a86aa0b30a853

* Sat Jun 20 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.4^1.git.fc160d3-1
 - Update to commit fc160d39099757abf9739100fab2ef1c0fbad4ee

* Mon Jun 15 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.4^0.git.1e4a8ec-1
 - Update to 1.22.4

* Sun Jun 14 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.2^4.git.d278a40-1
 - Update to commit d278a40fad1d1d5ad24bfd9d5c374956f29d9318

* Sat Jun 13 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.2^3.git.1116fe4-1
 - Update to commit 1116fe4c251fcc67034ca2c19ebc5ad6a3c41e7b

* Sat Jun 13 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.2^2.git.a8b83bc-1
 - Update to commit a8b83bc511ef47f5f83e02e3d67e18b7313b017f

* Fri Jun 12 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.2^1.git.dc841bd-1
 - Update to commit dc841bde0578c5b793862818947697085c998ee4

* Fri Jun 12 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.2^0.git.028bc47-1
 - Update to 1.22.2

* Thu Jun 11 2026 Lachlan Marie <lchlnm@pm.me> - 1.22.1^0.git.c953b8d-1
 - Update to 1.22.1

* Thu Jun 11 2026 Lachlan Marie <lchlnm@pm.me> - 1.21.1^10.git.8d9aa01-1
 - Update to commit 8d9aa01f7208a38a40a1c4c546e68f7f8e96623c

* Thu Jun 11 2026 Lachlan Marie <lchlnm@pm.me> - 1.21.1^9.git.74ef0c2-1
 - Update to commit 74ef0c206348e1dcccf5fa75aab8f0c33f8b7d0e

* Wed Jun 10 2026 Lachlan Marie <lchlnm@pm.me> - 1.21.1^8.git.294ac8d-1
 - Update to commit 294ac8d49e846ad837354b6b06da2cd197276404

* Wed Jun 10 2026 Lachlan Marie <lchlnm@pm.me> - 1.21.1^7.git.77582df-1
 - Update to commit 77582dfa3c9fec2b6a729ee4143a5ab0d1f0b411

* Wed Jun 10 2026 Lachlan Marie <lchlnm@pm.me> - 1.21.1^6.git.a98e420-1
 - Update to commit a98e420613fc278a715677f44f8a228a7de6f46d

* Wed Jun 10 2026 Lachlan Marie <lchlnm@pm.me> - 1.21.1^5.git.da702de-1
 - Update to commit da702deb894f8829b7e2722770e52e568831fa32

* Tue Jun 09 2026 Lachlan Marie <lchlnm@pm.me> - 1.21.1^4.git.b1da0e2-1
 - Update to commit b1da0e24f34ec92dbdedb23a52f59e38f73debe1

* Mon Jun 08 2026 Lachlan Marie <lchlnm@pm.me> - 1.21.1^3.git.89ab1be-1
 - Update to commit 89ab1be4b141454dfa6af5bb7b4da701819f1269

* Mon Jun 08 2026 Lachlan Marie <lchlnm@pm.me> - 1.21.1^2.git.b43cccc-1
 - Update to commit b43cccc0dc9bf78f9e2d162a7bcc05fa0a08b72d

* Sun Jun 07 2026 Lachlan Marie <lchlnm@pm.me> - 1.21.1^1.git.6907d83-1
 - Update to commit 6907d838db8d1181b3bbe3106e9d679384b49ed1

* Sat Jun 06 2026 Lachlan Marie <lchlnm@pm.me> - 1.21.1^0.git.5b9e551-1
 - Update to 1.21.1

* Fri Jun 05 2026 Lachlan Marie <lchlnm@pm.me> - 1.20.4^5.git.087add6-1
 - Update to commit 087add63c18e3a95f160749b84f5c46cfd2da505

* Fri Jun 05 2026 Lachlan Marie <lchlnm@pm.me> - 1.20.4^4.git.56ce450-1
 - Update to commit 56ce4506faceee42d98c013619ab61b6697c7b82

* Fri Jun 05 2026 Lachlan Marie <lchlnm@pm.me> - 1.20.4^3.git.cbb6582-1
 - Update to commit cbb65825a724b125d84adc671d1bd1664e58da86

* Wed Jun 03 2026 Lachlan Marie <lchlnm@pm.me> - 1.20.4^2.git.9cd93d7-1
 - Update to commit 9cd93d7795e0f7c596b94124fc9c6b937811aa99

* Sat May 30 2026 Lachlan Marie <lchlnm@pm.me> - 1.20.4^1.git.69c2a06-1
 - Update to commit 69c2a067ad30aae9e9baa455d7f992badb00618a

* Thu May 28 2026 Lachlan Marie <lchlnm@pm.me> - 1.20.4^0.git.5b24a94-1
 - Update to 1.20.4

* Tue May 26 2026 Lachlan Marie <lchlnm@pm.me> - 1.20.3^1.git.b2b48b4-1
 - Update to commit b2b48b4df06ed90b937b5cc09537bdd2309fd17b

* Mon May 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.20.3^0.git.ff3578a-1
 - Update to 1.20.3

* Sun May 24 2026 Lachlan Marie <lchlnm@pm.me> - 1.20.1^0.git.975d615-1
 - Update to 1.20.1

* Sun May 24 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.5^3.git.4e25ce0-1
 - Update to commit 4e25ce002245b74616156a1ba28e5a388dc4e231

* Thu May 21 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.5^2.git.80abd18-1
 - Update to commit 80abd18862c87ff11dda73fbf9636eec85238d2d

* Wed May 20 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.5^1.git.4133ad6-1
 - Update to commit 4133ad6711ec145f1dc852e605b6f3a677e2c894

* Tue May 19 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.5^0.git.eba4c15-1
 - Update to 1.19.5

* Mon May 18 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.4^4.git.768ac9b-1
 - Update to commit 768ac9b1145400e99789ef6ffd165ccd971ed940

* Mon May 18 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.4^3.git.aa203d2-1
 - Update to commit aa203d27ec3b699834139a32285e880899d27718

* Sat May 16 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.4^2.git.c9b61a8-1
 - Update to commit c9b61a8cb9ae8d120d496df18f50c3ae8b27c8cc

* Fri May 15 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.4^1.git.eef6540-1
 - Update to commit eef654087c10106136fedad59fa0f22a575b8e35

* Thu May 14 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.4^0.git.6dae347-1
 - Update to 1.19.4

* Tue May 12 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.3^3.git.ff8a538-1
 - Update to commit ff8a538f4477e1ac98a16369edb9bcb8f7d522dd

* Tue May 12 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.3^2.git.90d312c-1
 - Update to commit 90d312ce7a34aaa2fb46879332e3689cf767915c

* Mon May 11 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.3^1.git.dcc89e9-1
 - Update to commit dcc89e91114188381125cac39358e4d193de7217

* Mon May 11 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.3^0.git.dcc89e9-1
 - Update to 1.19.3

* Sun May 10 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.2^2.git.d114dac-1
 - Update to commit d114dac47231302f4dbc089d2b868b732adee28a

* Sun May 10 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.2^1.git.827afad-1
 - Update to commit 827afad73f603e84876f4c64cefd4b026ae4b973

* Sat May 09 2026 Lachlan Marie <lchlnm@pm.me> - 1.19.2^0.git.b5534ef-1
 - Update to 1.19.2

* Thu May 07 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.12^4.git.434de34-1
 - Update to commit 434de34e573a277dd85fddf4118340cbb4dc3acd

* Thu May 07 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.12^3.git.3d09310-1
 - Update to commit 3d09310c401952d87adbf146db17427684435a68

* Wed May 06 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.12^2.git.0458c06-1
 - Update to commit 0458c0605ddc5a56200e4a011d4d8c47c1e14616

* Tue May 05 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.12^1.git.20c57e6-1
 - Update to commit 20c57e6d4449c736d42cd38503ac8cab018238c6

* Mon May 04 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.12^0.git.a7f4247-1
 - Update to 1.18.12

* Mon May 04 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.11^0.git.33e533d-1
 - Update to 1.18.11

* Sun May 03 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.10^1.git.398d3eb-1
 - Update to commit 398d3ebbc99d5619df4116d7ec9bd388fb9f4a48

* Fri May 01 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.10^0.git.e5a4b24-1
 - Update to 1.18.10

* Thu Apr 30 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.8^0.git.e519bbb-1
 - Update to 1.18.8

* Mon Apr 27 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.7^0.git.27f62ae-1
 - Update to 1.18.7

* Thu Apr 23 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.5^0.git.85a59b3-1
 - Update to 1.18.5

* Tue Apr 21 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.3^2.git.63e0d49-1
 - Update to commit 63e0d49c15801102252529d30666c470782184ce

* Mon Apr 20 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.3^1.git.d00a46d-1
 - Update to commit d00a46d4fcc7a595f20771d9d349a1278045d882

* Sat Apr 18 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.3^0.git.04ad8e1-1
 - Update to 1.18.3

* Sat Apr 18 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.2^1.git.d7380a4-1
 - Update to commit d7380a468adccf80d646dbf6b2d86805910ef93f

* Thu Apr 16 2026 Lachlan Marie <lchlnm@pm.me> - 1.18.2^0.git.0d028b2-1
 - Update to 1.18.2

* Wed Apr 15 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.5^1.git.1faaca0-1
 - Update to commit 1faaca079d2c3583933b152ab8c66478e8f4ca9f

* Sat Apr 04 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.5^0.git.3d8d72c-1
 - Update to 1.17.5

* Fri Apr 03 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.4^3.git.113bb69-1
 - Update to commit 113bb692b81257215d6741982fb0c3fc88b2f44b

* Thu Apr 02 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.4^2.git.6cfd434-1
 - Update to commit 6cfd4340f27e864685118ae8ff254ac03a3a8f79

* Wed Apr 01 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.4^1.git.635d67d-1
 - Update to commit 635d67de89d01f9c4b6b7fb09c0c41d753a0b6fa

* Tue Mar 31 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.4^0.git.1b63bff-1
 - Update to 1.17.4

* Tue Mar 31 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.3^3.git.138aea3-1
 - Update to commit 138aea3e4ebd80e485c33a9d133599ff9ee9822a

* Mon Mar 30 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.3^2.git.35b7032-1
 - Update to commit 35b7032146650e67dcbbaabe0678bb7d60e32b34

* Mon Mar 30 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.3^1.git.bdf6e0d-1
 - Update to commit bdf6e0deefa8000c8db6c93d842b6982fa743401

* Sun Mar 29 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.3^0.git.7c670d1-1
 - Update to 1.17.3

* Sat Mar 28 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.2^0.git.e827ac6-1
 - Update to 1.17.2

* Fri Mar 27 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.1^3.git.1b32956-1
 - Update to commit 1b3295659254d9ab09e4a031310fdc7da598948e

* Fri Mar 27 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.1^2.git.ce7d995-1
 - Update to commit ce7d99563bc269ab0d9fdfd4abc5c90e86c43556

* Thu Mar 26 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.1^1.git.31b10ce-1
 - Update to commit 31b10ced5c46f5101b03a71addaf8404e4ca8557

* Thu Mar 26 2026 Lachlan Marie <lchlnm@pm.me> - 1.17.1^0.git.2227c77-1
 - Update to 1.17.1

* Wed Mar 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.16.6^10.git.e16e48f-1
 - Update to commit e16e48f94c242ce95856154ee3348ea10023a99c

* Wed Mar 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.16.6^9.git.b98f03c-1
 - Update to commit b98f03ce2b9ce06b3f42dc7167c0b46e660ae870

* Wed Mar 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.16.6^8.git.8c701ca-1
 - Update to commit 8c701ca68eeaae70c4b54203769dec2c911f1974

* Wed Mar 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.16.6^7.git.b017826-1
 - Update to commit b01782681538a02fb5ad50b9e0d9c0fe18f9cb7b

* Wed Mar 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.16.6^6.git.3937e4c-1
 - Update to commit 3937e4ccb30c6cc9a5e8e8e5f33b7b7fded8276e

* Wed Mar 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.16.6^5.git.06535b3-1
 - Update to commit 06535b3d651ca7f8e3d78e61def0fedf0986ac1b

* Tue Mar 24 2026 Lachlan Marie <lchlnm@pm.me> - 1.16.6^4.git.48baac7-1
 - Update to commit 48baac796723250635dfc8e0997858185c01f781

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 1.16.6^3.git.091bbe0-1
 - Update to commit 091bbe06fc70daad3c94f8346f54252c49638640

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 1.16.6^2.git.b0faf66-1
 - Update to commit b0faf660835dc5c0bb06c151c699e99867af3306

* Mon Mar 23 2026 Lachlan Marie <lchlnm@pm.me> - 1.16.6^1.git.d543aaa-1
 - Update to commit d543aaa415b4decc265428e15a566cf55a6b2987

* Sun Mar 15 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.10^37.git.60950c0-1
 - Update to commit 60950c040ed44e42ebee087a301cbb12622db8a1

* Thu Mar 12 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.10^36.git.5c592d1-1
 - Update to commit 5c592d15bb632547e3842a9b90d9067040f21de9

* Wed Mar 11 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.10^35.git.19b3782-1
 - Update to commit 19b3782c7a244f75ac5835beed480c5ce7686b1e

* Sun Mar 08 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.10^34.git.64a7743-1
 - Update to commit 64a774311d50692471be2d56b24231b3e38b63c6

* Fri Mar 06 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.10^33.git.e37cedc-1
 - Update to commit e37cedc99b3e045dfaa78361d7bd8635b0021e5f

* Thu Mar 05 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.10^32.git.1d531f0-1
 - Update to commit 1d531f07cf0d80d06285ed3589b5d04c9fda4382

* Mon Mar 02 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.10^31.git.f4c3882-1
 - Update to commit f4c38820f268c15dd705957de96f4589a4e3cd1d

* Sun Mar 01 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.10^30.git.ea908ce-1
 - Update to commit ea908ce252d83642ac7f6c54d8a6f9a15ff6accb

* Sat Feb 28 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.10^29.git.8213cc3-1
 - Update to commit 8213cc3baa440ddaa2425f494b4192e7fa38403b

* Mon Jan 26 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.10^28.git.e235218-1
 - Update to commit e2352188d71dca7ed2bccd3e956fe6bfe82b07c7

* Sun Jan 25 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.8^27.git.b7dbcdc-1
 - Update to commit b7dbcdcd695751ba5d5349e9933f77f209081427

* Wed Jan 21 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.8^26.git.17fece8-1
 - Update to commit 17fece8e3b5b9b0a2b5d46fadde1f555ef0d6394

* Mon Jan 19 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.6^25.git.3bdf23c-1
 - Update to commit 3bdf23cf433df4ab9ccf81d76d4730957ea92864

* Mon Jan 19 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.6^24.git.ae07c54-1
 - Update to commit ae07c54e2e7499e6b21b5764e595330139f4d823

* Sat Jan 17 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.6^23.git.752836f-1
 - Update to commit 752836f2b286dcc01d5f3171d5307daff3a67d72

* Wed Jan 14 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.4^22.git.69fc639-1
 - Update to commit 69fc639512e5eea1322168e840e2c37cda36e92c

* Wed Jan 14 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.4^21.git.c804b4a-1
 - Update to commit c804b4aabee1be33fab2c74d322ea246d2787cb3

* Tue Jan 13 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.4^20.git.22244d4-1
 - Update to commit 22244d49023e86876462ff221e54de528225fd75

* Fri Jan 09 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.3^19.git.3b6ff51-1
 - Update to commit 3b6ff512b25d5a114a7f8bf867bff46c2827caa1

* Fri Jan 09 2026 Lachlan Marie <lchlnm@pm.me> - 1.13.1^18.git.256f943-1
 - Update to commit 256f943b36cdb976aed9b07497fa0b1c88967171

* Wed Jan 07 2026 Lachlan Marie <lchlnm@pm.me> - 1.12.1^17.git.1079be0-1
 - Update to commit 1079be0a41ce817b54ce667af4b3ab62b287d5ba

* Tue Jan 06 2026 Lachlan Marie <lchlnm@pm.me> - 1.12.1^16.git.8430d70-1
 - Update to commit 8430d707205aa8a9b473d13f8b988ea98d17f363

* Tue Jan 06 2026 Lachlan Marie <lchlnm@pm.me> - 1.12.1^15.git.dccd451-1
 - Update to commit dccd4519dccfa6a0667cecc4eea47ff606e9112b

* Sun Jan 04 2026 Lachlan Marie <lchlnm@pm.me> - 1.11.8^14.git.6f613dd-1
 - Update to commit 6f613dde03943183a066d385eddb677dffe6d4d5

* Sat Jan 03 2026 Lachlan Marie <lchlnm@pm.me> - 1.11.8^13.git.6f8fc60-1
 - Update to commit 6f8fc60cdc729dcf0e522ff4f1616b9b100a3e96

* Tue Dec 30 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.8^12.git.f08a083-1
 - Update to commit f08a08355a96330cacbaf8780087c5b4c75d1e41

* Sat Dec 27 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.7^11.git.d0222c3-1
 - Update to commit d0222c30bf0fdaa0a8de1fac55868b50a102dd71

* Thu Dec 25 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.7^10.git.828cdd4-1
 - Update to commit 828cdd422f342e81c04cfaa5121ff4ece67ab2e0

* Wed Dec 24 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.7^9.git.01c9288-1
 - Update to commit 01c9288ac56ede941cdc3fe24d5736388e1d9526

* Mon Dec 22 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.7^8.git.5a65ad1-1
 - Update to commit 5a65ad104be924d88298ad3350eb64c1134c1876

* Sun Dec 21 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.7^7.git.950240e-1
 - Update to commit 950240e3b88e8aef46d5fad318f92f1a6e61c414

* Fri Dec 19 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.6^6.git.791896e-1
 - Update to commit 791896e5245d37e64eee05d844fc3a605d71f109

* Fri Dec 19 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.6^5.git.b7bd230-1
 - Update to commit b7bd230a84d199b8bfcda6f87992ced231c1f6e9

* Thu Dec 18 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.5^4.git.80d5545-1
 - Update to commit 80d5545aafb597334533ebaf23ae4c413abe94fc

* Tue Dec 16 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.4^3.git.35a8c76-1
 - Update to commit 35a8c76963fd5ebf4e5a4f2528a8d8906ee2fbbf

* Sun Dec 14 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.3^2.git.34fa1fd-1
 - Update to commit 34fa1fd977191d7d6b7f6f58d015c92f3a36ac12

* Sun Dec 14 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.3^1.git.2482afe-1
 - Update to commit 2482afe5fdcce4ea72eac852ce38675b055396ae

* Thu Dec 11 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.1^3.git.10e4718-1
 - Update to commit 10e471840ca2014d3664d02426f73d9ca562d584

* Tue Dec 09 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.1^2.git.7c86c8e-1
 - Update to commit 7c86c8e51d4991c18671bf0196c13f284fbe4014

* Mon Dec 08 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.1^1.git.c9a1e1e-1
 - Update to commit c9a1e1e99c14e22ff5d86c9a9dbba32188609578

* Sun Dec 07 2025 Lachlan Marie <lchlnm@pm.me> - 1.11.1^0.git.3b962c6-1
 - Adapted specfile from faugus copr
 - Changed build from project git commits
 - Update to commit 3b962c60c9b5e6be38d60644f1a0c8020d89b121
