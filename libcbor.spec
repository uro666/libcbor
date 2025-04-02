%define major 0
%define minor 12
%define patch 0
%define libname %mklibname cbor
%define devname %mklibname cbor -d
%define soname %{name}.%{major}.%{minor}.%{patch}

Name:		libcbor
Version:	0.12.0
Release:	1
Summary:	CBOR protocol implementation for C
URL:		https://github.com/PJK/libcbor
License:	MIT
Group:		System/Libraries
Source0:	https://github.com/PJK/libcbor/archive/v%{version}/%{name}-%{version}.tar.gz
Patch0:		libcbor-0.12.0-no-doxygen-timestamps.patch

BuildRequires:	cmake
BuildRequires:	ninja
BuildRequires:	gcc-c++
BuildRequires:	pkgconfig(cmocka)
BuildRequires:	pkgconfig(libcjson)
BuildRequires:	python%{pyver}dist(cython)

# for docs
BuildRequires:	doxygen
BuildRequires:	python%{pyver}dist(sphinx)
BuildRequires:	python%{pyver}dist(sphinx-rtd-theme)
BuildRequires:	python%{pyver}dist(breathe)

%description
libcbor is a C library for parsing and generating CBOR, the general-purpose
schema-less binary data format.

################################
%package -n %{libname}
Summary:	CBOR protocol implementation for C
Group:	Development/C
Suggests:	%{devname} = %{EVRD}
Suggests:	%{libname}-doc = %{EVRD}

%description -n %{libname}
libcbor is a C library for parsing and generating CBOR, the general-purpose
schema-less binary data format.

Main features:

	Complete IETF RFC 8949 (STD 94) conformance
	Robust platform-independent C99 implementation
	Layered architecture offers both control and convenience
	Flexible memory management
	No shared global state - threading friendly
	Proper handling of UTF-8
	Full support for streams & incremental processing
	Extensive documentation and test suite
	No runtime dependencies, small footprint


################################
%package -n %{devname}
Summary:	Development files for %{name}
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Suggests:	%{libname}-doc = %{EVRD}

%description -n %{devname}
Development files (Headers etc.) for %{name}.

################################
%package -n %{libname}-doc
Summary:	Documentation for %{name}
BuildArch:	noarch
Suggests:	%{libname} = %{EVRD}

%description -n %{libname}-doc
Man pages and HTML Documentation for %{name}.

################################
%prep
%autosetup -p1

################################
%build
export CFLAGS="%{optflags} -Wno-return-type"
export CXXFLAGS="$CFLAGS"
export LDFLAGS="%{ldflags}"

# generate docs
%make_build -C doc man

# build libcbor
%cmake -DCMAKE_BUILD_TYPE=RelWithDebInfo \
	-DCMAKE_C_COMPILER="/usr/bin/clang" \
	-DCMAKE_CXX_COMPILER="/usr/bin/clang++" \
	-DWITH_TESTS=ON \
	-DWITH_EXAMPLES=ON \
	-G Ninja
%ninja_build

################################
%install
%ninja_install -C build

################################
# install html and man contents
install -dpm 0755 %{buildroot}%{_docdir}/%{libname}/html
mv ./doc/build/doxygen/html %{buildroot}%{_docdir}/%{libname}
# compress and move man pages
echo $(pwd)
zstd -r --rm ./doc/build/man/libcbor.3
install -Dpm 0644 ./doc/build/man/libcbor.3.zst \
		%{buildroot}%{_mandir}/man3/libcbor.3.zst

%check
export LD_LIBRARY_PATH=%{buildroot}%{_libdir}
cd build
ctest -VV

%post -p /sbin/ldconfig
%postun -p /sbin/ldconfig


################################
%files -n %{libname}
%{_libdir}/*.so.%{major}*
%doc README.md
%license LICENSE.md

%files -n %{devname}
%{_includedir}/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*
%{_libdir}/cmake/*

%files -n %{libname}-doc
%{_mandir}/*/*.3.zst
%{_docdir}/%{libname}/html
%license LICENSE.md
%{_docdir}/%{libname}/README.md
