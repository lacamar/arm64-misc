Name:           libsignal-jni
Version:        0.106.1
Release:        1%{?dist}
Summary:        libsignal JNI native library for signal-cli

License:        AGPL-3.0-only
URL:            https://github.com/signalapp/libsignal
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/libsignal-%{version}.tar.gz
Source1:        %{name}-%{version}-vendor.tar.zst

ExclusiveArch:  aarch64
BuildRequires:  rust-packaging
BuildRequires:  cmake
BuildRequires:  clang
BuildRequires:  gcc-c++
BuildRequires:  perl
BuildRequires:  git-core
BuildRequires:  golang
BuildRequires:  protobuf-compiler
BuildRequires:  protobuf-devel
Supplements:    signal-cli

%description
Native JNI bridge of libsignal, version-locked to the libsignal-client jar bundled with signal-cli.

%prep
%autosetup -n libsignal-%{version} -p1 -a1
mv %{name}-%{version}-vendor/vendor vendor
mkdir -p .cargo
sed "s#^directory = .*#directory = \"vendor\"#" %{name}-%{version}-vendor/vendor-config.toml > .cargo/config.toml

%build
export RUSTFLAGS="--cfg aes_armv8 --cfg tokio_unstable ${RUSTFLAGS:-}"
cargo build --release --offline --locked -p libsignal-jni

%install
install -Dm755 target/release/libsignal_jni.so %{buildroot}%{_libdir}/libsignal_jni.so

%files
%license LICENSE
%{_libdir}/libsignal_jni.so
%define debug_package %{nil}

%changelog
* Wed Nov 25 2026 lacamar <lchlnm@pm.me> - 0.106.1-1
- Initial package
