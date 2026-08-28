# For the extra python package gguf that comes with llama-cpp
%global pypi_name gguf
%global pypi_version 0.10.0
%global tag b10675

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

# On aarch64 this is built and run on the same box (Apple Silicon under
# Asahi), so -march=native (GGML_NATIVE) is safe and picks up dotprod/i8mm/
# bf16 automatically instead of the generic armv8-a baseline. KleidiAI adds
# Arm's own hand-tuned int4/int8 GEMM/GEMV kernels on top of that (fetched
# via CMake FetchContent, network is already enabled for this mock build).
# Neither applies to the x86_64/rocm variant, which stays on its existing
# explicit AVX* toggles for redistributability.
%ifarch aarch64
%global build_native ON
%global build_kleidiai ON
%else
%global build_native OFF
%global build_kleidiai OFF
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
BuildRequires:  openblas-devel

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
    -DGGML_NATIVE=%{build_native} \
    -DGGML_CPU_KLEIDIAI=%{build_kleidiai} \
    -DGGML_RPC=ON \
    -DGGML_BLAS=ON \
    -DGGML_BLAS_VENDOR=OpenBLAS \
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
rm -f %{buildroot}/usr/lib/debug/usr/bin/llama-results-*
rm -f %{buildroot}/usr/lib/debug/usr/lib64/libggml-vulkan.so*
rm -f %{buildroot}/usr/lib/debug/usr/lib64/libllama-common.so*
rm -f %{buildroot}/usr/lib/debug/usr/bin/llama-*
rm -f %{buildroot}/usr/lib64/libllama-batched-bench-impl.so-*.debug
rm -f %{buildroot}/usr/lib64/libllama-bench-impl.so-*.debug
rm -f %{buildroot}/usr/lib64/libllama-cli-impl.so-*.debug
rm -f %{buildroot}/usr/lib64/libllama-completion-impl.so-*.debug
rm -f %{buildroot}/usr/lib64/libllama-fit-params-impl.so-*.debug
rm -f %{buildroot}/usr/lib64/libllama-perplexity-impl.so-*.debug
rm -f %{buildroot}/usr/lib64/libllama-quantize-impl.so-*.debug
rm -f %{buildroot}/usr/lib64/libllama-server-impl.so-*.debug


%if %{with examples}
mkdir -p %{buildroot}%{_datarootdir}/%{name}
cp -r %{_vpath_srcdir}/examples %{buildroot}%{_datarootdir}/%{name}/
cp -r %{_vpath_srcdir}/models %{buildroot}%{_datarootdir}/%{name}/
cp -r %{_vpath_srcdir}/README.md %{buildroot}%{_datarootdir}/%{name}/
rm -rf %{buildroot}%{_datarootdir}/%{name}/examples/llama.android
%else
#rm %{buildroot}%{_bindir}/convert*.py
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
%if %{with rocm}
%{_libdir}/libggml-hip.so.*
%endif
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
* Fri Aug 28 2026 Lachlan Marie <lchlnm@pm.me> - b10675-1
 - Update to b10675

* Fri Aug 28 2026 Lachlan Marie <lchlnm@pm.me> - b10666-2
 - On aarch64, build with -DGGML_NATIVE=ON and -DGGML_CPU_KLEIDIAI=ON: the
   package is built and run on the same Apple Silicon/Asahi box, so this
   picks up dotprod/i8mm/bf16 and Arm's own KleidiAI GEMM/GEMV kernels
   instead of the generic armv8-a baseline. Not enabled for the x86_64/rocm
   variant, which keeps its existing explicit AVX* toggles.
 - Enable the BLAS (OpenBLAS) and RPC ggml backends unconditionally; package
   the new libggml-blas.so*, libggml-rpc.so* and ggml-rpc-server
 - Add BuildRequires: openblas-devel

* Fri Aug 28 2026 Lachlan Marie <lchlnm@pm.me> - b10666-1
 - Update to b10666
 - Drop llama-debug-template-parser/llama-template-analysis: upstream removed
   tools/parser (add_subdirectory(parser) dropped from tools/CMakeLists.txt
   after b10590), so these binaries are no longer built

* Sun Aug 23 2026 Lachlan Marie <lchlnm@pm.me> - b10590-1
 - Update to b10590

* Fri Aug 21 2026 Lachlan Marie <lchlnm@pm.me> - b10549-1
 - Update to b10549

* Fri Aug 21 2026 Lachlan Marie <lchlnm@pm.me> - b10548-1
 - Update to b10548

* Fri Aug 21 2026 Lachlan Marie <lchlnm@pm.me> - b10537-1
 - Update to b10537

* Fri Aug 21 2026 Lachlan Marie <lchlnm@pm.me> - b10532-1
 - Update to b10532

* Fri Aug 21 2026 Lachlan Marie <lchlnm@pm.me> - b10531-1
 - Update to b10531

* Fri Aug 21 2026 Lachlan Marie <lchlnm@pm.me> - b10524-1
 - Update to b10524

* Mon Aug 17 2026 Lachlan Marie <lchlnm@pm.me> - b10453-1
 - Update to b10453

* Sun Aug 16 2026 Lachlan Marie <lchlnm@pm.me> - b10448-1
 - Update to b10448

* Sat Aug 15 2026 Lachlan Marie <lchlnm@pm.me> - b10435-1
 - Update to b10435

* Fri Aug 14 2026 Lachlan Marie <lchlnm@pm.me> - b10430-1
 - Update to b10430

* Fri Aug 14 2026 Lachlan Marie <lchlnm@pm.me> - b10423-1
 - Update to b10423

* Thu Aug 13 2026 Lachlan Marie <lchlnm@pm.me> - b10405-1
 - Update to b10405

* Wed Aug 12 2026 Lachlan Marie <lchlnm@pm.me> - b10380-1
 - Update to b10380

* Wed Aug 12 2026 Lachlan Marie <lchlnm@pm.me> - b10362-1
 - Update to b10362

* Tue Aug 11 2026 Lachlan Marie <lchlnm@pm.me> - b10355-1
 - Update to b10355

* Mon Aug 10 2026 Lachlan Marie <lchlnm@pm.me> - b10344-1
 - Update to b10344

* Sun Aug 09 2026 Lachlan Marie <lchlnm@pm.me> - b10333-1
 - Update to b10333

* Sat Aug 08 2026 Lachlan Marie <lchlnm@pm.me> - b10330-1
 - Update to b10330

* Sat Aug 08 2026 Lachlan Marie <lchlnm@pm.me> - b10327-1
 - Update to b10327

* Fri Aug 07 2026 Lachlan Marie <lchlnm@pm.me> - b10321-1
 - Update to b10321

* Fri Aug 07 2026 Lachlan Marie <lchlnm@pm.me> - b10298-1
 - Update to b10298

* Thu Aug 06 2026 Lachlan Marie <lchlnm@pm.me> - b10290-1
 - Update to b10290

* Wed Aug 05 2026 Lachlan Marie <lchlnm@pm.me> - b10276-1
 - Update to b10276

* Mon Aug 03 2026 Lachlan Marie <lchlnm@pm.me> - b10235-1
 - Update to b10235

* Sun Aug 02 2026 Lachlan Marie <lchlnm@pm.me> - b10223-1
 - Update to b10223

* Sat Aug 01 2026 Lachlan Marie <lchlnm@pm.me> - b10218-1
 - Update to b10218

* Sat Aug 01 2026 Lachlan Marie <lchlnm@pm.me> - b10216-1
 - Update to b10216

* Fri Jul 31 2026 Lachlan Marie <lchlnm@pm.me> - b10210-1
 - Update to b10210

* Fri Jul 31 2026 Lachlan Marie <lchlnm@pm.me> - b10199-1
 - Update to b10199

* Thu Jul 30 2026 Lachlan Marie <lchlnm@pm.me> - b10195-1
 - Update to b10195

* Thu Jul 30 2026 Lachlan Marie <lchlnm@pm.me> - b10189-1
 - Update to b10189

* Thu Jul 30 2026 Lachlan Marie <lchlnm@pm.me> - b10182-1
 - Update to b10182

* Wed Jul 29 2026 Lachlan Marie <lchlnm@pm.me> - b10176-1
 - Update to b10176

* Wed Jul 29 2026 Lachlan Marie <lchlnm@pm.me> - b10173-1
 - Update to b10173

* Tue Jul 28 2026 Lachlan Marie <lchlnm@pm.me> - b10172-1
 - Update to b10172

* Tue Jul 28 2026 Lachlan Marie <lchlnm@pm.me> - b10159-1
 - Update to b10159

* Tue Jul 28 2026 Lachlan Marie <lchlnm@pm.me> - b10156-1
 - Update to b10156

* Mon Jul 27 2026 Lachlan Marie <lchlnm@pm.me> - b10149-1
 - Update to b10149

* Sun Jul 26 2026 Lachlan Marie <lchlnm@pm.me> - b10133-1
 - Update to b10133

* Sun Jul 26 2026 Lachlan Marie <lchlnm@pm.me> - b10121-1
 - Update to b10121

* Fri Jul 24 2026 Lachlan Marie <lchlnm@pm.me> - b10103-1
 - Update to b10103

* Wed Jul 22 2026 Lachlan Marie <lchlnm@pm.me> - b10088-1
 - Update to b10088

* Wed Jul 22 2026 Lachlan Marie <lchlnm@pm.me> - b10079-1
 - Update to b10079

* Tue Jul 21 2026 Lachlan Marie <lchlnm@pm.me> - b10075-1
 - Update to b10075

* Mon Jul 20 2026 Lachlan Marie <lchlnm@pm.me> - b10069-1
 - Update to b10069

* Sun Jul 19 2026 Lachlan Marie <lchlnm@pm.me> - b10068-1
 - Update to b10068

* Fri Jul 17 2026 Lachlan Marie <lchlnm@pm.me> - b10064-1
 - Update to b10064

* Fri Jul 17 2026 Lachlan Marie <lchlnm@pm.me> - b10063-1
 - Update to b10063

* Fri Jul 17 2026 Lachlan Marie <lchlnm@pm.me> - b10054-1
 - Update to b10054

* Thu Jul 16 2026 Lachlan Marie <lchlnm@pm.me> - b10052-1
 - Update to b10052

* Thu Jul 16 2026 Lachlan Marie <lchlnm@pm.me> - b10046-1
 - Update to b10046

* Thu Jul 16 2026 Lachlan Marie <lchlnm@pm.me> - b10034-1
 - Update to b10034

* Wed Jul 15 2026 Lachlan Marie <lchlnm@pm.me> - b10015-1
 - Update to b10015

* Tue Jul 14 2026 Lachlan Marie <lchlnm@pm.me> - b10002-1
 - Update to b10002

* Tue Jul 14 2026 Lachlan Marie <lchlnm@pm.me> - b9994-1
 - Update to b9994

* Mon Jul 13 2026 Lachlan Marie <lchlnm@pm.me> - b9987-1
 - Update to b9987

* Mon Jul 13 2026 Lachlan Marie <lchlnm@pm.me> - b9982-1
 - Update to b9982

* Mon Jul 13 2026 Lachlan Marie <lchlnm@pm.me> - b9978-1
 - Update to b9978

* Sun Jul 12 2026 Lachlan Marie <lchlnm@pm.me> - b9977-1
 - Update to b9977

* Sat Jul 11 2026 Lachlan Marie <lchlnm@pm.me> - b9967-1
 - Update to b9967

* Sat Jul 11 2026 Lachlan Marie <lchlnm@pm.me> - b9957-1
 - Update to b9957

* Fri Jul 10 2026 Lachlan Marie <lchlnm@pm.me> - b9956-1
 - Update to b9956

* Fri Jul 10 2026 Lachlan Marie <lchlnm@pm.me> - b9951-1
 - Update to b9951

* Fri Jul 10 2026 Lachlan Marie <lchlnm@pm.me> - b9946-1
 - Update to b9946

* Thu Jul 09 2026 Lachlan Marie <lchlnm@pm.me> - b9940-1
 - Update to b9940

* Thu Jul 09 2026 Lachlan Marie <lchlnm@pm.me> - b9937-1
 - Update to b9937

* Thu Jul 09 2026 Lachlan Marie <lchlnm@pm.me> - b9934-1
 - Update to b9934

* Tue Jul 07 2026 Lachlan Marie <lchlnm@pm.me> - b9892-1
 - Update to b9892

* Tue Jul 07 2026 Lachlan Marie <lchlnm@pm.me> - b9891-1
 - Update to b9891

* Mon Jul 06 2026 Lachlan Marie <lchlnm@pm.me> - b9878-1
 - Update to b9878

* Sun Jul 05 2026 Lachlan Marie <lchlnm@pm.me> - b9873-1
 - Update to b9873

* Thu Jul 02 2026 Lachlan Marie <lchlnm@pm.me> - b9859-1
 - Update to b9859

* Wed Jul 01 2026 Lachlan Marie <lchlnm@pm.me> - b9856-1
 - Update to b9856

* Wed Jul 01 2026 Lachlan Marie <lchlnm@pm.me> - b9853-1
 - Update to b9853

* Wed Jul 01 2026 Lachlan Marie <lchlnm@pm.me> - b9850-1
 - Update to b9850

* Tue Jun 30 2026 Lachlan Marie <lchlnm@pm.me> - b9846-1
 - Update to b9846

* Tue Jun 30 2026 Lachlan Marie <lchlnm@pm.me> - b9843-1
 - Update to b9843

* Tue Jun 30 2026 Lachlan Marie <lchlnm@pm.me> - b9842-1
 - Update to b9842

* Mon Jun 29 2026 Lachlan Marie <lchlnm@pm.me> - b9839-1
 - Update to b9839

* Mon Jun 29 2026 Lachlan Marie <lchlnm@pm.me> - b9835-1
 - Update to b9835

* Sun Jun 28 2026 Lachlan Marie <lchlnm@pm.me> - b9827-1
 - Update to b9827

* Sat Jun 27 2026 Lachlan Marie <lchlnm@pm.me> - b9821-1
 - Update to b9821

* Sat Jun 27 2026 Lachlan Marie <lchlnm@pm.me> - b9817-1
 - Update to b9817

* Fri Jun 26 2026 Lachlan Marie <lchlnm@pm.me> - b9803-1
 - Update to b9803

* Fri Jun 26 2026 Lachlan Marie <lchlnm@pm.me> - b9789-1
 - Update to b9789

* Thu Jun 25 2026 Lachlan Marie <lchlnm@pm.me> - b9784-1
 - Update to b9784

* Thu Jun 25 2026 Lachlan Marie <lchlnm@pm.me> - b9782-1
 - Update to b9782

* Wed Jun 24 2026 Lachlan Marie <lchlnm@pm.me> - b9776-1
 - Update to b9776

* Wed Jun 24 2026 Lachlan Marie <lchlnm@pm.me> - b9775-1
 - Update to b9775

* Tue Jun 23 2026 Lachlan Marie <lchlnm@pm.me> - b9771-1
 - Update to b9771

* Tue Jun 23 2026 Lachlan Marie <lchlnm@pm.me> - b9770-1
 - Update to b9770

* Tue Jun 23 2026 Lachlan Marie <lchlnm@pm.me> - b9763-1
 - Update to b9763

* Mon Jun 22 2026 Lachlan Marie <lchlnm@pm.me> - b9756-1
 - Update to b9756

* Mon Jun 22 2026 Lachlan Marie <lchlnm@pm.me> - b9754-1
 - Update to b9754

* Sun Jun 21 2026 Lachlan Marie <lchlnm@pm.me> - b9744-1
 - Update to b9744

* Sun Jun 21 2026 Lachlan Marie <lchlnm@pm.me> - b9743-1
 - Update to b9743

* Sat Jun 20 2026 Lachlan Marie <lchlnm@pm.me> - b9738-1
 - Update to b9738

* Sat Jun 20 2026 Lachlan Marie <lchlnm@pm.me> - b9733-1
 - Update to b9733

* Sat Jun 20 2026 Lachlan Marie <lchlnm@pm.me> - b9728-1
 - Update to b9728

* Sat Jun 20 2026 Lachlan Marie <lchlnm@pm.me> - b9727-1
 - Update to b9727

* Fri Jun 19 2026 Lachlan Marie <lchlnm@pm.me> - b9722-1
 - Update to b9722

* Fri Jun 19 2026 Lachlan Marie <lchlnm@pm.me> - b9713-1
 - Update to b9713

* Fri Jun 19 2026 Lachlan Marie <lchlnm@pm.me> - b9704-1
 - Update to b9704

* Thu Jun 18 2026 Lachlan Marie <lchlnm@pm.me> - b9694-1
 - Update to b9694

* Thu Jun 18 2026 Lachlan Marie <lchlnm@pm.me> - b9688-1
 - Update to b9688

* Wed Jun 17 2026 Lachlan Marie <lchlnm@pm.me> - b9682-1
 - Update to b9682

* Wed Jun 17 2026 Lachlan Marie <lchlnm@pm.me> - b9680-1
 - Update to b9680

* Wed Jun 17 2026 Lachlan Marie <lchlnm@pm.me> - b9672-1
 - Update to b9672

* Wed Jun 17 2026 Lachlan Marie <lchlnm@pm.me> - b9670-1
 - Update to b9670

* Tue Jun 16 2026 Lachlan Marie <lchlnm@pm.me> - b9660-1
 - Update to b9660

* Mon Jun 15 2026 Lachlan Marie <lchlnm@pm.me> - b9641-1
 - Update to b9641

* Mon Jun 15 2026 Lachlan Marie <lchlnm@pm.me> - b9637-1
 - Update to b9637

* Sun Jun 14 2026 Lachlan Marie <lchlnm@pm.me> - b9626-1
 - Update to b9626

* Sat Jun 13 2026 Lachlan Marie <lchlnm@pm.me> - b9620-1
 - Update to b9620

* Sat Jun 13 2026 Lachlan Marie <lchlnm@pm.me> - b9616-1
 - Update to b9616

* Fri Jun 12 2026 Lachlan Marie <lchlnm@pm.me> - b9608-1
 - Update to b9608

* Fri Jun 12 2026 Lachlan Marie <lchlnm@pm.me> - b9603-1
 - Update to b9603

* Fri Jun 12 2026 Lachlan Marie <lchlnm@pm.me> - b9601-1
 - Update to b9601

* Thu Jun 11 2026 Lachlan Marie <lchlnm@pm.me> - b9596-1
 - Update to b9596

* Thu Jun 11 2026 Lachlan Marie <lchlnm@pm.me> - b9592-1
 - Update to b9592

* Thu Jun 11 2026 Lachlan Marie <lchlnm@pm.me> - b9590-1
 - Update to b9590

* Wed Jun 10 2026 Lachlan Marie <lchlnm@pm.me> - b9587-1
 - Update to b9587

* Wed Jun 10 2026 Lachlan Marie <lchlnm@pm.me> - b9585-1
 - Update to b9585

* Tue Jun 09 2026 Lachlan Marie <lchlnm@pm.me> - b9568-1
 - Update to b9568

* Mon Jun 08 2026 Lachlan Marie <lchlnm@pm.me> - b9555-1
 - Update to b9555

* Mon Jun 08 2026 Lachlan Marie <lchlnm@pm.me> - b9554-1
 - Update to b9554

* Mon Jun 08 2026 Lachlan Marie <lchlnm@pm.me> - b9553-1
 - Update to b9553

* Mon Jun 08 2026 Lachlan Marie <lchlnm@pm.me> - b9550-1
 - Update to b9550

* Sun Jun 07 2026 Lachlan Marie <lchlnm@pm.me> - b9549-1
 - Update to b9549

* Sat Jun 06 2026 Lachlan Marie <lchlnm@pm.me> - b9542-1
 - Update to b9542

* Sat Jun 06 2026 Lachlan Marie <lchlnm@pm.me> - b9536-1
 - Update to b9536

* Fri Jun 05 2026 Lachlan Marie <lchlnm@pm.me> - b9524-1
 - Update to b9524

* Fri Jun 05 2026 Lachlan Marie <lchlnm@pm.me> - b9522-1
 - Update to b9522

* Fri Jun 05 2026 Lachlan Marie <lchlnm@pm.me> - b9519-1
 - Update to b9519

* Fri Jun 05 2026 Lachlan Marie <lchlnm@pm.me> - b9518-1
 - Update to b9518

* Fri Jun 05 2026 Lachlan Marie <lchlnm@pm.me> - b9515-1
 - Update to b9515

* Thu Jun 04 2026 Lachlan Marie <lchlnm@pm.me> - b9496-1
 - Update to b9496

* Wed Jun 03 2026 Lachlan Marie <lchlnm@pm.me> - b9490-1
 - Update to b9490

* Wed Jun 03 2026 Lachlan Marie <lchlnm@pm.me> - b9484-1
 - Update to b9484

* Wed Jun 03 2026 Lachlan Marie <lchlnm@pm.me> - b9481-1
 - Update to b9481

* Fri May 15 2026 Lachlan Marie <lchlnm@pm.me> - b9151-1
 - Update to b9151

* Thu May 14 2026 Lachlan Marie <lchlnm@pm.me> - b9145-1
 - Update to b9145

* Thu May 14 2026 Lachlan Marie <lchlnm@pm.me> - b9144-1
 - Update to b9144

* Thu May 14 2026 Lachlan Marie <lchlnm@pm.me> - b9133-1
 - Update to b9133

* Wed May 13 2026 Lachlan Marie <lchlnm@pm.me> - b9128-1
 - Update to b9128

* Wed May 13 2026 Lachlan Marie <lchlnm@pm.me> - b9122-1
 - Update to b9122

* Tue May 12 2026 Lachlan Marie <lchlnm@pm.me> - b9115-1
 - Update to b9115

* Tue May 12 2026 Lachlan Marie <lchlnm@pm.me> - b9106-1
 - Update to b9106

* Mon May 11 2026 Lachlan Marie <lchlnm@pm.me> - b9102-1
 - Update to b9102

* Mon May 11 2026 Lachlan Marie <lchlnm@pm.me> - b9097-1
 - Update to b9097

* Sun May 10 2026 Lachlan Marie <lchlnm@pm.me> - b9095-1
 - Update to b9095

* Sun May 10 2026 Lachlan Marie <lchlnm@pm.me> - b9093-1
 - Update to b9093

* Sat May 09 2026 Lachlan Marie <lchlnm@pm.me> - b9089-1
 - Update to b9089

* Sat May 09 2026 Lachlan Marie <lchlnm@pm.me> - b9082-1
 - Update to b9082

* Fri May 08 2026 Lachlan Marie <lchlnm@pm.me> - b9071-1
 - Update to b9071

* Fri May 08 2026 Lachlan Marie <lchlnm@pm.me> - b9066-1
 - Update to b9066

* Thu May 07 2026 Lachlan Marie <lchlnm@pm.me> - b9050-1
 - Update to b9050

* Thu May 07 2026 Lachlan Marie <lchlnm@pm.me> - b9049-1
 - Update to b9049

* Wed May 06 2026 Lachlan Marie <lchlnm@pm.me> - b9041-1
 - Update to b9041

* Wed May 06 2026 Lachlan Marie <lchlnm@pm.me> - b9037-1
 - Update to b9037

* Wed May 06 2026 Lachlan Marie <lchlnm@pm.me> - b9033-1
 - Update to b9033

* Tue May 05 2026 Lachlan Marie <lchlnm@pm.me> - b9029-1
 - Update to b9029

* Tue May 05 2026 Lachlan Marie <lchlnm@pm.me> - b9025-1
 - Update to b9025

* Mon May 04 2026 Lachlan Marie <lchlnm@pm.me> - b9016-1
 - Update to b9016

* Sun May 03 2026 Lachlan Marie <lchlnm@pm.me> - b9010-1
 - Update to b9010

* Sat May 02 2026 Lachlan Marie <lchlnm@pm.me> - b9006-1
 - Update to b9006

* Sat May 02 2026 Lachlan Marie <lchlnm@pm.me> - b8999-1
 - Update to b8999

* Sat May 02 2026 Lachlan Marie <lchlnm@pm.me> - b8996-1
 - Update to b8996

* Fri May 01 2026 Lachlan Marie <lchlnm@pm.me> - b8994-1
 - Update to b8994

* Fri May 01 2026 Lachlan Marie <lchlnm@pm.me> - b8992-1
 - Update to b8992

* Thu Apr 30 2026 Lachlan Marie <lchlnm@pm.me> - b8979-1
 - Update to b8979

* Wed Apr 29 2026 Lachlan Marie <lchlnm@pm.me> - b8966-1
 - Update to b8966

* Tue Apr 28 2026 Lachlan Marie <lchlnm@pm.me> - b8953-1
 - Update to b8953

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
