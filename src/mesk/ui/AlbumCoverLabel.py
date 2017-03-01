#!/usr/bin/env python
################################################################################
#  Copyright (C) 2004  Travis Shirk <travis@pobox.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#
#  $Id: AlbumCoverLabel.py,v 1.1 2004/12/20 07:01:38 travis Exp $
################################################################################
from qt import *;

class AlbumCoverLabel(QLabel):
    def __init__(self, parent = None, name = None, flags = 0):
        QLabel.__init__(self, parent, name, flags);
        self.setMinimumSize(QSize(64,64))
        self.setMaximumSize(QSize(64,64))
        self.setFrameShape(QLabel.NoFrame)
        self.setScaledContents(1)
        self.setFocusPolicy(QWidget.ClickFocus);

        self._default_pixmap = QPixmap();
        self._default_pixmap.loadFromData(blank_image_data);
        self.setPixmap(self._default_pixmap);

    def setPixmap(self, pm):
        if not pm:
            pm = self._default_pixmap;
        QLabel.setPixmap(self, pm);

    def mouseDoubleClickEvent(self, mouse_event):
        # TODO: Album presentation; the ability to view/select alternate covers
        print "AlbumCoverLabel double clicked"

blank_image_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x01\x00\x00\x00\x01" \
    "\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00" \
    "\x0d\x49\x44\x41\x54\x08\x99\x63\x60\x60\x60\x60" \
    "\x00\x00\x00\x05\x00\x01\x87\xa1\x4e\xd4\x00\x00" \
    "\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82";
