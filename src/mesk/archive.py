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
#  $Id: archive.py,v 1.18 2004/12/27 22:37:36 travis Exp $
################################################################################
import os, os.path, md5, re, stat;
from datetime import datetime, timedelta;
import eyeD3;
# Internals
import database, config, utils;

class Archive:
    def __init__(self, archive_config):
        self.config = archive_config;
        self.sync_log = config.sync_log;
        self._sync_cb = None;
        self._clearCache();

    def getDatabase(self):
        return database.createDatabase(self.config);

    def sync(self):
        start_time = datetime.now();
        self.sync_log.info("*** Syncing '%s' archive ***" % (self.config.name));
        self.sync_log.debug("Clearing cache");
        self._clearCache();

        db = self.getDatabase();
        db.connect();

        self.sync_log.debug("Clearing sync bit on all table rows");
        db.clearSync();

        for f in self.files():
            self.sync_log.debug("Processing '%s'" % (f.path));
            (track, artist, album) = self._syncTrack(f, db);
            db.commit();
            if self._sync_cb:
                self._sync_cb();

        self._removed_artists = db.getUnsyncedArtists();
        for a in self._removed_artists:
            self.sync_log.info("Removing artist '%s'" % (a.name));
            db.removeArtist(a);
        self._removed_albums = db.getUnsyncedAlbums();
        for a in self._removed_albums:
            self.sync_log.info("Removing album '%s'" % (a.name));
            db.removeAlbum(a);
        self._removed_tracks = db.getUnsyncedTracks();
        for t in self._removed_tracks:
            self.sync_log.info("Removing track '%s'" % (t.name));
            db.removeTrack(t);

        self.sync_log.info("Updating 'meta_var' table with statistics");
        metadata = db.updateMetaData();

        db.commit();
        db.disconnect();

        end_time = datetime.now();
        self.sync_log.info("*** Archive stats for '%s' @ '%s' ***" %\
                           (self.config.name, str(metadata.sync_timestamp)));
        self.sync_log.info("*** Artist Count: %d (%d new) (%d removed)" %\
                           (metadata.artist_count, len(self._added_artists),
                            len(self._removed_artists)));
        self.sync_log.info("*** Album Count:  %d (%d new) (%d removed)" %\
                           (metadata.album_count, len(self._added_albums),
                            len(self._removed_albums)));
        self.sync_log.info("*** Track Count:  %d (%d new) (%d updated) "\
                           "(%d removed)" %\
                           (metadata.track_count, len(self._added_tracks),
                            len(self._updated_tracks),
                            len(self._removed_tracks)));
        self.sync_log.info("*** Archive Size: %s" % (metadata.archive_size));
        td = timedelta(seconds = metadata.total_time);
        self.sync_log.info("*** Archive Time: %s" %\
                    (utils.formatTimeDelta(td)));
        self.sync_log.info("*** Sync Time:    %s" %\
                           (str(end_time - start_time)));

        # TODO: Compute compilations?

        self._clearCache();

    def getArtists(self):
        db = self.getDatabase();
        db.connect();
        artists = db.getArtists();
        db.disconnect();
        return artists;

    def getTracks(self):
        db = self.getDatabase();
        db.connect();
        tracks = db.getTracks();
        db.disconnect();
        return tracks;

    def _syncArtist(self, file, db):
        # Check cache
        name = file.tag.getArtist();
        if name:
            try:
                artist = self._artist_sync_cache[name];
                return artist;
            except:
                pass;

        artist = db.getArtist(archive_file = file, sync = True);
        if not artist:
            artist = db.addArtist(file.tag.getArtist());
            self._artist_sync_cache[name] = artist;
            self.sync_log.info("Adding artist: '%s'" % (artist.name));
            self._added_artists.append(artist);
        else:
            self.sync_log.debug("Artist exists: '%s'" % (artist.name));
        return artist;

    def _syncAlbum(self, file, db, artist):
        # Cacheing
        album_name = file.tag.getAlbum();
        if album_name and self._last_artist and\
           artist.name == self._last_artist.name:
            if self._last_album and album_name == self._last_album.name:
                return self._last_album;

        album = db.getAlbum(archive_file = file, artist = artist, sync = True);
        if not album:
            album = db.addAlbum(file, artist);
            self.sync_log.info("Adding album: '%s'" % (album.name));
            self._added_albums.append(album);
        else:
            self.sync_log.debug("Album exists: '%s'" % (album.name));

        if album.name == database.STR_UNKNOWN:
            self.sync_log.warn("Missing album: '%s'" % (file.path));

        self._last_artist = artist;
        self._last_album = album;
        return album;

    def _syncTrack(self, file, db):
        track = db.getTrack(archive_file = file, sync = True); 
        if not track:
            artist = self._syncArtist(file, db);
            album = self._syncAlbum(file, db, artist);
            track = db.addTrack(file, artist, album);
            self.sync_log.info("Adding track: '%s'" % (track.name));
            self._added_tracks.append(track);
            if track.name == database.STR_UNKNOWN:
                self.sync_log.warn("Missing track name: '%s'" % (track.path));
        else:
            self.sync_log.debug("Track exists: '%s'" % (track.name));
            artist = self._syncArtist(file, db);
            album = self._syncAlbum(file, db, artist);
            if os.stat(track.path)[stat.ST_MTIME] > track.mod_time:
                track = db.updateTrack(track.id, file, artist, album);
                self.sync_log.info("Updating track: '%s'" % (track.path));
                self._updated_tracks.append(track);

        return (track, artist, album);

    def getNumFiles(self):
        count = long(0);
        for (root, dirs, files) in os.walk(self.config.root):
            for f in files:
                f = os.path.abspath(root + os.sep + f);
                if not self._isExcluded(f) and eyeD3.isMp3File(f):
                    count += 1;
        return count;

    def files(self):
        for (root, dirs, files) in os.walk(self.config.root):
            for f in files:
                f = os.path.abspath(root + os.sep + f);
                if not self._isExcluded(f) and eyeD3.isMp3File(f):
                    try:
                        af = ArchiveFile(f);
                        if not af.tag:
                            self.sync_log.warn("Missing tag '%s'" % f);
                            continue;
                    except (eyeD3.InvalidAudioFormatException,
                            eyeD3.TagException), ex:
                        if isinstance(ex,
                                      eyeD3.InvalidAudioFormatException):
                            self.sync_log.warn("Bad AUDIO '%s'" % (str(ex)));
                        elif isinstance(ex,
                                        eyeD3.TagException):
                            self.sync_log.warn("Bad TAG '%s'" % (str(ex)));
                        continue;
                    yield af;

    def setSyncCB(self, cb):
        self._sync_cb = cb;

    def _isExcluded(self, path):
        for exd in self.config.exclude_dirs:
            match = re.compile(exd).search(path);
            if match and match.start() == 0:
                return 1;
        return 0;

    def _clearCache(self):
        self._artist_sync_cache = {};
        self._last_artist = None;
        self._last_album = None;
        self._added_artists = [];
        self._added_albums = [];
        self._added_tracks = [];
        self._removed_artists = [];
        self._removed_albums = [];
        self._removed_tracks = [];
        self._updated_tracks = [];
        pass;

class ArchiveFile:
    path       = None;
    audio_file = None;
    tag        = None;
    mod_time   = None;

    def __init__(self, path):
        if not os.path.isfile(path) and eyeD3.isMp3File(path):
            raise IOError(path);
        self.audio_file = eyeD3.Mp3AudioFile(path);
        self.tag = self.audio_file.getTag();
        self.mod_time = os.stat(path)[stat.ST_MTIME];
        self.path = path;

if __name__ == "__main__":
    pass;
