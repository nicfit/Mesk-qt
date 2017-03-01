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
#  $Id: PlaylistWidget.py,v 1.11 2004/12/03 07:24:18 travis Exp $
################################################################################
from qt import *;
from BrowserWidgetBase import BrowserWidgetBase;

class BrowserWidget(BrowserWidgetBase):
    ARTISTS_ITEM = 0;
    ARTISTS      = "Artists";
    ALBUMS_ITEM  = 1;
    ALBUMS       = "Albums";
    GENRES_ITEM  = 2;
    GENRES       = "Genres";

    def __init__(self, parent = None, name = None, fl = 0):
        BrowserWidgetBase.__init__(self, parent, name, fl);
        self.connect(self.browse_select_combobox, SIGNAL("activated(int)"),
                     self._browseSelectComboActivated);
        self.browse_select_combobox.insertItem(self.ARTISTS);
        self.browse_select_combobox.insertItem(self.ALBUMS);
        self.browse_select_combobox.insertItem(self.GENRES);

        self._archive = None;
        self._artists = [];
        self._albums  = [];
        self._genres  = [];

    def setArchive(self, archive):
        assert(archive);
        self._archive = archive;
        self._display(self.browse_select_combobox.currentItem());

    def _browseSelectComboActivated(self, index):
        self._display(index);

    def _updateList(self, which):
        db = self._archive.getDatabase();
        db.connect();
        if which == self.ARTISTS_ITEM or which == self.ARTISTS:
            self._artists = db.getArtists();
        elif which == self.ALBUMS_ITEM or which == self.ALBUMS:
            self._albums = db.getAlbums();
        elif which == self.GENRES_ITEM or which == self.GENRES:
            # FIXME
            self._genres = db.getArtists();
        else:
            assert(0);
        db.disconnect();

    def _display(self, which):
        while self.browse_listbox.count():
            self.browse_listbox.removeItem(0);
        if which == self.ARTISTS_ITEM:
            if not self._artists:
                self._updateList(self.ARTISTS_ITEM);
            self.browse_select_combobox.setCurrentItem(self.ARTISTS_ITEM);
            for a in self._artists:
                self.browse_listbox.insertItem(QString(a.name));
        elif which == self.ALBUMS_ITEM:
            if not self._albums:
                self._updateList(self.ALBUMS_ITEM);
            self.browse_select_combobox.setCurrentItem(self.ALBUMS_ITEM);
            for a in self._albums:
                self.browse_listbox.insertItem(QString(a.name));
        elif which == self.GENRES_ITEM:
            # FIXME
            if not self._artists:
                self._updateList(self.ARTISTS_ITEM);
            self.browse_select_combobox.setCurrentItem(self.ARTISTS_ITEM);
            for a in self._artists:
                self.browse_listbox.insertItem(QString(a.name));
            pass;
        else:
            assert(0);
