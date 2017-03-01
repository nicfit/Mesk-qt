# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

inherit distutils

DESCRIPTION="Mesk Media Player"
HOMEPAGE="http://eyed3.nicfit.net/"
SRC_URI="http://eyed3.nicfit.net/releases/${P}.tar.gz"
LICENSE="GPL-2"

SLOT="0"
KEYWORDS="x86"
IUSE="alsa oss esd"
DEPEND=">=virtual/python-2.3
=dev-python/pysqlite-1.0
>=dev-python/eyeD3-0.6.4
>=media-libs/gstreamer-0.8.9
>=media-libs/gst-plugins-0.8.8
>=media-plugins/gst-plugins-mad-0.8.8
>=media-plugins/gst-plugins-gnomevfs-0.8.8
>=dev-python/gst-python-0.8.1
>=dev-python/PyQt-3.14"


src_compile() {
	econf || die
	distutils_src_compile || die
}

src_install() {
	make DESTDIR=${D} install || die
}
