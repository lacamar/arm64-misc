%global fontname apple-emoji-linux
%global fontconf 70-%{fontname}.conf
%global fontdir %{_datadir}/fonts/%{fontname}
%global fontconfig_avail %{_datadir}/fontconfig/conf.avail
%global fontconfig_confdir %{_sysconfdir}/fonts/conf.d

Name:           %{fontname}-fonts
Version:        26.2.1
Release:        2%{?dist}
Summary:        Apple Color Emoji font for Linux

License:        OFL-1.1 AND Apache-2.0
URL:            https://github.com/samuelngs/%{fontname}
Source0:        https://github.com/samuelngs/%{fontname}/archive/refs/tags/v%{version}.tar.gz
Source1:        %{name}-fontconfig.conf
Source2:        %{fontname}.metainfo.xml
# Fixes 77 default (no skin-tone modifier) hand/body emoji glyphs that the
# v26.2.1 asset refresh accidentally built from the dark-skin-tone (U+1F3FF)
# bitmap instead of the standard yellow default. Contains the pre-regression
# PNGs (from upstream commit b22ae7f, the parent of the breaking commit
# b229fd8) for just those glyphs. Upstream tracked as samuelngs/apple-emoji-ttf#116,
# closed without a fix.
Source3:        %{name}-default-skintone-fix.tar.gz

BuildArch:      noarch

BuildRequires:  make
BuildRequires:  fonttools
BuildRequires:  nototools
BuildRequires:  optipng
BuildRequires:  zopfli
BuildRequires:  pngquant
BuildRequires:  ImageMagick
BuildRequires:  libappstream-glib

%description
Apple Color Emoji for Linux is a color emoji font that recreates Apple's
emoji designs for use on Linux desktops and applications. It uses the CBDT/CBLC
color font format and covers the same Unicode emoji repertoire as recent iOS
releases.

%prep
%autosetup -n apple-emoji-ttf-%{version}

# Restore correct yellow default glyphs (see Source3 comment above / gh#116)
tar xzf %{SOURCE3} -C png/160 --strip-components=1

%build
# Stop short of the default "font" target: it would embed a single CBDT/CBLC
# strike and finish assembling AppleColorEmoji.ttf, which we redo below with
# extra strikes. AppleColorEmoji.tmpl.ttf is the glyph/cmap/GSUB shell (no
# bitmaps yet); "compressed" produces the native ~160px strike's PNGs.
%make_build AppleColorEmoji.tmpl.ttf compressed

# Upstream embeds only one CBDT/CBLC bitmap strike, natively sized around
# 160px (EMOJI_SRC_DIR := png/160 in the Makefile). Several renderers --
# terminal emulators in particular -- don't downscale a single oversized
# bitmap strike correctly and instead draw it close to its native pixel
# size, so emoji appear enormous relative to surrounding text. Build a few
# smaller strikes from the same source images and merge them into the font
# with upstream's own emoji_builder.py, which natively supports embedding
# multiple strikes per font (it just was never invoked that way here).
for px in 16 32 64; do
    strikedir="build/extra_strike_${px}"
    mkdir -p "$strikedir"
    mogrify -path "$strikedir" -resize "${px}x${px}!" -background none \
        -format png png/160/emoji_u*.png
    # pngquant exits non-zero as soon as any single image in the batch isn't
    # worth quantizing (common at these tiny sizes) -- non-fatal, so don't
    # let it abort the (set -e) build; the un-quantized resize is still valid.
    ( cd "$strikedir" && pngquant --speed 1 \
        --quality 85-95 --force --ext .png -- *.png ) || :
    optipng -quiet -o2 -clobber "$strikedir"/*.png
done

python3 third_party/color_emoji/emoji_builder.py -S -V \
    AppleColorEmoji.tmpl.ttf AppleColorEmoji.ttf \
    build/extra_strike_16/emoji_u \
    build/extra_strike_32/emoji_u \
    build/extra_strike_64/emoji_u \
    build/compressed_pngs/emoji_u
python3 map_pua_emoji.py AppleColorEmoji.ttf AppleColorEmoji.ttf-with-pua
add_vs_cmap.py -vs 2640 2642 2695 --dstdir . \
    -o AppleColorEmoji.ttf-with-pua-varsel AppleColorEmoji.ttf-with-pua
mv AppleColorEmoji.ttf-with-pua-varsel AppleColorEmoji.ttf
rm AppleColorEmoji.ttf-with-pua

%install
install -m 0755 -d %{buildroot}%{fontdir}
install -m 0644 -p AppleColorEmoji.ttf \
    %{buildroot}%{fontdir}/

install -m 0755 -d %{buildroot}%{fontconfig_avail} \
                   %{buildroot}%{fontconfig_confdir}
install -m 0644 -p %{SOURCE1} \
    %{buildroot}%{fontconfig_avail}/%{fontconf}
ln -s %{fontconfig_avail}/%{fontconf} \
    %{buildroot}%{fontconfig_confdir}/%{fontconf}

install -m 0755 -d %{buildroot}%{_metainfodir}
install -m 0644 -p %{SOURCE2} \
    %{buildroot}%{_metainfodir}/%{fontname}.metainfo.xml

%check
appstream-util validate-relax --nonet \
    %{buildroot}/%{_metainfodir}/%{fontname}.metainfo.xml

%post
if [ -x /usr/bin/fc-cache ]; then
    fc-cache -f %{_datadir}/fonts >/dev/null 2>&1 || :
fi

%postun
if [ $1 -eq 0 ] && [ -x /usr/bin/fc-cache ]; then
    fc-cache -f %{_datadir}/fonts >/dev/null 2>&1 || :
fi

%files
%license LICENSE
%doc README.md
%{fontdir}/AppleColorEmoji.ttf
%{fontconfig_avail}/%{fontconf}
%{fontconfig_confdir}/%{fontconf}
%{_metainfodir}/%{fontname}.metainfo.xml

%changelog
* Thu Aug 20 2026 Lachlan Marie <lchlnm@pm.me> - 26.2.1-2
- Fix 77 default (no skin-tone modifier) hand/body emoji rendering with the
  dark skin tone instead of the standard yellow default (upstream regression
  in v26.2.1, samuelngs/apple-emoji-ttf#116)
- Embed 3 extra, smaller CBDT/CBLC bitmap strikes (16/32/64px, alongside the
  existing ~160px one) so apps that don't downscale a single oversized
  bitmap strike (terminals in particular) stop rendering emoji giant-sized

* Sun Nov 23 2025 Lachlan Marie <lchlnm@pm.me> - 18.4-3
- Fixed minor changes to font config

* Sun Nov 23 2025 Lachlan Marie <lchlnm@pm.me> - 18.4-2
- Fixed font config warning

* Sun Nov 23 2025 Lachlan Marie <lchlnm@pm.me> - 18.4-1
- Initial packaging for apple-emoji-linux-fonts
