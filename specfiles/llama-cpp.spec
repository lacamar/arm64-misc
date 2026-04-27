# For the extra python package gguf that comes with llama-cpp
%global pypi_name gguf
%global pypi_version 0.10.0
%global tag b8941

# Some optional subpackages
%bcond_with examples
%if %{with examples}
%global build_examples ON
%else
%global build_examples OFF
%endif

%bcond_with test
%if %{with test}
%global build_test ON
%else
%global build_test OFF
%endif

%bcond_with check

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

ExclusiveArch:  x86_64 aarch64

%ifarch x86_64
%bcond_without rocm
%else
%bcond_with rocm
%endif

%if %{with rocm}
%global build_hip ON
%global toolchain rocm
# hipcc does not support some clang flags
%global build_cxxflags %(echo %{optflags} | sed -e 's/-fstack-protector-strong/-Xarch_host -fstack-protector-strong/' -e 's/-fcf-protection/-Xarch_host -fcf-protection/' -e 's/-mtls-dialect=gnu2//')
%else
%global build_hip OFF
%global toolchain gcc
%endif

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

BuildRequires: vulkan-headers
BuildRequires: vulkan-loader-devel
BuildRequires: spirv-headers-devel

%if %{with examples}
BuildRequires:  python3-devel
BuildRequires:  python3dist(pip)
BuildRequires:  python3dist(poetry)
%endif

%if %{with rocm}
BuildRequires:  hipblas-devel
BuildRequires:  rocm-comgr-devel
BuildRequires:  rocm-hip-devel
BuildRequires:  rocblas-devel
BuildRequires:  hipblas-devel
BuildRequires:  rocm-runtime-devel
BuildRequires:  rocm-rpm-macros

Requires:       rocblas
Requires:       hipblas
%endif

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

%if %{with test}
%package test
Summary:        Tests for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description test
%{summary}
%endif

%if %{with examples}
%package examples
Summary:        Examples for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       python3dist(numpy)
Requires:       python3dist(torch)
Requires:       python3dist(sentencepiece)

%description examples
%{summary}
%endif

%prep
%autosetup -p1 -n llama.cpp-%{version}

# gcc 15 include cstdint
sed -i '/#include <vector.*/a#include <cstdint>' src/llama-mmap.h

# no android needed
rm -rf exmples/llma.android
# git cruft
find . -name '.gitignore' -exec rm -rf {} \;

%build

%if %{with examples}
cd %{_vpath_srcdir}/gguf-py
%pyproject_wheel
cd -
%endif

%if %{with rocm}
export HIPCC_COMPILE_FLAGS_APPEND="--offload-compress"
%endif

%cmake \
    -DCMAKE_INSTALL_LIBDIR=%{_lib} \
    -DCMAKE_SKIP_RPATH=ON \
    -DGGML_AVX=OFF \
    -DGGML_AVX2=OFF \
    -DGGML_AVX512=OFF \
    -DGGML_AVX512_VBMI=OFF \
    -DGGML_AVX512_VNNI=OFF \
    -DGGML_FMA=OFF \
    -DGGML_F16C=OFF \
    -DGGML_HIP=%{build_hip} \
    -DAMDGPU_TARGETS=%{rocm_gpu_list_default} \
    -DLLAMA_BUILD_EXAMPLES=%{build_examples} \
    -DLLAMA_BUILD_TESTS=%{build_test} \
    -DCMAKE_BUILD_TYPE=Release \
    -DGGML_VULKAN=ON \
    -DGGML_LTO=ON \
    -DLLAMA_BUILD_COMMON=ON \
    -DLLAMA_BUILD_TOOLS=ON \
    -DLLAMA_BUILD_SERVER=ON \
    -DLLAMA_SERVER_SSL=ON

%cmake_build

%install
%if %{with examples}
cd %{_vpath_srcdir}/gguf-py
%pyproject_install
cd -
%endif

%cmake_install

rm -rf %{buildroot}%{_libdir}/libggml_shared.*
rm -f %{buildroot}/usr/lib/debug/usr/bin/llama-debug-template-parser-*
rm -f %{buildroot}/usr/lib/debug/usr/bin/llama-results-*
rm -f %{buildroot}/usr/lib/debug/usr/bin/llama-template-analysis-*
rm -f %{buildroot}/usr/lib/debug/usr/lib64/libggml-vulkan.so*
rm -f %{buildroot}/usr/lib/debug/usr/lib64/libllama-common.so*


%if %{with examples}
mkdir -p %{buildroot}%{_datarootdir}/%{name}
cp -r %{_vpath_srcdir}/examples %{buildroot}%{_datarootdir}/%{name}/
cp -r %{_vpath_srcdir}/models %{buildroot}%{_datarootdir}/%{name}/
cp -r %{_vpath_srcdir}/README.md %{buildroot}%{_datarootdir}/%{name}/
rm -rf %{buildroot}%{_datarootdir}/%{name}/examples/llama.android
%else
rm %{buildroot}%{_bindir}/convert*.py
%endif

%if %{with test}
%if %{with check}
%check
# cpu results
#   14 - test-tokenizers-ggml-vocabs (Failed)              main
# rocm 7.2 gfx1100 results
#   14 - test-tokenizers-ggml-vocabs (Failed)              main
#   36 - test-backend-ops (Subprocess aborted)             main
export LD_LIBRARY_PATH=$PWD/%{_vpath_builddir}/bin
%ctest
%endif
%endif

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
%if %{with rocm}
%{_libdir}/libggml-hip.so.*
%endif
%{_bindir}/llama-batched-bench
%{_bindir}/llama-bench
%{_bindir}/llama-cli
%{_bindir}/llama-completion
%{_bindir}/llama-cvector-generator
%{_bindir}/llama-debug-template-parser
%{_bindir}/llama-export-lora
%{_bindir}/llama-fit-params
%{_bindir}/llama-gguf-split
%{_bindir}/llama-imatrix
%{_bindir}/llama-mtmd-cli
%{_bindir}/llama-perplexity
%{_bindir}/llama-quantize
%{_bindir}/llama-results
%{_bindir}/llama-server
%{_bindir}/llama-template-analysis
%{_bindir}/llama-tokenize
%{_bindir}/llama-tts

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
%if %{with rocm}
%{_libdir}/libggml-hip.so
%endif
%{_libdir}/cmake/llama/*.cmake
%{_libdir}/cmake/ggml/*.cmake
%{_libdir}/pkgconfig/llama.pc

%if %{with test}
%files test
%{_bindir}/test-*
%endif

%if %{with examples}
%files examples
%{_bindir}/convert_hf_to_gguf.py
%{_bindir}/gguf-*
%{_bindir}/llama-*
%{_datarootdir}/%{name}/
%{_libdir}/libllava_shared.so
%{python3_sitelib}/%{pypi_name}
%{python3_sitelib}/%{pypi_name}*.dist-info
%{python3_sitelib}/scripts
%endif

%changelog
* Mon Apr 27 2026 Lachlan Marie <lchlnm@pm.me> - b8941-1
 - Update to b8941

* Sun Apr 26 2026 Lachlan Marie <lchlnm@pm.me> - b8933-1
 - Update to b8933

* Sat Apr 25 2026 Lachlan Marie <lchlnm@pm.me> - b8920-1
 - Update to b8920

* Fri Apr 24 2026 Lachlan Marie <lchlnm@pm.me> - b8902-1
 - Update to b8902

* Wed Apr 22 2026 Lachlan Marie <lchlnm@pm.me> - b8883-1
 - Update to b8883

* Wed Apr 22 2026 Lachlan Marie <lchlnm@pm.me> - b8871-1
 - Update to b8871

* Tue Apr 21 2026 Lachlan Marie <lchlnm@pm.me> - b8855-1
 - Update to b8855

* Mon Apr 20 2026 Lachlan Marie <lchlnm@pm.me> - b8851-1
 - Update to b8851

* Fri Apr 17 2026 Lachlan Marie <lchlnm@pm.me> - b8816-1
 - Update to b8816

* Tue Apr 14 2026 Lachlan Marie <lchlnm@pm.me> - b8785-1
 - Update to b8785

* Tue Apr 14 2026 Lachlan Marie <lchlnm@pm.me> - b8779-1
 - Update to b8779

* Sun Apr 12 2026 Lachlan Marie <lchlnm@pm.me> - b8763-1
 - Update to b8763

* Fri Apr 10 2026 Lachlan Marie <lchlnm@pm.me> - b8739-1
 - Update to b8739

* Fri Apr 10 2026 Lachlan Marie <lchlnm@pm.me> - b8733-1
 - Update to b8733

* Thu Apr 09 2026 Lachlan Marie <lchlnm@pm.me> - b8720-1
 - Update to b8720

* Thu Apr 09 2026 Lachlan Marie <lchlnm@pm.me> - b8708-1
 - Update to b8708

* Wed Apr 08 2026 Lachlan Marie <lchlnm@pm.me> - b8705-1
 - Update to b8705

* Wed Apr 08 2026 Lachlan Marie <lchlnm@pm.me> - b8703-1
 - Update to b8703

* Wed Apr 08 2026 Lachlan Marie <lchlnm@pm.me> - b8702-1
 - Update to b8702

* Tue Apr 07 2026 Lachlan Marie <lchlnm@pm.me> - b8690-1
 - Update to b8690

* Tue Apr 07 2026 Lachlan Marie <lchlnm@pm.me> - b8676-1
 - Update to b8676

* Mon Apr 06 2026 Lachlan Marie <lchlnm@pm.me> - b8668-1
 - Update to b8668

* Sun Apr 05 2026 Lachlan Marie <lchlnm@pm.me> - b8667-1
 - Update to b8667

* Sun Apr 05 2026 Lachlan Marie <lchlnm@pm.me> - b8664-1
 - Update to b8664

* Sat Apr 04 2026 Lachlan Marie <lchlnm@pm.me> - b8662-1
 - Update to b8662

* Sat Apr 04 2026 Lachlan Marie <lchlnm@pm.me> - b8661-1
 - Update to b8661

* Sat Apr 04 2026 Lachlan Marie <lchlnm@pm.me> - b8660-1
 - Update to b8660

* Fri Apr 03 2026 Lachlan Marie <lchlnm@pm.me> - b8646-1
 - Update to b8646

* Thu Apr 02 2026 Lachlan Marie <lchlnm@pm.me> - b8635-1
 - Update to b8635

* Wed Apr 01 2026 Lachlan Marie <lchlnm@pm.me> - b8610-1
 - Update to b8610

* Wed Apr 01 2026 Lachlan Marie <lchlnm@pm.me> - b8606-1
 - Update to b8606

* Tue Mar 31 2026 Lachlan Marie <lchlnm@pm.me> - b8591-1
 - Update to b8591

* Tue Mar 31 2026 Lachlan Marie <lchlnm@pm.me> - b8586-1
 - Update to b8586

* Mon Mar 30 2026 Lachlan Marie <lchlnm@pm.me> - b8583-1
 - Update to b8583

* Mon Mar 30 2026 Lachlan Marie <lchlnm@pm.me> - b8580-1
 - Update to b8580

* Mon Mar 30 2026 Lachlan Marie <lchlnm@pm.me> - b8578-1
 - Update to b8578

* Sun Mar 29 2026 Lachlan Marie <lchlnm@pm.me> - b8576-1
 - Update to b8576

* Sat Mar 28 2026 Lachlan Marie <lchlnm@pm.me> - b8565-1
 - Update to b8565

* Sat Mar 28 2026 Lachlan Marie <lchlnm@pm.me> - b8559-1
 - Update to b8559

* Fri Mar 27 2026 Lachlan Marie <lchlnm@pm.me> - b8555-1
 - Update to b8555

* Fri Mar 27 2026 Lachlan Marie <lchlnm@pm.me> - b8552-1
 - Update to b8552

* Fri Mar 27 2026 Lachlan Marie <lchlnm@pm.me> - b8550-1
 - Update to b8550

* Fri Mar 27 2026 Lachlan Marie <lchlnm@pm.me> - b8533-1
 - Update to b8533

* Thu Mar 26 2026 Lachlan Marie <lchlnm@pm.me> - b8533-1
 - Update to b8533

* Thu Mar 26 2026 Lachlan Marie <lchlnm@pm.me> - b8532-1
 - Update to b8532

* Thu Mar 26 2026 Lachlan Marie <lchlnm@pm.me> - b8522-1
 - Update to b8522
