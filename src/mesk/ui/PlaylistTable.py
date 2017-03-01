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
#  $Id: PlaylistTable.py,v 1.10 2004/12/28 02:27:56 travis Exp $
################################################################################
import sys, os;
from qt import *;
from qttable import *;

class PlaylistTable(QTable):
    # Supported mime types
    MIME_TYPE_URI_LIST = "text/uri-list";
    MIME_TYPE_MOZ_URL  = "text/x-moz-url";

    STATUS_COL = 0;
    TITLE_COL  = 1;
    ARTIST_COL = 2;
    ALBUM_COL  = 3;
    TIME_COL   = 4;

    RESIZABLE_SECTIONS = [TITLE_COL, ALBUM_COL, ARTIST_COL];

    def __init__(self, parent = None, name = None):
        QTable.__init__(self, parent, name);

        table_font = QFont(self.font());
        table_font.setFamily("Bitstream Vera Sans");
        table_font.setPointSize(10);
        self.setFont(table_font);

        self.setShowGrid(0);
        self.setReadOnly(True);
        self.setFrameShape(QTable.Panel)
        self.setFrameShadow(QTable.Raised)
        self.setRowMovingEnabled(True);
        self.setSelectionMode(QTable.MultiRow);
        self.setFocusStyle(QTable.FollowStyle);

        self.viewport().setAcceptDrops(True);
        self.setDragAutoScroll(True);

        # Set up columns, there are no rows until the playlist is set.
        self.setNumRows(0);
        self.setNumCols(5);
        header = self.horizontalHeader();
        header.setLabel(self.STATUS_COL, "");
        header.setResizeEnabled(False, self.STATUS_COL);
        header.setLabel(self.TITLE_COL, "Title");
        header.setResizeEnabled(False, self.TITLE_COL);
        header.setLabel(self.ARTIST_COL, "Artist");
        header.setResizeEnabled(False, self.ARTIST_COL);
        header.setLabel(self.ALBUM_COL, "Album");
        header.setResizeEnabled(False, self.ALBUM_COL);
        header.setLabel(self.TIME_COL, "Time");
        header.setResizeEnabled(False, self.TIME_COL);
        # XXX: Support for sizing headers works "just okay".  Resizing is
        # disabled above so this slot is not called.
        self.connect(header, SIGNAL("sizeChange(int,int,int)"),
                     self._headerSizeChanged);

        # Used to control what sections to resize when the header changes size
        self._resizable_sections = [];
        self._last_resized_section = None;

    def isDragAccepted(self, event):
        return event.provides(self.MIME_TYPE_URI_LIST) or\
               event.provides(self.MIME_TYPE_MOZ_URL);
    def contentsDragEnterEvent(self, event):
        accept = self.isDragAccepted(event);
        event.accept(accept);
        if accept:
            self._last_drag_row = None;
            self.clearSelection(True);
        # XXX: Debugging
        #print "========="
        #i = 0;
        #mt = event.format(i);
        #while mt:
        #    print "%s:\n%s" % (mt, event.encodedData(mt));
        #    i += 1;
        #    mt = event.format(i);

    def contentsDragMoveEvent(self, event):
        row = self.rowAt(event.pos().y());
        if row != self._last_drag_row:
            self.clearSelection(True);
            self.selectRow(row);
        self._last_drag_row = row;

    def contentsDropEvent(self, event):
        if event.provides(self.MIME_TYPE_MOZ_URL):
            data = str(event.encodedData(self.MIME_TYPE_MOZ_URL));
            if data:
                (url, title) = data.split("\n");
                # TODO
                print "URL:\n%s - %s" % (title, url);
        elif event.provides(self.MIME_TYPE_URI_LIST):
            files = QStringList();
            QUriDrag.decodeLocalFiles(event, files);
            if files:
                # Convert any directories to files
                for f in files:
                    if os.path.isdir(unicode(f)):
                        files.remove(f);
                        for (root, dirs, filez) in os.walk(unicode(f)):
                            for new_file in filez:
                                files.append(QString(root + os.sep + new_file));

                pos = event.pos();
                if pos.isNull() or pos.y() > self.rowPos(self.numRows() - 1):
                    # Append contents
                    insert_row = self.numRows();
                else:
                    # Insert contents
                    y = pos.y();
                    insert_row = self.rowAt(y);
                    if insert_row < 0:
                        insert_row = 0;
                files.sort();
                self.emit(PYSIGNAL("filesAdded(file_list,int)"), (files,
                                                                  insert_row));
        else:
            # We should never get here
            assert(False);
            return;
    def externalDropEvent(self, event, row):
        # Seeting a null point tells contentsDropEvent to append. 
        event.setPoint(QPoint(self.columnPos(row), self.rowPos(row)));
        self.contentsDropEvent(event);


    def keyReleaseEvent(self, key_event):
        if key_event.key() == Qt.Key_Delete:
            selected_rows = self.getSelectedRows();
            selected_rows.sort();
            if not selected_rows:
                return;
            self.clearSelection(True);
            key_event.accept();
            self.emit(PYSIGNAL("entriesDeleted(index_list)"), (selected_rows,));
        elif key_event.state() == Qt.ControlButton and\
             key_event.key() == Qt.Key_A:
            if self.numRows():
                self.clearSelection(True);
                selection = QTableSelection();
                selection.init(0, 0);
                selection.expandTo(self.numRows() - 1, self.numCols() - 1);
                self.addSelection(selection);
        else:
            key_event.ignore();

    def getSelectedRows(self):
        i = 0;
        rows = [];
        while i < self.numSelections():
            table_selection = self.selection(i);
            rng = range(table_selection.topRow(),
                         table_selection.bottomRow() + 1);
            for r in rng:
                rows.append(r);
            i += 1;
        rows.sort();
        return rows;

    def show(self):
        QTable.show(self);
    def resizeHeader(self):
        num_rows = self.numRows();
        if not num_rows:
            return;
        header = self.horizontalHeader();
        table_width = self.width() -\
                      self.verticalHeader().sectionSize(num_rows - 1);
        header_width = header.headerWidth();
        # Compute the space in which the header needs to fit.
        usable_space = table_width - header.sectionSize(self.STATUS_COL) -\
                       header.sectionSize(self.TIME_COL);
        scroll_bar = self.verticalScrollBar();
        if scroll_bar:
            usable_space -= scroll_bar.frameSize().width();
        # Fudge
        usable_space -= 15;

        title_secion_sz   = int(usable_space * 0.40);
        header.resizeSection(self.TITLE_COL, title_secion_sz);
        album_section_sz  = int(usable_space * 0.35);
        header.resizeSection(self.ALBUM_COL, album_section_sz);
        artist_section_sz = int(usable_space * 0.25);
        header.resizeSection(self.ARTIST_COL, artist_section_sz);

        header.update();
        self.updateContents();

    def _headerSizeChanged(self, section, old, new):
        print "header section %d size changed %d -> %d" % (section, old, new);
        if not self._resizable_sections or\
           section != self._last_resized_section:
            self._last_resized_section = section;
            self._resizable_sections = list(self.RESIZABLE_SECTIONS);
            print self._resizable_sections;
            print section;
            self._resizable_sections.remove(section);
        header = self.horizontalHeader();
        difference = (new - old) * -1;
        resize_section = self._resizable_sections.pop();
        header.resizeSection(resize_section,
                             header.sectionSize(resize_section) + difference);
