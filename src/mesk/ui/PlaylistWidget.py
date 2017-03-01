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
#  $Id: PlaylistWidget.py,v 1.33 2004/12/28 05:31:20 travis Exp $
################################################################################
import sys, datetime;
from qt import *;
from qttable import *;
from PlaylistWidgetBase import PlaylistWidgetBase;
import mesk.database;
from mesk.utils import formatSize;
from mesk.utils import formatTrackTime;
from mesk.utils import formatTimeDelta;

# A playlist UI
#
# Signals emmitted by this class.
# entriesDeleted(index_list)
#   Emitted when enties are deleted from the playlist.
#   The argument is a list of the removed integer indices.
# filesAdded(file_list,int)
#   Emitted when files are added to the playlist.
#   The arguments are a list of the added files, and the 
#   position in the list where the tracks should be inserted.
class PlaylistWidget(PlaylistWidgetBase):
    _currently_playing_row = None;

    def __init__(self, parent = None, name = None):
        PlaylistWidgetBase.__init__(self, parent, name);

        # Popup Menu for the playlist.
        self.context_menu = PlaylistMenu(self);

        # Pass thru signals.
        self.connect(self.pl_table, PYSIGNAL("filesAdded(file_list,int)"),
                     PYSIGNAL("filesAdded(file_list,int)"));
        self.connect(self.pl_table, PYSIGNAL("entriesDeleted(index_list)"),
                     PYSIGNAL("entriesDeleted(index_list)"));
        # Most drops are handled in PlaylistTable, but we'll accept them
        # for prepending and appending to the playlist.
        self.setAcceptDrops(True);

        # Stats for pl_stats_label
        self.track_total = long(0);
        self.time_total  = long(0);
        self.size_total  = long(0);

    def show(self):
        PlaylistWidgetBase.show(self);
        self.pl_table.resizeHeader();

    def remove(self, row):
        cx = self.pl_table.contentsX();
        cy = self.pl_table.contentsY();
        self.pl_table.removeRow(row);
        # QScrollView always moves to and selects the end of the playlist;
        # undo that.
        self.pl_table.clearSelection(True);
        self.pl_table.ensureVisible(cx, cy);

        if row < self._currently_playing_row:
            self._currently_playing_row -= 1;
        track = self._playlist[row];
        self.track_total += 1;
        self.time_total  += track.time;
        self.size_total  += track.file_size;
        self.updatePlaylistStats();

    def insert(self, row, track):
        assert(track);
        self.pl_table.insertRows(row, 1);
        self.pl_table.setItem(row, self.pl_table.STATUS_COL,
                              PlaylistStatusItem(self.pl_table));
        self.pl_table.setItem(row, self.pl_table.TITLE_COL,
                              PlaylistItem(self.pl_table, QString(track.name)));
        artist = self._playlist.getArtist(track.artist_id).name;
        self.pl_table.setItem(row, self.pl_table.ARTIST_COL,
                              PlaylistItem(self.pl_table, QString(artist)));
        album = self._playlist.getAlbum(track.album_id).name;
        self.pl_table.setItem(row, self.pl_table.ALBUM_COL,
                              PlaylistItem(self.pl_table, QString(album)));
        time_str = formatTrackTime(track.time);
        self.pl_table.setItem(row, self.pl_table.TIME_COL,
                              PlaylistItem(self.pl_table, QString(time_str)));
        self.pl_table.clearSelection(True);

        if row <= self._currently_playing_row:
            self._currently_playing_row += 1;
        self.track_total += 1;
        self.time_total  += track.time;
        self.size_total  += track.file_size;
        self.updatePlaylistStats();

    def setList(self, pl):
        assert(pl != None and isinstance(pl, mesk.database.Playlist));

        # Clear current list.
        self.pl_table.setNumRows(0);
        self.pl_table.update();

        self._playlist = pl;
        # Stats for pl_stats_label
        self.track_total = 0;
        self.time_total = long(0);
        self.size_total = long(0);

        row = 0;
        for t in self._playlist:
            self.insert(row, t);
            row += 1;

        horiz_header = self.pl_table.horizontalHeader();
        self.pl_table.adjustColumn(self.pl_table.STATUS_COL);
        self.pl_table.adjustColumn(self.pl_table.TIME_COL);

        # Update state
        self.setPlayingRow(self._playlist.getCurrentIndex());
        self.pl_table.update();
        self.updatePlaylistStats();

    def updatePlaylistStats(self, num_tracks = None, size_bytes = None,
                            time_secs = None):
        nt = num_tracks;
        sb = size_bytes;
        ts = time_secs;
        if nt == None or sb == None or ts == None:
            if nt == None:
                num_tracks = long(0);
            if sb == None:
                size_bytes = long(0);
            if ts == None:
                time_secs = long(0);
            for t in self._playlist:
                if nt == None:
                    num_tracks += 1;
                if sb == None:
                    size_bytes += t.file_size;
                if ts == None:
                    time_secs += t.time;
        delta = datetime.timedelta(seconds = time_secs);
        self.pl_stats_label.setText("%d tracks [%s] - %s" %\
                                    (num_tracks, formatSize(size_bytes),
                                     formatTimeDelta(delta)));
        self.pl_stats_label.adjustSize();

    def setPlayingRow(self, row_index, scroll = True):
        # Clear previously playing row
        if self.pl_table.numRows() == 0:
            self._currently_playing_row = None;
            return;
        if self._currently_playing_row != None:
            for col in range(0, self.pl_table.numCols()):
                table_item = self.pl_table.item(self._currently_playing_row,
                                                col);
                table_item.setPlaying(False);
                self.pl_table.updateCell(self._currently_playing_row, col);

        if row_index == None:
            return;

        # Mark the playing row.
        for col in range(0, self.pl_table.numCols()):
            table_item = self.pl_table.item(row_index, col);
            table_item.setPlaying(True);
            self.pl_table.updateCell(row_index, col);
        self.pl_table.adjustColumn(self.pl_table.STATUS_COL);
        # Update state
        self._currently_playing_row = row_index;
        # Update play queue numbering
        self._updateQueueValues();
        if scroll:
            self.setVisibleRow(row_index);

    # Handle upstream key events.  This is a method of QWidget and has no
    # corresponding signal connection.
    def keyReleaseEvent(self, key_event):
        key = key_event.ascii();
        # Handle 'q' on the playlist for queuing up tracks.
        if key == ord('q') or key == ord('u'):
            self._handleQueueKeyEvents(key);
            key_event.accept();
        elif key == ord('j'):
            self.setVisibleRow(self._currently_playing_row);
            key_event.accept();
        else:
            key_event.ignore();

    def setVisibleRow(self, row):
        if row != None:
            self.pl_table.ensureCellVisible(row, self.pl_table.STATUS_COL);

    def contextMenuEvent(self, ctx_menu_event):
        print "contextMenuEvent in PlaylistWidgetBase"
        self.context_menu.popup(ctx_menu_event.globalPos());

    def _handleQueueKeyEvents(self, key_int):
        assert(key_int == ord('q') or key_int == ord('u'));
        selected_rows = self.pl_table.getSelectedRows();
        if not selected_rows:
            return;

        if key_int == ord('q'):
            self._playlist.enqueue(selected_rows);
        elif key_int == ord('u'):
            self._playlist.dequeue(selected_rows);
        self._updateQueueValues();
    
    def _updateQueueValues(self):
        queue = self._playlist.getQueue();
        queue_index = 1;
        # Process each row since we don't know the previous queue state
        rows = range(0, len(self._playlist));
        for q in queue:
            status_item = self.pl_table.item(q, self.pl_table.STATUS_COL);
            status_item.setQueueValue(queue_index);
            self.pl_table.updateCell(q, self.pl_table.STATUS_COL);
            rows.remove(q);
            queue_index += 1;
        self.pl_table.adjustColumn(self.pl_table.STATUS_COL);
        for r in rows:
            status_item = self.pl_table.item(r, self.pl_table.STATUS_COL);
            if status_item:
                status_item.setQueueValue(None);
                self.pl_table.updateCell(r, self.pl_table.STATUS_COL);

        self.pl_table.adjustColumn(self.pl_table.STATUS_COL);
        self.pl_table.resizeHeader()

    def dragEnterEvent(self, event):
        event.accept(self.pl_table.isDragAccepted(event));
    def dropEvent(self, event):
        # Dropped above or below?
        if event.pos().y() > self.pl_table.height():
            insert_row = 0;
        else:
            insert_row = self.pl_table.numRows();
        self.pl_table.externalDropEvent(event, insert_row);

    def resizeEvent(self, resise_event):
        self.pl_table.resizeHeader();

class PlaylistItem(QTableItem):
    ELLIPSES = "...";

    def __init__(self, table, text, truncate_text = True):
        QTableItem.__init__(self, table, QTableItem.Never, text);
        self.setReplaceable(False);
        self._is_playing = False;
        self._truncate_txt = truncate_text;
        self.setText(text);

    def setText(self, qstr):
        if qstr == None:
            qtr = QString("");
        QTableItem.setText(self, qstr);
        self._full_text = unicode(qstr);

    def sizeText(self, width, font_metrics):
        # Fudge, becuase it seems to work better
        if self._is_playing:
            width -= 2;
        else:
            width -= 1;

        if not self._truncate_txt or width <= 0:
            return self._full_text;
        elif font_metrics.width(self._full_text) < width:
            return self._full_text;

        # Only chopping one character at a time.  I don't see a quick way
        # to determine mono-spaced fonts, but if one is used chopping 3 at a
        # time would be more efficient.
        text = self._full_text[:-1] + self.ELLIPSES + " ";
        while font_metrics.width(text) > width:
            # 1 char + 3 ... + 1 whitespace
            text = text[:-5] + self.ELLIPSES + " ";
        return text;

    def paint(self, painter, color_group, rect, selected):
        font = painter.font();
        if self._is_playing:
            font.setWeight(QFont.DemiBold);
        else:
            font.setWeight(QFont.Normal);
        painter.setFont(font);
        # Make sure to call the base class implementation.
        QTableItem.setText(self,
                           self.sizeText(self.table().columnWidth(self.col()),
                           painter.fontMetrics()));
        QTableItem.paint(self, painter, color_group, rect, selected);

    def setPlaying(self, b):
        self._is_playing = b;

# Create the pixmap that will be used to mark currently playing track
playing_pixmap = None;
class PlaylistStatusItem(PlaylistItem):
    def __init__(self, table):
        PlaylistItem.__init__(self, table, QString(""), False);
        global playing_pixmap;
        if not playing_pixmap:
            playing_pixmap = QPixmap();
            playing_pixmap.loadFromData(play_image_data, "PNG");
        self._queue_value = None;

    def setPlaying(self, b):
        if self._is_playing and not b:
            self.setPixmap(QPixmap());
        elif not self._is_playing and b:
            self.setText("");
            self.setPixmap(playing_pixmap);
        PlaylistItem.setPlaying(self, b);

    def setQueueValue(self, i):
        if not i:
            self.setText(QString(""));
        else:
            self.setText(QString("[%d]" % i));

    def paint(self, painter, color_group, rect, selected):
        PlaylistItem.paint(self, painter, color_group, rect, selected);

class PlaylistMenu(QPopupMenu):
    def __init__(self, parent = None, name = ""):
        QPopupMenu.__init__(self, parent, name);


play_image_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x18\x00\x00\x00\x18" \
    "\x08\x06\x00\x00\x00\xe0\x77\x3d\xf8\x00\x00\x00" \
    "\xfd\x49\x44\x41\x54\x48\x89\xed\xd2\x41\x2e\x43" \
    "\x51\x14\xc6\xf1\xff\x73\xce\xed\xe3\xde\x97\x97" \
    "\xd6\xa0\x6c\xa0\x42\x50\xf4\x99\x10\x7b\xb0\x0c" \
    "\x09\x06\x98\x62\x09\xc2\x16\x24\xac\x43\xc2\xb4" \
    "\xfb\xb0\x8c\x63\x20\x1d\xb6\x3d\xf7\xa5\x9d\xf5" \
    "\x1b\x9f\x7c\xbf\x73\x92\x03\xab\xcc\x89\x38\x66" \
    "\x2e\x81\x0a\xf8\x6d\x03\xac\x39\x66\xb6\x81\x31" \
    "\xd0\x2c\x0b\x98\xa4\x15\xe2\x06\x1e\xee\xef\x5a" \
    "\x21\x6e\x60\x23\x46\x6e\x6f\xae\xb3\x11\x37\xa0" \
    "\x22\x1c\x0e\x0f\x78\x7e\x7a\xcc\x42\xdc\x80\x88" \
    "\xa0\xa2\x34\xcd\x09\x6f\xaf\x2f\x6e\xc4\x7f\x81" \
    "\x0a\xaa\x8a\x6a\x60\x67\x30\xe0\xf3\xe3\xdd\x85" \
    "\xe4\x5d\xa0\x42\x50\x41\x83\xb2\xd5\xef\xf3\xf3" \
    "\xfd\x05\x30\x36\x33\x9b\xba\x58\x1e\xa0\x68\x08" \
    "\xac\x97\x25\x29\x55\x1c\x8f\x4e\x31\x33\x8a\xa2" \
    "\x28\x16\x02\x54\xa9\x22\xc6\x48\x4a\x89\xe1\xd1" \
    "\x68\x6e\x79\x16\x50\xd7\x35\x2a\x42\xaf\xb7\xc9" \
    "\xee\xde\xbe\xab\x1c\x32\xdf\xb4\xee\x76\xb3\xca" \
    "\xb3\x80\x4e\xd9\xe1\xec\xfc\x22\xab\xdc\x9b\x2b" \
    "\xc0\x00\x9b\xf5\x2d\xd3\xe2\xb9\x20\xf1\xdf\xbe" \
    "\xf0\xcd\x27\x69\xda\x6c\xee\xce\x32\xbb\x57\x01" \
    "\xe0\x0f\x2e\xfa\x3d\x63\x47\x25\x88\x6e\x00\x00" \
    "\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"
