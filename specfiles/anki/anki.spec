%global __requires_exclude_from ^%{_datadir}/anki/.*$
%global __provides_exclude_from ^%{_datadir}/anki/.*$
%global tag 26.09.2

Name:           anki
Version:        %{tag}
Release:        2%{?dist}
Summary:        Anki - a powerful flashcard program
License:        Gnu Affero Public License
URL:            https://github.com/ankitects/anki

# Build tools
BuildRequires:  python3
BuildRequires:  python3-pip
BuildRequires:  python3-devel
BuildRequires:  gcc
BuildRequires:  gcc-c++
BuildRequires:  redhat-rpm-config
BuildRequires:  desktop-file-utils

# Runtime dependencies
Requires:       python3
Requires:       python3-pyqt6
Requires:       python3-pyqt6-base
Requires:       python3-pyqt6-sip
Requires:       python3-pyqt6-webengine
Requires:       python3-markdown
Requires:       python3-werkzeug
Requires:       python3-blinker
Requires:       python3-click
Requires:       python3-beautifulsoup4
Requires:       python3-jsonschema
Requires:       python3-waitress
Requires:       python3-orjson
Requires:       python3-itsdangerous
Requires:       python3-typing-extensions
Requires:       python3-requests
Requires:       python3-wrapt
Requires:       python3-send2trash
Requires:       python3-jinja2
Requires:       qt6-qtwayland
Requires:       qt6-qtbase-gui
Requires:       python3-decorator

%description
Anki is a powerful, intelligent flashcard program. This package installs Anki using pip inside a system-wide virtual environment under /usr/share/anki.

%prep
# No source to unpack

%build
# Nothing to build, pip handles it

%install
mkdir -p %{buildroot}%{_datadir}/anki
python3 -m venv --system-site-packages %{buildroot}%{_datadir}/anki

rm -rf %{buildroot}%{_datadir}/anki/lib64
ln -s lib %{buildroot}%{_datadir}/anki/lib64

%{buildroot}%{_datadir}/anki/bin/python3 -m pip install --upgrade pip setuptools wheel
%{buildroot}%{_datadir}/anki/bin/python3 -m pip install "aqt[qt6]==%{version}"

find %{buildroot}%{_datadir}/anki -name "__pycache__" -type d -exec rm -rf {} +
find %{buildroot}%{_datadir}/anki -name "*.pyc" -delete

find %{buildroot}%{_datadir}/anki/bin -type f -exec grep -l "%{buildroot}" {} + | xargs -r sed -i "s|%{buildroot}||g"
if [ -f %{buildroot}%{_datadir}/anki/pyvenv.cfg ]; then
    sed -i "s|%{buildroot}||g" %{buildroot}%{_datadir}/anki/pyvenv.cfg
fi

mkdir -p %{buildroot}%{_bindir}
cat > %{buildroot}%{_bindir}/anki << 'EOF'
#!/bin/sh
exec %{_datadir}/anki/bin/anki "$@"
EOF
chmod 755 %{buildroot}%{_bindir}/anki

mkdir -p %{buildroot}%{_datadir}/applications
mkdir -p %{buildroot}%{_datadir}/pixmaps
ICON_SRC=$(find %{buildroot}%{_datadir}/anki/lib/python3.*/site-packages/_aqt/data/qt/icons/anki.png -print -quit)
if [ -z "$ICON_SRC" ]; then
    ICON_SRC=$(find %{buildroot}%{_datadir}/anki/lib/python3.*/site-packages/_aqt/data/web/imgs/anki-logo-thin.png -print -quit)
fi
if [ -z "$ICON_SRC" ]; then
    echo "ERROR: could not locate an anki icon inside the installed aqt wheel" >&2
    exit 1
fi
install -Dm644 "$ICON_SRC" %{buildroot}%{_datadir}/pixmaps/anki.png

cat > %{buildroot}%{_datadir}/applications/anki.desktop << 'EOF'
[Desktop Entry]
Type=Application
Name=Anki
GenericName=Flashcard Trainer
Comment=Study using spaced repetition
Exec=anki %f
Icon=anki
Terminal=false
StartupWMClass=anki
Categories=Education;Languages;
MimeType=application/x-apkg;
EOF
chmod 644 %{buildroot}%{_datadir}/applications/anki.desktop
desktop-file-validate %{buildroot}%{_datadir}/applications/anki.desktop

%files
/usr/share/anki
/usr/bin/anki
%{_datadir}/applications/anki.desktop
%{_datadir}/pixmaps/anki.png

%changelog
* Fri Sep 18 2026 Lachlan Marie <lchlnm@pm.me> - 26.09.2-2
 - Update to 26.09.2

* Thu Aug 06 2026 Lachlan Marie <lchlnm@pm.me> - 26.08.1-2
 - Update to 26.08.1

* Sat Aug 01 2026 Lachlan Marie <lchlnm@pm.me> - 26.08-2
 - Update to 26.08

* Mon Jun 22 2026 Lachlan Marie <lchlnm@pm.me> - 26.05-2
 - Update to 26.05

* Mon Jun 22 2026 Lachlan Marie <lchlnm@pm.me> - 26.05-2
- Pin pip install to the spec version so the RPM matches its declared contents
- Fix taskbar icon by correcting StartupWMClass to the window app_id

* Sun Jun 21 2026 Lachlan Marie <lchlnm@pm.me> - 26.05-1
- Update to 26.5
- Add desktop entry and icon

* Wed Mar 04 2026 Boyd Kelly <bkelly@coastsystems.net> - 25.09.2-1
- Fedora 44 RPM packaging for Anki using system-wide venv and pip
