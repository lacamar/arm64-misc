%global tag 1.9.5
Name:    whisper-cpp
Version: %{tag}
Release: 1%{?dist}
Summary: Port of OpenAI's Whisper model in C/C++

License: MIT
URL:     https://github.com/ggml-org/whisper.cpp
Source0: %{url}/archive/refs/tags/v%{version}.tar.gz#/whisper.cpp-%{version}.tar.gz

BuildRequires: cmake
BuildRequires: gcc-c++
BuildRequires: git
BuildRequires: llama-cpp-devel


%description
High-performance inference of OpenAI's Whisper speech recognition model,
built against the llama-cpp ggml so it shares its Vulkan GPU backend.


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
    -DWHISPER_BUILD_EXAMPLES=OFF \
    -DWHISPER_BUILD_SERVER=OFF \
    -DWHISPER_BUILD_TESTS=OFF \
    -DGGML_NATIVE=OFF
%cmake_build


%install
%cmake_install
find %{buildroot} -name '*.pc' -delete


%files
%license LICENSE
%{_libdir}/libwhisper.so.*
%{_libdir}/libparakeet.so.*


%files devel
%doc README.md
%{_includedir}/whisper.h
%{_includedir}/parakeet.h
%{_libdir}/libwhisper.so
%{_libdir}/libparakeet.so
%{_libdir}/cmake/whisper/
%{_libdir}/cmake/parakeet/


%changelog
* Sat Oct 18 2026 Lachlan Marie <lchlnm@pm.me> - 1.9.5-1
 - Initial packaging against llama-cpp ggml (Vulkan)
