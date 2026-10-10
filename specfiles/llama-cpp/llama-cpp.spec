%global tag b11541

Summary:        Port of Facebook's LLaMA model in C/C++
Name:           llama-cpp

# Licensecheck reports
#
# *No copyright* The Unlicense
# ----------------------------
# common/base64.hpp
# common/stb_image.h
# These are public domain
#
# MIT License
# -----------
# LICENSE
# ...
# This is the main license

License:        MIT AND Apache-2.0 AND LicenseRef-Fedora-Public-Domain
Version:        %{tag}
Release:        %autorelease

URL:            https://github.com/ggerganov/llama.cpp
Source0:        %{url}/archive/%{version}.tar.gz#/llama.cpp-%{version}.tar.gz

ExclusiveArch:  aarch64

BuildRequires:  cmake
BuildRequires:  curl
BuildRequires:  git
BuildRequires:  wget
BuildRequires:  xxd
BuildRequires:  langpacks-en
# above are packages in .github/workflows/server.yml
BuildRequires:  libcurl-devel
BuildRequires:  gcc-c++
BuildRequires:  openmpi
BuildRequires:  pthreadpool-devel
BuildRequires:  vulkan-tools
BuildRequires:  glslc
BuildRequires:  openblas-devel

BuildRequires: vulkan-headers
BuildRequires: vulkan-loader-devel
BuildRequires: spirv-headers-devel

Requires:       curl
Recommends:     numactl

%description
The main goal of llama.cpp is to run the LLaMA model using 4-bit
integer quantization on a MacBook

* Plain C/C++ implementation without dependencies
* Apple silicon first-class citizen - optimized via ARM NEON, Accelerate
  and Metal frameworks
* AVX, AVX2 and AVX512 support for x86 architectures
* Mixed F16 / F32 precision
* 2-bit, 3-bit, 4-bit, 5-bit, 6-bit and 8-bit integer quantization support
* CUDA, Metal and OpenCL GPU backend support

The original implementation of llama.cpp was hacked in an evening.
Since then, the project has improved significantly thanks to many
contributions. This project is mainly for educational purposes and
serves as the main playground for developing new features for the
ggml library.

%package devel
Summary:        Port of Facebook's LLaMA model in C/C++
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description devel
%{summary}.

%prep
%autosetup -p1 -n llama.cpp-%{version}

# gcc 15 include cstdint
sed -i '/#include <vector.*/a#include <cstdint>' src/llama-mmap.h

# git cruft
find . -name '.gitignore' -exec rm -rf {} \;

%build
%cmake \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DCMAKE_SKIP_RPATH=ON \
    -DLLAMA_BUILD_EXAMPLES=OFF \
    -DLLAMA_BUILD_TESTS=OFF \
    -DCMAKE_BUILD_TYPE=Release \
    -DGGML_VULKAN=ON \
    -DGGML_LTO=ON \
    -DGGML_NATIVE=OFF \
    -DGGML_RPC=ON \
    -DGGML_BLAS=ON \
    -DGGML_BLAS_VENDOR=OpenBLAS \
    -DLLAMA_BUILD_COMMON=ON \
    -DLLAMA_BUILD_TOOLS=ON \
    -DLLAMA_BUILD_SERVER=ON \
    -DLLAMA_SERVER_SSL=ON

%cmake_build

%install
%cmake_install

rm -rf %{buildroot}%{_libdir}/libggml_shared.*
rm -f %{buildroot}/usr/lib/debug/usr/lib64/libggml-vulkan.so*
rm -f %{buildroot}/usr/lib/debug/usr/lib64/libllama-common.so*
rm -f %{buildroot}/usr/lib/debug/usr/bin/llama-*
rm -f %{buildroot}/usr/lib64/libllama-*-impl.so-*.debug

%files
%license LICENSE
%{_libdir}/libllama.so.*
%{_libdir}/libllama-common.so
%{_libdir}/libllama-common.so.*
%{_libdir}/libmtmd.so.*
%{_libdir}/libggml.so.*
%{_libdir}/libggml-base.so.*
%{_libdir}/libggml-cpu.so.*
%{_libdir}/libggml-vulkan.so.*
%{_libdir}/libggml-blas.so.*
%{_libdir}/libggml-rpc.so.*
%{_libdir}/libllama-batched-bench-impl.so
%{_libdir}/libllama-bench-impl.so
%{_libdir}/libllama-cli-impl.so
%{_libdir}/libllama-completion-impl.so
%{_libdir}/libllama-fit-params-impl.so
%{_libdir}/libllama-perplexity-impl.so
%{_libdir}/libllama-quantize-impl.so
%{_libdir}/libllama-server-impl.so
%{_bindir}/llama
%{_bindir}/llama-batched-bench
%{_bindir}/llama-bench
%{_bindir}/llama-cli
%{_bindir}/llama-completion
%{_bindir}/llama-cvector-generator
%{_bindir}/llama-export-lora
%{_bindir}/llama-fit-params
%{_bindir}/llama-gguf-split
%{_bindir}/llama-imatrix
%{_bindir}/llama-mtmd-cli
%{_bindir}/llama-perplexity
%{_bindir}/llama-quantize
%{_bindir}/llama-results
%{_bindir}/llama-server
%{_bindir}/llama-tokenize
%{_bindir}/llama-tts
%{_bindir}/ggml-rpc-server

%files devel
%dir %{_libdir}/cmake/llama
%dir %{_libdir}/cmake/ggml
%doc README.md
%{_includedir}/gguf.h
%{_includedir}/ggml*.h
%{_includedir}/llama*.h
%{_includedir}/mtmd*.h
%{_libdir}/libllama.so
%{_libdir}/libmtmd.so
%{_libdir}/libggml.so
%{_libdir}/libggml-base.so
%{_libdir}/libggml-cpu.so
%{_libdir}/libggml-vulkan.so
%{_libdir}/libggml-blas.so
%{_libdir}/libggml-rpc.so
%{_libdir}/cmake/llama/*.cmake
%{_libdir}/cmake/ggml/*.cmake
%{_libdir}/pkgconfig/llama.pc

%changelog
* Sat Oct 10 2026 Lachlan Marie <lchlnm@pm.me> - b11541-1
 - Update to b11541

* Thu Oct 08 2026 Lachlan Marie <lchlnm@pm.me> - b11514-1
 - Update to b11514

* Sun Sep 27 2026 Lachlan Marie <lchlnm@pm.me> - b11222-1
 - Update to b11222

* Sun Sep 27 2026 Lachlan Marie <lchlnm@pm.me> - b11221-1
 - Update to b11221

* Sun Sep 27 2026 Lachlan Marie <lchlnm@pm.me> - b11205-1
 - Update to b11205

* Sat Sep 26 2026 Lachlan Marie <lchlnm@pm.me> - b11201-1
 - Update to b11201

* Sat Sep 26 2026 Lachlan Marie <lchlnm@pm.me> - b11200-1
 - Update to b11200
