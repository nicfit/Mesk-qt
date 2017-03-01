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
#  $Id: MainWindow.py,v 1.48 2005/02/05 22:22:27 travis Exp $
################################################################################
import sys, errno, urllib2;
import mesk;
from mesk import *;
from qt import *;
from MainWindowBase import MainWindowBase;
from GstAudioControl import GstAudioControl;
from AboutDialog import AboutDialog;

CURRENTLY_PLAYING_FORMAT = "<p align='left'><nobr><b>%(track)s</b></nobr><br>"\
                           "<nobr>By <i>%(artist)s</i></nobr><br>"\
                           "<nobr><i>%(album)s</i></nobr></p>";

class MainWindow(MainWindowBase):
    BROWSER_TAB  = 0;
    PLAYLIST_TAB = 1;
    STATUS_TIME = 5000;

    def __init__(self, config, archive, parent = None, name = None, flags = 0):
        MainWindowBase.__init__(self, parent, "mesk.ui.MainWindow", flags);
        self.archive = archive;
        self.config = config;
        self.log = mesk.config.app_log;

        # Hook up menu items
        self.connect(self.fileSyncAction, SIGNAL("activated()"), self.fileSync);
        self.connect(self.fileSavePlaylistAction, SIGNAL("activated()"),
                     self.fileSavePlaylist);
        self.connect(self.fileImportPlaylistAction, SIGNAL("activated()"),
                     self.fileImportPlaylist);
        self.connect(self.viewDefaultPlaylistAction, SIGNAL("toggled(bool)"), 
                     self.viewDefaultPlaylistToggle);
        self.connect(self.viewBrowserAction, SIGNAL("toggled(bool)"), 
                     self.viewBrowserToggle);
        self.connect(self.viewStreamsAction, SIGNAL("toggled(bool)"), 
                     self.viewStreamsToggle);

        # Set the current playlist
        db = self.archive.getDatabase();
        db.connect();
        pl = db.getPlaylist(name = u"Playlist");
        self.ui_props = db.getUIProps();
        assert(self.ui_props);
        db.disconnect();
        self.pl = pl;
        self.playlist_widget.setList(pl);
        self.connect(self.playlist_widget.shuffle_checkbox,
                     SIGNAL("toggled(bool)"), self._shuffleToggled);
        self.connect(self.playlist_widget.repeat_checkbox,
                     SIGNAL("toggled(bool)"), self._repeatToggled);
        self.connect(self.playlist_widget,
                     PYSIGNAL("filesAdded(file_list,int)"),
                     self._playlistFilesAdded);
        self.connect(self.playlist_widget,
                     PYSIGNAL("entriesDeleted(index_list)"),
                     self._playlistFilesDeleted);
        self.player_widget.stop_button.setEnabled(False);
        if not self.pl:
            self.player_widget.play_pause_button.setEnabled(False);
            self.player_widget.next_button.setEnabled(False);
            self.player_widget.prev_button.setEnabled(False);

        # Playlist table connections
        self.tab_widget.setTabLabel(self.tab_widget.page(self.PLAYLIST_TAB),
                                    QString(self.pl.getName()));
        self.tab_widget.setCurrentPage(self.PLAYLIST_TAB);
        self.connect(self.playlist_widget.pl_table,
                     SIGNAL("doubleClicked(int, int, int, const QPoint&)"),
                     self._trackSelected);

        # Audio controller
        self.audio_controller = GstAudioControl(self.player_widget, config, pl);
        self.connect(self.audio_controller, PYSIGNAL("audioPlaying(int)"),
                     self._trackPlaying);
        self.connect(self.audio_controller, PYSIGNAL("audioComplete(int)"),
                     self._trackComplete);
        self.connect(self.audio_controller, PYSIGNAL("audioSkipped(int)"),
                     self._trackSkipped);

        # Clear currently playing
        self.currently_playing_label.setText("");
        self.playlist_widget.setPlayingRow(pl.getCurrentIndex());

        # Browser initialization
        self.browser_widget.setArchive(self.archive);

        # Album covers are downloaded asynchronously and cached
        self._last_playing_album = None;
        self.amazon_search = mesk.albumcover.AmazonSearchThread(config);
        self.amazon_search.start();
        self._setAlbumCoverLabel(None);

        self.sync_thread = None;
        self.progress_bar = QProgressBar(100, self);
        self.progress_bar.setCenterIndicator(True);
        self.progress_bar.setMaximumWidth(150);


    def show(self):
        # Restore our state
        if self.ui_props.main_window_pos_x or self.ui_props.main_window_pos_y:
            self.move(self.ui_props.main_window_pos_x,
                      self.ui_props.main_window_pos_y);
        self.resize(self.ui_props.main_window_width,
                    self.ui_props.main_window_height);
        self.playlist_widget.setVisibleRow(self.pl.getCurrentIndex());
        self._updateCurrentlyPlaying(self.pl.getCurrent());

        MainWindowBase.show(self);
        self.playlist_widget.pl_table.resizeHeader();
    
    def _trackPlaying(self, pos):
        self.playlist_widget.setPlayingRow(pos);
        self._updateCurrentlyPlaying(self.pl[pos]);
    def _trackComplete(self, pos):
        self.log.debug("Track complete: %d" % pos);
        db = self.archive.getDatabase();
        # Update play_count and _play_date in database.
        db.connect();
        db.trackPlayed(self.pl[pos].id);
        db.commit();
        db.disconnect();
    def _trackSkipped(self, pos):
        self.log.debug("[FIXME] Track skipped: %d" % pos);
        pass;

    def _trackSelected(self, row, col, button, mouse_pos):
        if not self.pl:
            return;
        self.player_widget.stop();
        self.pl.setNextIndex(row);
        self.audio_controller.setPlaylist(self.pl);
        self.player_widget.play();
        self.player_widget.externalPlayPause(self.player_widget.PAUSE);

    ## Begin slots for Playlist signals ##
    def _shuffleToggled(self, state):
        self.pl.setShuffle(state);
        # Start sequential mode after the current track.
        if not state:
            self.pl.setNextIndex(self.pl.getCurrentIndex() + 1);

    def _repeatToggled(self, state):
        self.pl.setRepeat(state);

    def _playlistFilesAdded(self, file_list, pos):
        self.log.debug("%d Playlist files added at position %d" %\
                       (len(file_list), pos));
        pl_was_empty = False;
        if not self.pl:
            pl_was_empty = True;
            self.player_widget.play_pause_button.setEnabled(True);
            self.player_widget.next_button.setEnabled(True);
            self.player_widget.prev_button.setEnabled(True);

        num_added = 0;
        db = self.archive.getDatabase();
        db.connect();
        # XXX: Sort based on track number
        for f in file_list:
            f = unicode(f);
            if f.find("file://") == 0:
                f = f[len("file://"):];
            path = os.path.realpath(os.path.abspath(f)).strip();
            track = db.getTrack(path = path);
            if not track:
                print "track not in db: %s" % path;
                # TODO: Handle tracks that are not in DB
                continue;
            self.pl.insert(pos, track);
            self.playlist_widget.insert(pos, track);
            pos += 1;
            num_added += 1;
        db.disconnect();

        current = self.pl.getCurrentIndex();
        self.playlist_widget.setPlayingRow(current, False);
        self._updateCurrentlyPlaying(self.pl[current]);

        # Update playlist stats
        self.playlist_widget.updatePlaylistStats();
        if num_added > 1:
            status_str = "items";
        else:
            status_str = "item";
        self.statusBar().message("%d playlist %s added" % (num_added,
                                                           status_str),
                                 self.STATUS_TIME);

    def _playlistFilesDeleted(self, index_list):
        self.log.debug("Playlist files deleted: %s" % str(index_list));
        # If the currently playing track is being deleted playback needs to stop
        current = self.pl.getCurrentIndex();
        current_deleted = False;
        if not self.audio_controller.isStopped() and current in index_list:
            current_deleted = True;
            self.player_widget.stop();

        # Remove tracks from playlist.
        index_list.reverse();
        for i in index_list:
            # The order of these two calls is required.
            self.playlist_widget.remove(i);
            self.pl.remove(i);

        # Current may have changed.
        current = self.pl.getCurrentIndex();
        self.playlist_widget.setPlayingRow(current, False);
        if current_deleted:
            self.pl.setNextIndex(current);
            self.audio_controller.setPlaylist(self.pl);
            if self.pl:
                self._updateCurrentlyPlaying(self.pl[current]);
                self.audio_controller.play();

        if not self.pl:
            self.player_widget.play_pause_button.setEnabled(False);
            self.player_widget.stop_button.setEnabled(False);
            self.player_widget.next_button.setEnabled(False);
            self.player_widget.prev_button.setEnabled(False);
            self._updateCurrentlyPlaying(None);

        # Update status
        self.playlist_widget.updatePlaylistStats();
        n = len(index_list);
        if n > 1:
            status_str = "items";
        else:
            status_str = "item";
        self.statusBar().message("%d playlist %s deleted" % (n, status_str),
                                 self.STATUS_TIME);
    ## End slots for Playlist signals ##


    def _updateCurrentlyPlaying(self, track):
        if track == None:
            self._updateAlbumCover(None, None);
            self._last_playing_album = None;
            self.currently_playing_label.setText(QString(""));
            self.currently_playing_label.adjustSize();
        else:
            artist = self.pl.getArtist(track.artist_id);
            album = self.pl.getAlbum(track.album_id);
            self._updateAlbumCover(artist, album);
            text = unicode(CURRENTLY_PLAYING_FORMAT %\
                           {"artist": artist.name,
                            "album": album.name,
                            "track": track.name});
            self.currently_playing_label.setText(QString(text));
            self.currently_playing_label.adjustSize();
            self._last_playing_album = album;

    def _updateAlbumCover(self, artist, album):
        if self._last_playing_album and\
           self._last_playing_album.id == album.id:
            # No update necessary
            return;
        self._setAlbumCoverLabel(None);
        self._setAlbumCoverLabel(album, artist);

    def _setAlbumCoverLabel(self, album, artist = None):
        pm = QPixmap();
        if not album:
            pm = None;
        elif album.small_cover:
            self.log.debug("Loading album cover from disk: %s" %\
                           album.small_cover);
            pm.load(album.small_cover);
            if pm.isNull() and artist:
                self.log.debug("Searching for album cover for '%s'" %\
                               album.name);
                self.amazon_search.search(artist, album,
                                          self._albumCoverSearchCB, None);
                return;
        else:
            self.log.debug("Searching for album cover for '%s'" %\
                           album.name);
            self.amazon_search.search(artist, album,
                                      self._albumCoverSearchCB, None);
            return;
        self.current_album_pixmap = pm;
        # The following need to occur on the Qt thread.
        QTimer.singleShot(0, self.__setAlbumCoverPixmap);
    def __setAlbumCoverPixmap(self):
        self.album_label.setPixmap(self.current_album_pixmap);

    def _albumCoverSearchCB(self, artist, album, album_list, arg):
        self.log.debug("Amazon search for '%s' returned %d results" %\
                       (album.name, len(album_list)));
        if len(album_list):
            # XXX: Always taking the first match.
            album_info = album_list[0];
            url = album_info.getImageURL(albumcover.IMG_SMALL);
            album.small_cover = self._fetchAndSaveImage(url,
                                                        albumcover.IMG_SMALL,
                                                        artist, album);
            if not album.small_cover:
                self.log.info("No album cover found for '%s' by %s" %\
                              (album.name, artist.name));
                self._setAlbumCoverLabel(None);
                return;
            self._setAlbumCoverLabel(album);
            # Update DB
            db = self.archive.getDatabase();
            db.connect();
            db.updateAlbumCovers(album);
            db.commit();
            db.disconnect();

    def _fetchAndSaveImage(self, url_str, sz, artist, album):
        if sz == albumcover.IMG_SMALL:
            sz_str = "SMALL";
        elif sz == albumcover.IMG_MEDIUM:
            sz_str = "MEDIUM";
        elif sz == albumcover.IMG_LARGE:
            sz_str = "LARGE";
        else:
            assert(False);

        dir = self.config.getAlbumCoversDir() + os.sep +\
              mesk.utils.sanitizeFilename(artist.name);
        if not os.path.isdir(dir):
            os.mkdir(dir);
        img_file_path = dir + os.sep +\
                        mesk.utils.sanitizeFilename(album.name) +\
                        ("(%s)" % sz_str) + ".jpg";
        self.log.debug("Fetching %s and storing at %s" %\
                       (url_str, img_file_path));
        url = urllib2.urlopen(url_str);
        image_data = url.read();
        # Check for 1x1 empty image.
        pm = QPixmap();
        pm.loadFromData(image_data);
        if pm.width() == 1 or pm.height == 1:
            return None;
        file_out = file(img_file_path, "wb");
        file_out.write(image_data);
        file_out.close();
        return img_file_path;

    def fileSync(self):
        self._sync_count = 0;
        self._sync_total = self.archive.getNumFiles();
        self.log.info("Syncing archive (%d files)--see the sync log for "\
                      "details" % self._sync_total);
        self.progress_bar.setTotalSteps(self._sync_total);
        self.progress_bar.reset();
        self.statusBar().addWidget(self.progress_bar, False, False);
        self.progress_bar.show();
        self.archive.setSyncCB(self._syncProgressCB);
        self.sync_thread = SyncThread(self.archive);
        self.sync_thread.start();
    def _syncProgressCB(self):
        self._sync_count += 1;
        # Yes, updating Qt on a separate thread.  It does not _seem_ to cause
        # problems :) Anyway, using singleShot did not produce the desired
        # effect
        self.progress_bar.setProgress(self._sync_count, self._sync_total);
        if self._sync_count == self._sync_total:
            self.progress_bar.update();
            QTimer.singleShot(1000, self._resetSyncProgress);
    def _resetSyncProgress(self):
        self.progress_bar.hide();
        self.progress_bar.reset();
        self.statusBar().removeWidget(self.progress_bar);
        self.statusBar().message("Archive synchronized", self.STATUS_TIME);

    def fileSavePlaylist(self):
        self.log.info("Saving playlist '%s'" % self.pl.getName());
        self.pl.save();
        self.statusBar().message("Playlist saved", self.STATUS_TIME);

    def fileImportPlaylist(self):
        pl_path = QFileDialog.getOpenFileName(self.config.getDataDir(),
                                              "M3U Files (*.m3u)", self,
                                              "import_playlist_dialog",
                                              "Choose playlist");
        if pl_path:
            # Conver QString to python string.
            pl_path = str(pl_path);
            self.player_widget.stop();
            self.log.info("Importing playlist '%s'" % pl_path);
            self.pl.load(pl_path);
            self.audio_controller.setPlaylist(self.pl);
            self.playlist_widget.setList(self.pl);
            self._updateCurrentlyPlaying(self.pl[0]);
            self.statusBar().message("Playlist loaded", self.STATUS_TIME);

    def contextMenuEvent(self, ctx_menu_event):
        print "contextMenuEvent in MainWindow"

    def fileExit(self):
        self.emit(PYSIGNAL("mainWindowExit"), ());
    def helpAbout(self):
        dialog = AboutDialog();
        dialog.exec_loop();
        del dialog;

    def viewDefaultPlaylistToggle(self, b):
        print "viewDefaultPlaylistToggle: %d" % b;
    def viewBrowserToggle(self, b):
        print "viewBrowserToggle: %d" % b;
    def viewStreamsToggle(self, b):
        print "viewStreamsToggle: %d" % b;

    def saveAppState(self):
        self.log.debug("MainWindow saving application state");
        # Stop threads
        self.player_widget.stop();
        self.amazon_search.stop();
        # Update db playlist
        self.fileSavePlaylist();
        # Update db ui properties
        db = self.archive.getDatabase();
        db.connect();
        self.ui_props.main_window_width = self.size().width();
        self.ui_props.main_window_height = self.size().height();
        self.ui_props.main_window_pos_x = self.pos().x();
        self.ui_props.main_window_pos_y = self.pos().y();
        db.updateUIProps(self.ui_props);
        db.commit();
        db.disconnect();

class SyncThread(QThread):
    def __init__(self, archive):
        QThread.__init__(self);
        self.archive = archive;
    def run(self):
        self.archive.sync();

