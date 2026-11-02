Name:           noise-suppression-for-voice
Version:        1.10
Release:        1%{?dist}
Summary:        Real-time rnnoise noise suppression LADSPA plugin
License:        GPL-3.0-or-later AND BSD-3-Clause
URL:            https://github.com/werman/noise-suppression-for-voice
Source0:        %{url}/archive/v%{version}/%{name}-%{version}.tar.gz
Source1:        60-j414-voice-isolation.conf

BuildRequires:  cmake
BuildRequires:  gcc
BuildRequires:  gcc-c++

%description
Real-time noise suppression plugin for voice based on Xiph's RNNoise,
built as a LADSPA plugin (noise_suppressor_mono/stereo).

%package        apple-j414
Summary:        Voice Isolation microphone source for MacBook Pro J414
BuildArch:      noarch
Requires:       %{name} = %{version}-%{release}
Requires:       asahi-audio >= 4.1
Requires:       pipewire

%description    apple-j414
PipeWire filter-chain adding a "Voice Isolation" source: rnnoise on top of
the asahi-audio beamformed J414 microphone.

%prep
%autosetup -p1

%build
%cmake \
    -DBUILD_TESTS=OFF \
    -DBUILD_VST_PLUGIN=OFF \
    -DBUILD_VST3_PLUGIN=OFF \
    -DBUILD_LV2_PLUGIN=OFF \
    -DBUILD_AU_PLUGIN=OFF \
    -DBUILD_AUV3_PLUGIN=OFF \
    -DBUILD_VERSION=%{version}
%cmake_build

%install
%cmake_install
install -Dpm0644 %{SOURCE1} %{buildroot}%{_datadir}/pipewire/pipewire.conf.d/60-j414-voice-isolation.conf

%files
%license LICENSE
%doc README.md
%{_libdir}/ladspa/librnnoise_ladspa.so

%files apple-j414
%{_datadir}/pipewire/pipewire.conf.d/60-j414-voice-isolation.conf

%changelog
* Mon Nov 02 2026 Lachlan Marie <lchlnm@pm.me> - 1.10-1
- Initial package, LADSPA only
- Add J414 Voice Isolation source
