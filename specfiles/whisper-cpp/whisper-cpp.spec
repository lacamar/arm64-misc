%global tag 1.9.5
Name:    whisper-cpp
Version: %{tag}
Release: 3%{?dist}
Summary: Port of OpenAI's Whisper model in C/C++

License: MIT
URL:     https://github.com/ggml-org/whisper.cpp
Source0: %{url}/archive/refs/tags/v%{version}.tar.gz#/whisper.cpp-%{version}.tar.gz
Source1: whisper-dictate
Patch0:  whisper-stream-vad-clear.patch

BuildRequires: cmake
BuildRequires: gcc-c++
BuildRequires: git
BuildRequires: llama-cpp-devel
BuildRequires: pkgconfig(sdl2)

Requires: llama-cpp%{?_isa}


%description
High-performance inference of OpenAI's Whisper speech recognition model,
built against the llama-cpp ggml so it shares its Vulkan GPU backend.


%package dictate
Summary:   Push-to-talk dictation with whisper.cpp
BuildArch: noarch
Requires:  %{name}
Requires:  wtype
Requires:  curl

%description dictate
Toggle script: listens on the default microphone and types each phrase
into the focused Wayland window when you pause.


%package devel
Summary:  Libraries and headers for %{name}
Requires: %{name}%{?_isa} = %{version}-%{release}
Requires: llama-cpp-devel%{?_isa}

%description devel
Headers and CMake files for %{name}.


%prep
%autosetup -p1 -n whisper.cpp-%{version}


%build
%cmake \
    -DWHISPER_USE_SYSTEM_GGML=ON \
    -DWHISPER_BUILD_EXAMPLES=ON \
    -DWHISPER_SDL2=ON \
    -DWHISPER_BUILD_SERVER=OFF \
    -DWHISPER_BUILD_TESTS=OFF \
    -DGGML_NATIVE=OFF
%cmake_build


%install
%cmake_install
find %{buildroot} -name '*.pc' -delete
# talk-llama bundles its own libllama, clashing with llama-cpp
rm -rf %{buildroot}%{_bindir}/whisper-talk-llama %{buildroot}%{_includedir}/llama*.h %{buildroot}%{_libdir}/libllama.so* %{buildroot}%{_libdir}/cmake/llama
install -Dm755 %{SOURCE1} %{buildroot}%{_bindir}/whisper-dictate


%files
%license LICENSE
%{_libdir}/libwhisper.so.*
%{_libdir}/libparakeet.so.*
%{_bindir}/whisper-*
%exclude %{_bindir}/whisper-dictate
%{_bindir}/parakeet-*


%files dictate
%{_bindir}/whisper-dictate


%files devel
%doc README.md
%{_includedir}/whisper.h
%{_includedir}/parakeet.h
%{_libdir}/libwhisper.so
%{_libdir}/libparakeet.so
%{_libdir}/cmake/whisper/
%{_libdir}/cmake/parakeet/


%changelog
* Tue Oct 27 2026 Lachlan Marie <lchlnm@pm.me> - 1.9.5-3
- Build SDL2 examples (whisper-stream)
- whisper-stream: clear audio after each VAD phrase
- whisper-dictate: continuous phrase-by-phrase typing

* Tue Oct 27 2026 Lachlan Marie <lchlnm@pm.me> - 1.9.5-2
- Ship whisper-cli
- Add whisper-dictate push-to-talk subpackage

* Sat Oct 18 2026 Lachlan Marie <lchlnm@pm.me> - 1.9.5-1
 - Initial packaging against llama-cpp ggml (Vulkan)
