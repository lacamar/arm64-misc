%undefine __brp_mangle_shebangs

%global forgeurl https://github.com/dnglab/dnglab

Name:           dnglab
Version:        0.8.0
Release:        4%{?dist}
Summary:        Camera RAW to DNG file format converter

License:        LGPL-2.1-only
URL:            %{forgeurl}
Source0:        %{forgeurl}/archive/refs/tags/v%{version}/%{name}-%{version}.tar.gz
# Adds `--full-size-preview` to `convert`/`ftpserver`: forces the DNG
# preview/thumbnail to be rendered from the full raw sensor data instead of
# using whatever (often much smaller) JPEG preview the camera embedded,
# matching Adobe DNG Converter's "Full Size JPEG Preview" behavior -- see
# rawler/src/dng/convert.rs's generate_preview(), which otherwise always
# prefers the camera's own embedded preview when one exists. Not upstream.
Patch0:         0001-full-size-preview.patch

BuildRequires:  cargo
BuildRequires:  anda-srpm-macros
BuildRequires:  cargo-rpm-macros

%description
DNGlab is a fast, cross-platform converter for camera RAW images to the
Digital Negative (DNG) format, written in Rust. It also supports the reverse
operation, extracting the original raw file that is embedded in a DNG.

%prep
%autosetup -n %{name}-%{version} -p1

%build
%cargo_prep_online
%cargo_build

%install
install -Dm755 target/rpm/%{name} %{buildroot}%{_bindir}/%{name}

install -Dm644 bin/%{name}/manpages/%{name}.1 %{buildroot}%{_mandir}/man1/%{name}.1
for man in bin/%{name}/manpages/%{name}-*.1; do
    install -Dm644 "$man" %{buildroot}%{_mandir}/man1/"$(basename "$man")"
done

install -Dm644 bin/%{name}/completions/%{name}.bash %{buildroot}%{_datadir}/bash-completion/completions/%{name}
install -Dm644 bin/%{name}/completions/%{name}.fish %{buildroot}%{_datadir}/fish/vendor_completions.d/%{name}.fish
install -Dm644 bin/%{name}/completions/_%{name} %{buildroot}%{_datadir}/zsh/site-functions/_%{name}

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*
%{_mandir}/man1/%{name}-*.1*
%{_datadir}/bash-completion/completions/%{name}
%{_datadir}/fish/vendor_completions.d/%{name}.fish
%{_datadir}/zsh/site-functions/_%{name}

%changelog
* Tue Sep 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.8.0-4
- 0.8.0-3 built with a stale cached copy of 0001-full-size-preview.patch from
  ~/.local/rpm/sources/dnglab/ (mx-rpm doesn't re-sync a local Patch0 already
  present there), so it shipped without the writer.rs fix below despite the
  changelog claiming it. Re-synced the source-dir patch copy and rebuilt.

* Tue Sep 01 2026 Lachlan Marie <lchlnm@pm.me> - 0.8.0-3
- Fix --full-size-preview to actually produce a full-size preview:
  DngWriter::preview() (rawler/src/dng/writer.rs) was unconditionally
  resizing the preview subframe to fit 1024x768 regardless of source, so
  the 0.8.0-2 patch only changed where the pre-resize image came from
  (embedded JPEG vs. full raw develop) without changing the output size.
  Thread full_size_preview through to preview() and skip the resize cap
  when it's set.

* Sun Aug 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.8.0-2
- Add patch for a --full-size-preview convert/ftpserver flag (renders the DNG
  preview/thumbnail from the full raw data instead of the camera's own,
  often much smaller, embedded preview)

* Sun Aug 30 2026 Lachlan Marie <lchlnm@pm.me> - 0.8.0-1
- Initial packaging
