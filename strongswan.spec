%define         strongswan_docdir    %{_defaultdocdir}/%{name}
%define         strongswan_libdir    /usr/libexec/strongswan
%define         strongswan_configs   /etc/strongswan.d
%define         strongswan_datadir   /usr/share/strongswan
%define         strongswan_plugins   %{strongswan_libdir}/plugins
%define         strongswan_templates %{strongswan_datadir}/templates
%bcond_without  stroke
%bcond_with     tests
%bcond_without  fipscheck
%bcond_with     integrity
%bcond_without  farp
%bcond_without  afalg
%bcond_without  mysql
%bcond_without  sqlite
%bcond_without  gcrypt
%bcond_without  nm
%bcond_without  systemd

Name:           strongswan
Version:        6.0.0
Release:        1%{?dist}
Summary:        IPsec-based VPN solution
License:        GPL-2.0-or-later
Group:          Productivity/Networking/Security
URL:            https://www.strongswan.org/
Source0:        http://download.strongswan.org/strongswan.tar.bz2
Source1:        http://download.strongswan.org/strongswan.tar.bz2.sig
Source2:        %{name}.init.in
Source3:        %{name}-rpmlintrc
Source4:        README.RHEL
Source5:        %{name}.keyring
Source7:        fips-enforce.conf
Patch2:         %{name}_ipsec_service.patch
Patch5:         0005-ikev1-Don-t-retransmit-Aggressive-Mode-response.patch
Patch6:         harden_strongswan.service.patch
Patch7:         init.patch

BuildRequires:  autoconf
BuildRequires:  automake
BuildRequires:  bison
BuildRequires:  curl-devel
BuildRequires:  flex
BuildRequires:  gmp-devel
BuildRequires:  gperf
BuildRequires:  iptables
BuildRequires:  libpcap-devel
BuildRequires:  openssl-devel
BuildRequires:  libtool
BuildRequires:  openldap-devel
BuildRequires:  pam-devel
BuildRequires:  pcsc-lite-devel
BuildRequires:  pkg-config
BuildRequires:  sqlite-devel
BuildRequires:  systemd-devel
Obsoletes:      strongswan-libs0 < %version-%release
Provides:       strongswan-libs0 = %version-%release
Requires:       systemd

%description
StrongSwan is an IPsec-based VPN solution for Linux. It supports IKEv1 and IKEv2, encryption, NAT traversal, and more.

%prep
%autosetup -p1

%build
autoreconf --force --install
%configure \
    --with-plugindir=%{strongswan_plugins} \
    --with-systemdsystemunitdir=%{_unitdir} \
    --enable-pkcs11 \
    --enable-openssl \
    --enable-agent \
    --enable-blowfish \
    --enable-ctr \
    --enable-ccm \
    --enable-gcm \
    --enable-md4 \
    --enable-eap-md5 \
    --enable-eap-mschapv2 \
    --enable-eap-tls \
    --enable-eap-radius \
    --enable-xauth-eap \
    --enable-xauth-pam \
    --enable-tnc-pdp \
    --enable-dhcp \
    --enable-ldap \
    --enable-curl \
    --enable-bypass-lan \
    --disable-static
%make_build

%install
%make_install
install -d -m 0755 %{buildroot}/%{_tmpfilesdir}
echo 'd /run/%{name} 0770 root root' > %{buildroot}%{_tmpfilesdir}/%{name}.conf

%post
/sbin/ldconfig
systemctl daemon-reload
systemctl enable --now strongswan.service || :

%postun
/sbin/ldconfig
if [ $1 -eq 0 ]; then
    systemctl stop strongswan.service || :
    systemctl disable strongswan.service || :
    systemctl daemon-reexec || :
fi

%files
%dir %{strongswan_docdir}
%{strongswan_docdir}/README.RHEL
%config(noreplace) %attr(600,root,root) /etc/swanctl/swanctl.conf
%dir /etc/swanctl
%{_unitdir}/strongswan.service
%{_sbindir}/charon-systemd
%{_bindir}/pki
%{_sbindir}/swanctl
%{_mandir}/man1/pki*.1*
%{_mandir}/man5/strongswan.conf.5*
%dir %{strongswan_plugins}
%{strongswan_plugins}/libstrongswan-drbg.so
%{strongswan_plugins}/libstrongswan-updown.so
%{_tmpfilesdir}/%{name}.conf
%config(noreplace) %attr(600,root,root) /etc/strongswan.conf
%dir %{strongswan_configs}
%dir %{strongswan_configs}/charon
%config(noreplace) %attr(600,root,root) %{strongswan_configs}/charon.conf
%config(noreplace) %attr(600,root,root) %{strongswan_configs}/charon-systemd.conf
%config(noreplace) %attr(600,root,root) %{strongswan_configs}/charon-logging.conf
%config(noreplace) %attr(600,root,root) %{strongswan_configs}/imcv.conf
%config(noreplace) %attr(600,root,root) %{strongswan_configs}/pki.conf
%config(noreplace) %attr(600,root,root) %{strongswan_configs}/pool.conf
%config(noreplace) %attr(600,root,root) %{strongswan_configs}/tnc.conf
%config(noreplace) %attr(600,root,root) %{strongswan_configs}/swanctl.conf

%changelog
* Sat Feb 22 2025 - Adapted for AlmaLinux 9
