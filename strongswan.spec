%global _hardened_build 1
%bcond_without python3
%bcond_without perl
%bcond_with    check

# For Fedora 36+ and RHEL 9+, disable trousers
%if (0%{?fedora} && 0%{?fedora} < 36) || (0%{?rhel} && 0%{?rhel} < 9)
%bcond_without tss_trousers
%else
%bcond_with tss_trousers
%endif

%global forgeurl0 https://github.com/strongswan/strongswan

Name:           strongswan
Version:        6.0.0
Release:        1%{?dist}
Summary:        An OpenSource IPsec-based VPN and TNC solution
License:        GPL-2.0-or-later
URL:            https://www.strongswan.org/
VCS:            git:%{forgeurl0}
Source0:        https://download.strongswan.org/%{name}-%{version}.tar.bz2
Source3:        tmpfiles-strongswan.conf

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  systemd
BuildRequires:  systemd-devel
BuildRequires:  systemd-rpm-macros
BuildRequires:  gmp-devel
BuildRequires:  libcurl-devel
BuildRequires:  openldap-devel
BuildRequires:  openssl-devel
%if 0%{?fedora} >= 41
BuildRequires:  openssl-devel-engine
%endif
BuildRequires:  sqlite-devel
BuildRequires:  gettext-devel
BuildRequires:  libxml2-devel
BuildRequires:  pam-devel
BuildRequires:  json-c-devel
BuildRequires:  libgcrypt-devel
BuildRequires:  iptables-devel
BuildRequires:  libcap-devel
BuildRequires:  tpm2-tss-devel
Recommends:     tpm2-tools

%if %{with python3}
BuildRequires:  python3-devel
BuildRequires:  python3-setuptools
BuildRequires:  python3-pytest
%endif

%if %{with perl}
BuildRequires:  perl-devel perl-generators
BuildRequires:  perl(ExtUtils::MakeMaker)
%endif

%if %{with tss_trousers}
BuildRequires:  trousers-devel
%endif

BuildRequires:  NetworkManager-libnm-devel
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
The strongSwan IPsec implementation supports both the IKEv1 and IKEv2 key
exchange protocols in conjunction with the native NETKEY IPsec stack of the
Linux kernel.

%package libipsec
Summary: Strongswan's libipsec backend
%description libipsec
The kernel-libipsec plugin provides an IPsec backend that works entirely
in userland, using TUN devices and its own IPsec implementation libipsec.

%package charon-nm
Summary:        NetworkManager plugin for Strongswan
Requires:       dbus
Obsoletes:      strongswan-NetworkManager < 0:5.0.4-5
Conflicts:      strongswan-NetworkManager < 0:5.0.4-5
Conflicts:      NetworkManager-strongswan < 1.4.2-1
%description charon-nm
NetworkManager plugin integrates a subset of Strongswan capabilities
to NetworkManager.

%package sqlite
Summary: SQLite support for strongSwan
Requires: strongswan = %{version}-%{release}
%description sqlite
The sqlite plugin adds an SQLite database backend to strongSwan.

%package tnc-imcvs
Summary: Trusted network connect (TNC)'s IMC/IMV functionality
Requires: strongswan = %{version}-%{release}
Requires: strongswan-sqlite = %{version}-%{release}
%description tnc-imcvs
This package provides Trusted Network Connect's (TNC) architecture support.

%if %{with python3}
%package -n python3-vici
Summary: Strongswan Versatile IKE Configuration Interface python bindings
BuildArch: noarch
%description -n python3-vici
VICI is an attempt to improve the situation for system integrators by providing
a stable IPC interface, allowing external tools to query, configure
and control the IKE daemon.
%endif

%if %{with perl}
%package -n perl-vici
Summary: Strongswan Versatile IKE Configuration Interface perl bindings
BuildArch: noarch
%description -n perl-vici
VICI is an attempt to improve the situation for system integrators by providing
a stable IPC interface, allowing external tools to query, configure
and control the IKE daemon.
%endif

%prep
%autosetup -p1

%build
%configure --disable-static \
    --with-ipsec-script=strongswan \
    --sysconfdir=%{_sysconfdir}/strongswan \
    --with-ipsecdir=%{_libexecdir}/strongswan \
    --bindir=%{_libexecdir}/strongswan \
    --with-ipseclibdir=%{_libdir}/strongswan \
    --with-piddir=%{_rundir}/strongswan \
    --with-nm-ca-dir=%{_sysconfdir}/strongswan/ipsec.d/cacerts/ \
    --enable-bypass-lan \
    --enable-tss-tss2 \
    --enable-nm \
    --enable-systemd \
    --enable-openssl \
    --enable-unity \
    --enable-curl \
    --enable-sqlite \
    --enable-sql \
    --enable-pkcs11 \
    --enable-tpm \
    --enable-vici \
    --enable-swanctl \
    --enable-eap-identity \
    --enable-eap-md5 \
    --enable-eap-tls \
    --enable-eap-ttls \
    --enable-eap-peap \
    --enable-eap-mschapv2 \
    --enable-xauth-eap \
    --enable-xauth-pam \
    --enable-dhcp \
    --enable-farp \
    --enable-cmd \
%ifarch x86_64 %{ix86}
    --enable-aesni \
%endif
%if %{with python3}
    PYTHON=%{python3} --enable-python-eggs \
%endif
%if %{with perl}
    --enable-perl-cpan \
%endif
%if %{with tss_trousers}
    --enable-tss-trousers \
%endif
    --enable-kernel-libipsec \
    --with-capabilities=libcap \
    CPPFLAGS="-DSTARTER_ALLOW_NON_ROOT"

%make_build

%if %{with python3}
pushd src/libcharon/plugins/vici/python
%make_build
sed -e "s,/var/run/charon.vici,%{_rundir}/strongswan/charon.vici," -i vici/session.py
popd
%endif

%if %{with perl}
pushd src/libcharon/plugins/vici/perl/Vici-Session/
perl Makefile.PL INSTALLDIRS=vendor
%make_build
popd
%endif

%install
%make_install

%if %{with python3}
pushd src/libcharon/plugins/vici/python
%py3_install
popd
%endif

%if %{with perl}
%make_install -C src/libcharon/plugins/vici/perl/Vici-Session
rm -f %{buildroot}{%{perl_archlib}/perllocal.pod,%{perl_vendorarch}/auto/Vici/Session/.packlist}
%endif

# Create ipsec.d directory tree
install -d -m 700 %{buildroot}%{_sysconfdir}/strongswan/ipsec.d
for i in aacerts acerts certs cacerts crls ocspcerts private reqs; do
    install -d -m 700 %{buildroot}%{_sysconfdir}/strongswan/ipsec.d/${i}
done

install -d -m 0700 %{buildroot}%{_rundir}/strongswan
install -D -m 0644 %{SOURCE3} %{buildroot}/%{_tmpfilesdir}/strongswan.conf
install -D -m 0644 %{SOURCE3} %{buildroot}/%{_tmpfilesdir}/strongswan-starter.conf

find %{buildroot} -type f -name '*.la' -delete
rm %{buildroot}%{_libdir}/strongswan/*.so

%post
%systemd_post strongswan.service strongswan-starter.service

%preun
%systemd_preun strongswan.service strongswan-starter.service

%postun
%systemd_postun_with_restart strongswan.service strongswan-starter.service

%files
%doc README NEWS TODO
%license COPYING
%dir %attr(0755,root,root) %{_sysconfdir}/strongswan
%config(noreplace) %{_sysconfdir}/strongswan/*
%dir %{_libdir}/strongswan
%exclude %{_libdir}/strongswan/imcvs
%dir %{_libdir}/strongswan/plugins
%dir %{_libexecdir}/strongswan
%{_unitdir}/strongswan.service
%{_unitdir}/strongswan-starter.service
%{_sbindir}/charon-cmd
%{_sbindir}/charon-systemd
%{_sbindir}/strongswan
%{_sbindir}/swanctl
%{_libdir}/strongswan/*.so.*
%exclude %{_libdir}/strongswan/libipsec.so.*
%{_libdir}/strongswan/plugins/*.so
%exclude %{_libdir}/strongswan/plugins/libstrongswan-sqlite.so
%exclude %{_libdir}/strongswan/plugins/libstrongswan-kernel-libipsec.so
%{_libexecdir}/strongswan/*
%exclude %{_libexecdir}/strongswan/charon-nm
%{_mandir}/man?/*.gz
%attr(0755,root,root) %dir %{_rundir}/strongswan
%attr(0644,root,root) %{_tmpfilesdir}/strongswan.conf
%attr(0644,root,root) %{_tmpfilesdir}/strongswan-starter.conf

%files sqlite
%{_libdir}/strongswan/plugins/libstrongswan-sqlite.so

%files libipsec
%{_libdir}/strongswan/libipsec.so.*
%{_libdir}/strongswan/plugins/libstrongswan-kernel-libipsec.so

%files charon-nm
%doc COPYING
%{_datadir}/dbus-1/system.d/nm-strongswan-service.conf
%{_libexecdir}/strongswan/charon-nm

%if %{with python3}
%files -n python3-vici
%license COPYING
%doc src/libcharon/plugins/vici/python/README.rst
%{python3_sitelib}/vici
%{python3_sitelib}/vici-%{version}-py*.egg-info
%endif

%if %{with perl}
%files -n perl-vici
%license COPYING
%{perl_vendorlib}/Vici
%endif

%changelog
* Fri Feb 22 2025 Package Maintainer <maintainer@example.com> - 6.0.0-1
- Update to strongSwan 6.0.0
- Aligned with Fedora packaging guidelines
- Added support for python3 and perl VICI bindings
- Improved systemd integration
- Enhanced TPM2 support
