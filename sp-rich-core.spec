Name: sp-rich-core

Version: 1.74.8
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
/lib/systemd/system/rich-core-early-collect.service
/lib/systemd/system/graphical.target.wants/rich-core-early-collect.service
/usr/lib/sysctl.d/sp-rich-core.conf
%{_sbindir}/rich-core-dumper
%{_libexecdir}/rich-core-check-oneshot
/usr/lib/startup/preinit/late.d/rich-core-preinit
/var/cache/core-dumps

%package postproc
Summary: Rich core postprocessing
Group: Development/Tools
Requires: lzop
Requires: gzip

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
Requires: gdb-qml-stacktrace = %{version}-%{release}
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

%package -n gdb-qml-stacktrace
Summary: Allows inspecting QML stack traces in gdb
Group: Development/Tools

%description -n gdb-qml-stacktrace
A gdb frame filter that prints a QML stack trace in addition to a regular backtrace of a Qt/QML application.

%files -n gdb-qml-stacktrace
%defattr(-,root,root,-)
%config %{_sysconfdir}/gdbinit.d/*
%{_datadir}/gdb/python/gdb/*

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
mkdir -p %{buildroot}/usr/lib/sysctl.d
mkdir -m 777 -p %{buildroot}/var/cache/core-dumps
mkdir -p %{buildroot}/%{_datadir}/%{name}-tests
make install DESTDIR=%{buildroot}

%clean
make distclean

%post
/sbin/sysctl -p /usr/lib/sysctl.d/sp-rich-core.conf

%postun
if [ "$1" = 0 ]; then
  rm -f /var/cache/core-dumps/{*.tmp,oneshots}
fi
