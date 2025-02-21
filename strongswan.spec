# RPM Spec file for strongSwan 6.0
# This spec file builds strongSwan with common plugins and security features enabled

Name:           strongswan
Version:        6.0.0
Release:        1%{?dist}
Summary:        IPsec-based VPN Solution
License:        GPL-2.0-or-later

URL:            https://www.strongswan.org
Source0:        https://download.strongswan.org/strongswan.tar.bz2

# Build requirements for core functionality
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  libtool
BuildRequires:  systemd-devel
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  pkgconfig
BuildRequires:  gmp-devel
BuildRequires:  libcurl-devel
BuildRequires:  openssl-devel
BuildRequires:  trousers-devel
BuildRequires:  libxml2-devel
BuildRequires:  sqlite-devel
BuildRequires:  ldns-devel
BuildRequires:  unbound-devel
BuildRequires:  systemd
BuildRequires:  openldap-devel

# Runtime requirements
Requires:       gmp
Requires:       libcurl
Requires:       openssl
Requires:       trousers
Requires:       libxml2
Requires:       sqlite
Requires:       ldns
Requires:       unbound
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
strongSwan is an OpenSource IPsec-based VPN solution for Linux and other operating
systems. It implements both the IKEv1 and IKEv2 key exchange protocols and
supports many popular cipher suites and cryptographic algorithms.

%prep
%autosetup -n %{name}-%{version}

%build
# Configure with common options and security features
%configure \
    --sysconfdir=%{_sysconfdir} \
    --with-systemdsystemunitdir=%{_unitdir} \
    --enable-curl \
    --enable-openssl \
    --enable-sqlite \
    --enable-af-alg \
    --enable-gcrypt \
    --enable-pkcs11 \
    --enable-agent \
    --enable-farp \
    --enable-dhcp \
    --enable-eap-radius \
    --enable-eap-identity \
    --enable-eap-md5 \
    --enable-eap-mschapv2 \
    --enable-eap-tls \
    --enable-eap-ttls \
    --enable-eap-peap \
    --enable-xauth-eap \
    --enable-unity \
    --enable-monolithic \
    --enable-ldap \
    --enable-cmd \
    --enable-acert \
    --enable-aikgen \
    --enable-tpm \
    --enable-sha3 \
    --enable-systemd

%make_build

%install
%make_install
# Remove unwanted .la files
find %{buildroot} -type f -name '*.la' -delete
# Ensure correct permissions on config files
chmod 644 %{buildroot}%{_sysconfdir}/strongswan.conf
chmod 644 %{buildroot}%{_sysconfdir}/ipsec.conf
chmod 600 %{buildroot}%{_sysconfdir}/ipsec.secrets

%post
%systemd_post strongswan.service
%systemd_post strongswan-starter.service

%preun
%systemd_preun strongswan.service
%systemd_preun strongswan-starter.service

%postun
%systemd_postun_with_restart strongswan.service
%systemd_postun_with_restart strongswan-starter.service

%files
%license COPYING
%doc README NEWS TODO
%{_sbindir}/*
%{_libdir}/ipsec/*
%{_libdir}/strongswan/*
%{_libexecdir}/ipsec/*
%config(noreplace) %{_sysconfdir}/strongswan.conf
%config(noreplace) %{_sysconfdir}/ipsec.conf
%config(noreplace) %attr(600,root,root) %{_sysconfdir}/ipsec.secrets
%config(noreplace) %{_sysconfdir}/strongswan.d/
%config(noreplace) %{_sysconfdir}/swanctl/
%{_unitdir}/strongswan.service
%{_unitdir}/strongswan-starter.service
%{_datadir}/strongswan
%{_mandir}/man[158]/*
%{_mandir}/man8/*.8*

%changelog
* Fri Feb 21 2025 Package Maintainer <maintainer@example.com> - 6.0.0-1
- Initial package for strongSwan 6.0.0
