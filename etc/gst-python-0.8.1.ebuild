# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /home/cvsroot/bmg_overlay/dev-python/gst-python/gst-python-0.7.91.ebuild,v 1.2 2004/04/02 22:23:53 schick Exp $

inherit python debug

DESCRIPTION="A Python Interface to GStreamer"
HOMEPAGE="http://gstreamer.freedesktop.org"
SRC_URI="http://gstreamer.freedesktop.org/src/${PN}/${P}.tar.gz"
LICENSE="LGPL-2"
SLOT="0"
KEYWORDS="~x86"
IUSE=""

RDEPEND=">=dev-python/pygtk-1.99.4
		>=dev-libs/glib-2
		>=x11-libs/gtk+-2
		>=media-libs/gst-plugins-0.8
		>=dev-lang/python-2.2"

DEPEND="${RDEPEND}
		dev-util/pkgconfig"

S=${WORKDIR}/${P}

src_compile() {
	
	### Docs didn't work for me - Matt
	myconf="--disable-docs"

	econf ${myconf} || die
	emake || die
}

src_install() {

	einstall || die
	dodoc AUTHORS COPYING ChangeLog INSTALL NEWS README TODO
	docinto examples
	cp -a examples/* ${D}usr/share/doc/${PF}/examples
	prepalldocs
		 
}

pkg_postinst() {
	python_version
	python_mod_optimize ${ROOT}usr/lib/python${PYVER}/site-packages/gst
}
																		
pkg_postrm() {
	python_version
	python_mod_cleanup ${ROOT}usr/lib/python${PYVER}/site-packages/gst
}

