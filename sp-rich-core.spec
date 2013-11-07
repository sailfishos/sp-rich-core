Name: sp-rich-core

Version: 1.71.19
Release: 1
Summary: Create rich core dumps
Group: Development/Tools
License: GPL-2
URL: http://github.com/mer-tools
Source0: %{name}-%{version}.tar.gz  
Source1: _src
BuildRequires: elfutils-libelf-devel
BuildRequires: autoconf
BuildRequires: gcc-c++
Requires: sed
Requires: coreutils
Requires: lzop
Requires: sp-endurance
Requires: core-reducer
Requires: binutils

%description
Tool that creates rich core dumps, which include information about system state and core in a single compressed file. Requires a kernel that supports piping core dumps. 

%files
%defattr(-,root,root,-)
/lib/systemd/system/rich-core-pattern.service
/lib/systemd/system/basic.target.wants/rich-core-pattern.service
%{_sbindir}/rich-core-dumper
/var/cache/core-dumps

%package postproc
Summary: Rich core postprocessing
Group: Development/Tools
Requires: lzop

%description postproc
Tools to extract information from rich cores.

%files postproc
%defattr(-,root,root,-)
%{_bindir}/rich-core-extract

%package tests
Summary: Tests for the sp-rich-core packages
Group: Development/Libraries
Requires: %{name} = %{version}-%{release}
Requires: %{name}-postproc = %{version}-%{release}
Requires: core-reducer = %{version}-%{release}
# From mer-qa project
Requires: blts-tools

%description tests
Provides test cases for sp-rich-core, sp-rich-core-postproc and core-reducer.

%files tests
%defattr(-,root,root,-)
%{_datadir}/%{name}-tests/*

%package -n core-reducer
Summary: Reduce the size of a core dump
Group: Development/Tools
Requires: %{name} = %{version}-%{release}
Requires: elfutils-libelf

%description -n core-reducer
Create core dumps that have a reduced size, allowing them to be transported between systems, even those with limited network throughput.

%files -n core-reducer
%defattr(-,root,root,-)
%{_bindir}/core-reducer

%prep
# Adjusting %%setup since git-pkg unpacks to src/
# %%setup -q -n %%{name}-%%{version}
%setup -q -n src

%build
touch NEWS README AUTHORS ChangeLog
autoreconf --install
%configure --prefix=/usr
make

%install
mkdir -p %{buildroot}/%{_sbindir}
mkdir -p %{buildroot}/lib/systemd/system
mkdir -p %{buildroot}/lib/systemd/system/basic.target.wants
mkdir -m 777 -p %{buildroot}/var/cache/core-dumps
mkdir -p %{buildroot}/%{_datadir}/%{name}-tests
make install DESTDIR=%{buildroot}

%clean
make distclean

%post
systemctl daemon-reload
systemctl start rich-core-pattern.service
