Name:           kasmvncserver
Version:        1.0.0
Release:        1%{?dist}
Summary:        VNC server accessible from a web browser

License: GPLv2+
URL: https://github.com/kasmtech/KasmVNC

BuildRequires: rsync
Requires: xorg-x11-xauth, xorg-x11-xkb-utils, xkeyboard-config, xorg-x11-server-utils, openssl, perl, perl-Switch, perl-YAML-Tiny, perl-Hash-Merge-Simple, perl-Scalar-List-Utils, perl-List-MoreUtils, perl-Try-Tiny
Conflicts: tigervnc-server, tigervnc-server-minimal

%description
VNC stands for Virtual Network Computing. It is, in essence, a remote
display system which allows you to view a computing `desktop' environment
not only on the machine where it is running, but from anywhere on the
Internet and from a wide variety of machine architectures.

KasmVNC has different goals than TigerVNC:

Web-based - KasmVNC is designed to provide a web accessible remote desktop.
It comes with a web server and web-socket server built in. There is no need to
install other components. Simply run and navigate to your desktop's URL on the
port you specify. While you can still tun on the legacy VNC port, it is
disabled by default.

Security - KasmVNC defaults to HTTPS and allows for HTTP Basic Auth. VNC
Password authentication is limited by specification to 8 characters and is not
sufficient for use on an internet accessible remote desktop. Our goal is to
create a by default secure, web based experience.

Simplicity - KasmVNC aims at being simple to deploy and configure.

WARNING: this package requires EPEL.

%prep

%install
rm -rf $RPM_BUILD_ROOT

TARGET_OS=$(lsb_release -is | tr '[:upper:]' '[:lower:]')
TARGET_OS_CODENAME=$(lsb_release -cs | tr '[:upper:]' '[:lower:]')
TARBALL=$RPM_SOURCE_DIR/kasmvnc.${TARGET_OS}_${TARGET_OS_CODENAME}.tar.gz
TAR_DATA=$(mktemp -d)
tar -xzf "$TARBALL" -C "$TAR_DATA"

SRC=$TAR_DATA/usr/local
SRC_BIN=$SRC/bin
DESTDIR=$RPM_BUILD_ROOT
DST_MAN=$DESTDIR/usr/share/man/man1

mkdir -p $DESTDIR/usr/bin $DESTDIR/usr/share/man/man1 \
  $DESTDIR/usr/share/doc/kasmvncserver $DESTDIR/usr/lib \
  $DESTDIR/usr/share/perl5 $DESTDIR/etc/kasmvnc

cp $SRC_BIN/Xvnc $DESTDIR/usr/bin;
cp $SRC_BIN/vncserver $DESTDIR/usr/bin;
cp -a $SRC_BIN/KasmVNC $DESTDIR/usr/share/perl5/
cp $SRC_BIN/vncconfig $DESTDIR/usr/bin;
cp $SRC_BIN/kasmvncpasswd $DESTDIR/usr/bin;
cp $SRC_BIN/kasmxproxy $DESTDIR/usr/bin;
cp -r $SRC/lib/kasmvnc/ $DESTDIR/usr/lib/kasmvncserver
cd $DESTDIR/usr/bin && ln -s kasmvncpasswd vncpasswd;
cp -r $SRC/share/doc/kasmvnc*/* $DESTDIR/usr/share/doc/kasmvncserver/
rsync -r --exclude '.git*' --exclude po2js --exclude xgettext-html \
  --exclude www/utils/ --exclude .eslintrc --exclude configure \
  $SRC/share/kasmvnc $DESTDIR/usr/share

sed -i -e 's!pem_certificate: .\+$!pem_certificate: /etc/pki/tls/private/kasmvnc.pem!' \
    $DESTDIR/usr/share/kasmvnc/kasmvnc_defaults.yaml
sed -i -e 's!pem_key: .\+$!pem_key: /etc/pki/tls/private/kasmvnc.pem!' \
    $DESTDIR/usr/share/kasmvnc/kasmvnc_defaults.yaml
sed -e 's/^\([^#]\)/# \1/' $DESTDIR/usr/share/kasmvnc/kasmvnc_defaults.yaml > \
  $DESTDIR/etc/kasmvnc/kasmvnc.yaml
cp $SRC/man/man1/Xvnc.1 $DESTDIR/usr/share/man/man1/;
cp $SRC/share/man/man1/vncserver.1 $DST_MAN;
cp $SRC/share/man/man1/vncconfig.1 $DST_MAN;
cp $SRC/share/man/man1/vncpasswd.1 $DST_MAN;
cp $SRC/share/man/man1/kasmxproxy.1 $DST_MAN;
cd $DST_MAN && ln -s vncpasswd.1 kasmvncpasswd.1;


%files
%config(noreplace) /etc/kasmvnc

/usr/bin/*
/usr/lib/kasmvncserver
/usr/share/man/man1/*
/usr/share/perl5/KasmVNC
/usr/share/kasmvnc

%license /usr/share/doc/kasmvncserver/LICENSE.TXT
%doc /usr/share/doc/kasmvncserver/README.md

%changelog
* Tue Nov 29 2022 KasmTech <info@kasmweb.com> - 1.0.0-1
- Upstream release
* Tue Nov 29 2022 KasmTech <info@kasmweb.com> - 1.0.0-1
- Upstream release
* Tue Mar 22 2022 KasmTech <info@kasmweb.com> - 0.9.3~beta-1
* Fri Feb 12 2021 KasmTech <info@kasmweb.com> - 0.9.1~beta-1
- Initial release of the rpm package.

%post
  kasmvnc_group="kasmvnc-cert"

  create_kasmvnc_group() {
    if ! getent group "$kasmvnc_group" >/dev/null; then
	    groupadd --system "$kasmvnc_group"
    fi
  }

  make_self_signed_certificate() {
    local cert_file=/etc/pki/tls/private/kasmvnc.pem
    [ -f "$cert_file" ] && return 0

    openssl req -x509 -nodes -days 3650 -newkey rsa:2048 \
      -keyout "$cert_file" \
      -out "$cert_file" -subj \
      "/C=US/ST=VA/L=None/O=None/OU=DoFu/CN=kasm/emailAddress=none@none.none"
    chgrp "$kasmvnc_group" "$cert_file"
    chmod 640 "$cert_file"
  }

  create_kasmvnc_group
  make_self_signed_certificate

%postun
  rm -f /etc/pki/tls/private/kasmvnc.pem
