%global commit 057ee8fc9c9da65795a6f14497fc408c2fe23c76
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global commitdate 20261031

Name:           rustunes
Version:        0.1.0
Release:        1.%{commitdate}git%{shortcommit}%{?dist}
Summary:        Sync a music library into the iPhone Music app

License:        MIT
URL:            https://github.com/fbiba/rustunes
Source0:        %{url}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
Patch0:         0001-ios26-support.patch

BuildRequires:  cargo
BuildRequires:  gcc
BuildRequires:  anda-srpm-macros
BuildRequires:  cargo-rpm-macros
BuildRequires:  ffmpeg-free
Requires:       usbmuxd
Requires:       ffmpeg-free

%description
Syncs a local music library into the stock Music app on an iPhone over USB
or Wi-Fi, through Apple's own sync service.

%prep
%autosetup -n %{name}-%{commit} -p1

%build
%cargo_prep_online
%cargo_build

%install
install -Dm755 target/rpm/%{name} %{buildroot}%{_bindir}/%{name}
install -d %{buildroot}%{bash_completions_dir}
target/rpm/%{name} completions bash > %{buildroot}%{bash_completions_dir}/%{name}

%check
%cargo_test

%files
%license LICENSE
%doc README.md
%{_bindir}/%{name}
%{bash_completions_dir}/%{name}

%changelog
* Mon Nov 02 2026 Lachlan Marie <lchlnm@pm.me> - 0.1.0-1.20261031git057ee8f
- Initial package
- iOS 26 support patch
