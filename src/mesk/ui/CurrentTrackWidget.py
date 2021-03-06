# -*- coding: utf-8 -*-
################################################################################
#  Copyright (C) 2005  Travis Shirk <travis@pobox.com>
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
#  $Id$
################################################################################
from mesk.externalsearch import *;
from qt import *;
from CurrentTrackWidgetBase import CurrentTrackWidgetBase;


class CurrentTrackWidget(CurrentTrackWidgetBase):
    TITLE_ARTIST_LABLE_FORMAT =\
        "<p align='left'><nobr><b>%(title)s</b></nobr><br/>"\
        "<nobr><i>%(artist)s</i></nobr><br/>"\
        "</p>";
    ALBUM_LABEL_FORMAT = "<nobr><i>%(album)s</i></nobr>";
    
    def __init__(self, parent = None, name = None, fl = 0):
        CurrentTrackWidgetBase.__init__(self, parent, name, fl);

        # Cover label properties
        self.cover_label.setMinimumSize(QSize(64,64))
        self.cover_label.setMaximumSize(QSize(64,64))
        self.cover_label.setFrameShape(QLabel.NoFrame)
        self.cover_label.setScaledContents(1)
        self.cover_label.setFocusPolicy(QWidget.ClickFocus);
        self._default_pixmap = QPixmap();
        #self._default_pixmap.loadFromData(blank_image_data);
        self._default_pixmap.loadFromData(na_image_data);

        self.album_into_tt = AlbumInfoToolTip(self);

        self._last_album = None;
        self._external_search = None;
        self.clear();

    def setAlbumCoversEnabled(self, external_search):
        self._external_search = external_search;

    def clear(self):
        self.cover_label.setFrameShape(QLabel.Box)
        self.cover_label.setPixmap(self._default_pixmap);
        self.title_artist_label.setText(QString(""));
        self.title_artist_label.adjustSize();
        self.album_label.setText(QString(""));
        self.album_label.adjustSize();

    def display(self, artist, album, track):
        if track == None:
            self.clear();
            return;

        assert(artist and album);
        text = unicode(self.TITLE_ARTIST_LABLE_FORMAT %\
                       {"title": track.name, "artist": artist.name});
        self.title_artist_label.setText(QString(text));
        self.title_artist_label.adjustSize();
        text = unicode(self.ALBUM_LABEL_FORMAT % {"album": album.name});
        self.album_label.setText(QString(text));
        self.album_label.adjustSize();

        if self._last_album and album.id != self._last_album.id:
            self.cover_label.setFrameShape(QLabel.Box)
            self.cover_label.setPixmap(self._default_pixmap);

        self._last_album = album;


class AlbumInfoToolTip(QToolTip):
    def __init__(self, widget, tt_grp = None):
        QToolTip.__init__(self, widget, tt_grp);

    def maybeTip(self, pos):
        self.tip(self.parentWidget().rect(), "Year: 2005");

blank_image_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x01\x00\x00\x00\x01" \
    "\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00" \
    "\x0d\x49\x44\x41\x54\x08\x99\x63\x60\x60\x60\x60" \
    "\x00\x00\x00\x05\x00\x01\x87\xa1\x4e\xd4\x00\x00" \
    "\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82";

na_image_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x40\x00\x00\x00\x40" \
    "\x08\x06\x00\x00\x00\xaa\x69\x71\xde\x00\x00\x03" \
    "\x13\x49\x44\x41\x54\x78\x9c\xed\x98\x4b\x6c\x4c" \
    "\x61\x14\xc7\x7f\xd4\xa3\x09\x91\xb0\x50\x8a\x7a" \
    "\x54\x2b\x88\xb7\x10\x29\xb5\x21\x22\x51\x89\x20" \
    "\x21\xb1\xb0\xb1\x11\x1b\x89\x47\x62\xd5\x5d\x37" \
    "\x62\x25\x8d\x58\x88\x84\x88\x85\x06\xa9\x45\x25" \
    "\x8a\x44\xa2\x41\x5a\x8d\xc6\x23\x54\x6c\x90\x4a" \
    "\xa9\x57\x1f\xb4\x74\x2c\xbe\xff\x97\xf9\x66\x32" \
    "\xd3\xb9\xc3\x4c\xbb\x70\x7e\xc9\xcd\x99\xff\x77" \
    "\xcf\x39\xf7\xdc\x6f\xbe\xfb\x38\x17\x0c\xc3\x30" \
    "\x0c\xc3\x30\x0c\xc3\x30\x0c\xc3\x30\x0c\xc3\x30" \
    "\x0c\x63\xa4\x28\x00\xde\x03\x31\x60\xcd\x08\xd7" \
    "\x92\x35\x53\x70\x85\xf7\x03\xe7\x81\x4f\xc0\x77" \
    "\xa0\x3a\xf0\x29\x07\xae\x01\xdf\x80\x6e\xa0\x0e" \
    "\x98\xaa\x7d\xdb\x15\x1f\x6e\x3f\x81\x89\x79\xaf" \
    "\x3c\x47\xac\xc5\x15\x3d\x08\x6c\x02\x2a\xa5\x7b" \
    "\xb5\x7f\x0e\xf0\x11\x68\x03\x66\x00\x3b\xb5\xbf" \
    "\x3e\xc8\x71\x54\x63\x2d\xc3\x52\x71\x8e\xd9\x87" \
    "\x2b\xfe\x8e\xf4\x32\xe9\x17\xd2\x17\xa5\xab\xa4" \
    "\xc7\x4a\xf7\x05\x39\xce\x68\xec\x6c\xbe\x8b\xf5" \
    "\x8c\xce\x61\xae\xf9\xb2\x4d\xb2\x2b\x64\x1f\xcb" \
    "\x6e\x95\xbd\x27\xeb\x97\x76\x4f\x90\xa3\x54\xb6" \
    "\x39\x87\x75\x0d\x49\x2e\x27\xa0\x4c\xf6\xa5\xec" \
    "\x72\xd9\x56\xd9\x09\xb2\xfe\x84\x37\xc8\x36\x04" \
    "\x39\x86\x7d\x02\x72\xc9\x03\xdc\xf2\xad\x90\xbe" \
    "\x2b\xbd\x45\xfa\x86\xf4\x2e\xa0\x18\x78\x02\x74" \
    "\xe2\xee\x0d\x9e\x7e\xf9\x2c\xc8\x7b\xb5\x79\xa0" \
    "\x0b\x57\xbc\xbf\xab\x7f\x96\x2e\x92\x2e\xc2\x3d" \
    "\x01\x7a\x80\xaf\xc0\x55\xe2\xab\xc6\x73\x12\xf7" \
    "\xe4\x88\x01\xaf\xf2\x5c\xaf\x61\x18\x86\x31\x12" \
    "\xf8\xf7\x7c\x70\x8f\xc3\x18\xf0\x05\x18\x15\x21" \
    "\x36\x8a\x7f\x56\x39\x73\xf9\x22\xf4\x37\xac\x92" \
    "\x6d\x21\x3e\x29\xff\xea\x9f\x55\xce\x31\x11\x0e" \
    "\x9a\x6b\xc2\x7f\xc5\x17\x1b\xf5\xcd\x2f\x8a\x7f" \
    "\x56\x39\x93\x57\xc0\x61\x12\x5b\xd1\x66\x60\x7d" \
    "\xb0\xff\x83\xf6\x95\x48\xd7\x48\x37\x46\x88\xf7" \
    "\xed\x72\xf7\x10\xc5\x66\x3a\xbe\xf7\x2f\x03\x9e" \
    "\xe1\xde\x1c\xdb\x70\x8d\x57\xba\x9c\x25\xc0\x05" \
    "\x5c\x27\xfa\x03\xb8\x09\xcc\x24\x0d\xc7\x80\xd5" \
    "\xc0\x78\x5c\x4b\x1b\x03\x5e\x07\xfb\x6f\x69\x6c" \
    "\x1b\x30\x0d\xf7\x56\x17\xc3\xb5\xc2\x99\xe2\x7d" \
    "\xbb\xdc\x1a\xe4\xf3\x1f\x3f\xca\x22\xc4\x87\xfe" \
    "\x4d\x3a\xfe\x6e\xe9\x87\x69\x72\x4e\x07\xde\x69" \
    "\x2b\x05\x76\x90\xf8\x87\x0d\x49\x01\x6e\x86\x07" \
    "\x82\xb1\x53\x4a\x70\x02\x38\xad\xdf\xd7\x23\xc6" \
    "\xfb\x76\xf9\x8a\x74\xa6\x9b\x55\x72\xbc\xf7\x8f" \
    "\x01\x8b\x35\x36\x8e\xf8\x47\x98\x54\x39\xcf\x49" \
    "\x1f\x49\xe3\x9f\xc0\x6c\xe0\x12\xd0\x01\xfc\x0e" \
    "\x0e\xd6\x1e\xf8\xec\xd7\xd8\x7d\xdc\x12\x1d\x04" \
    "\x96\x44\x8c\xaf\x96\xae\x91\xae\x92\xbe\x1d\x31" \
    "\xde\xfb\x3f\x0a\xea\x99\xac\xb1\x8e\x34\x39\x3b" \
    "\x83\x3c\xe1\xe6\x3b\xd6\x84\x7b\x40\x1d\xb0\x17" \
    "\x38\x04\x14\x02\x07\x35\x1e\x7e\x9d\x69\x93\x5d" \
    "\x87\x9b\xcd\xcb\xc1\x58\xa6\x78\xbf\xcc\xfd\x09" \
    "\x25\x5f\xab\x99\xe2\x53\xdd\xdc\x36\xca\x36\xa4" \
    "\xf1\x99\x24\x5b\x88\x5b\x11\x7e\x2b\x27\x05\x7d" \
    "\xb8\xd9\x59\x08\x2c\x02\xde\x48\x1f\x0f\x7c\x0a" \
    "\x81\x5f\x1a\x1f\x20\xfe\x11\x24\x4a\xbc\x6f\x97" \
    "\x2b\xa5\xeb\xa5\xf7\x44\x8c\xf7\xfe\xed\xc0\x5c" \
    "\x60\x16\xf0\x14\xd7\x75\xce\x4b\x93\xb3\x51\xfa" \
    "\x80\x6a\xaf\x00\x6a\x53\x9d\x3c\xb8\xeb\xa4\x8b" \
    "\xf8\xc7\xca\x76\x05\x6f\x4e\xf2\x7b\x4e\xea\xcf" \
    "\x56\x99\xe2\x7d\xbb\x5c\x2c\x9d\x7c\x03\xcc\x14" \
    "\xef\xfd\x6b\x81\xb7\xb8\xeb\xb8\x09\x58\x19\xd4" \
    "\x90\x9c\xb3\x04\xb7\x3a\x7a\x71\x2d\x78\x1d\xb0" \
    "\x34\xdd\x04\x18\x86\x61\x18\x86\x61\x18\x86\x61" \
    "\x18\x86\x61\x18\xc6\x7f\xc0\x1f\x6a\x70\x1b\x18" \
    "\x1c\x40\x12\xd1\x00\x00\x00\x00\x49\x45\x4e\x44" \
    "\xae\x42\x60\x82"
