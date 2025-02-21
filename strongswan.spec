# RPM Spec file for strongSwan 6.0
# This spec file includes cross-compilation support and proper architecture handling

Name:           strongswan
Version:        6.0.0
Release:        1%{?dist}
Summary:        IPsec-based VPN Solution
License:        GPL-2.0-or-later

URL:            https://www.strongswan.org
Source0:        https://download.strongswan.org/%{name}-%{version}.tar.bz2

# Build requirements determined from configure script and plugin list
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  libtool
BuildRequires:  systemd-devel
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  pkgconfig
# Core crypto dependencies
BuildRequires:  openssl-devel
BuildRequires:  gmp-devel
BuildRequires:  libgcrypt-devel
# Authentication and identity management
BuildRequires:  openldap-devel
# Network and database support
BuildRequires:  libcurl-devel
BuildRequires:  sqlite-devel
# TPM support
BuildRequires:  tpm2-tss-devel

# Runtime dependencies
Requires:       gmp
Requires:       libcurl
Requires:       openssl
Requires:       libgcrypt
Requires:       openldap
Requires:       sqlite
Requires:       tpm2-tss
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd

%description
strongSwan is an OpenSource IPsec-based VPN solution for Linux and other operating
systems. It implements both the IKEv1 and IKEv2 key exchange protocols.

# Disable the format-security error that conflicts with strongSwan's build
%define _hardening_cflags %(echo '%{build_cflags}' | sed 's/-Werror=format-security//')
%global build_cflags %{_hardening_cflags}

%prep
%autosetup -n %{name}-%{version}

%build
# Determine the appropriate host for cross-compilation
%ifarch aarch64
%global strongswan_host aarch64-redhat-linux
%endif
%ifarch x86_64
%global strongswan_host x86_64-redhat-linux
%endif

# Configure with cross-compilation support and feature set
./configure \
    --prefix=%{_prefix} \
    --sysconfdir=%{_sysconfdir} \
    --host=%{strongswan_host} \
    --build=%{_build} \
    --libdir=%{_libdir} \
    --with-systemdsystemunitdir=%{_unitdir} \
    --enable-curl \
    --enable-openssl \
    --enable-sqlite \
    --enable-gcrypt \
    --enable-pkcs11 \
    --enable-af-alg \
    --enable-agent \
    --enable-farp \
    --enable-dhcp \
    --enable-eap-radius \
    --enable-eap-identity \
    --enable-eap-md5 \
    --enable-eap-tls \
    --enable-eap-ttls \
    --enable-eap-peap \
    --enable-xauth-eap \
    --enable-xauth-noauth \
    --enable-unity \
    --enable-monolithic \
    --enable-ldap \
    --enable-tpm \
    --enable-systemd


%make_build

%install
%make_install
# Remove unwanted .la files
find %{buildroot} -type f -name '*.la' -delete
# Set correct permissions for config files
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
- Added cross-compilation support
- Configured for both x86_64 and aarch64 architectures
