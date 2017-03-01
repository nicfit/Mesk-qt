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
#  $Id: database.py,v 1.38 2004/12/24 07:37:33 travis Exp $
################################################################################
import os, os.path, datetime, re, stat, threading;
import eyeD3;
import utils, config;

# This string is used for artist, album, and track names that are None or ""
STR_UNKNOWN = unicode("Unknown");

class Artist:
    def __init__(self, row = None):
        if not row:
            self.id = None;
            self.name = u"";
            self.date_added = None;
            self.sync = False;
            self.fuzzy_name = u"";
            self.sort_name = u"";
        else:
            self.id = row[0];
            self.name = unicode(row[1], "utf8");
            self.date_added = row[2];
            self.sync = row[3];
            self.fuzzy_name = unicode(row[4], "utf8");
            self.sort_name = unicode(row[5], "utf8");

class Album:
    def __init__(self, row = None):
        if not row:
            self.id = None;
            self.name = u"";
            self.artist_id = None;
            self.year = None;
            self.date_added = None;
            self.sync = False;
            self.fuzzy_name = None;
            self.small_cover = None;
            self.medium_cover = None;
            self.large_cover = None;
            self.compilation = False;
        else:
            self.id = row[0];
            self.name = unicode(row[1], "utf8");
            self.artist_id = row[2];
            self.year = row[3];
            self.date_added = row[4];
            self.sync = row[5];
            self.fuzzy_name = row[6];
            if row[7]:
                self.small_cover = unicode(row[7], "utf8");
            else:
                self.small_cover = None;
            if row[8]:
                self.medium_cover = unicode(row[8], "utf8");
            else:
                self.medium_cover = None;
            if row[9]:
                self.large_cover = unicode(row[9], "utf8");
            else:
                self.large_cover = None;
            self.compilation = row[10];

class Track:
    def __init__(self, row = None):
        if not row:
            self.id = None;
            self.name = u"";
            self.path = None;
            self.artist_id = None;
            self.album_id = None;
            self.track_num = None;
            self.track_total = None;
            self.time = None;
            self.date_added = None;
            self.bitrate = None;
            self.vbr = False;
            self.sample_freq = False;
            self.mode = None;
            self.audio_type = None;
            self.tag_version = None;
            self.play_count = 0;
            self.play_date = None;
            self.genre_id = None;
            self.file_size = None;
            self.year = None;
            self.fuzzy_name = u"";
            self.mod_time = None;
        else:
            self.id           = row[0];
            self.name         = unicode(row[1], "utf8");
            self.path         = row[2];
            self.artist_id    = row[3];
            self.album_id     = row[4];
            self.track_num    = row[5];
            self.track_total  = row[6];
            self.time         = row[7];
            self.date_added   = row[8];
            self.sync         = row[9];
            self.bitrate      = row[10];
            self.vbr          = row[11];
            self.sample_freq  = row[12];
            self.mode         = row[13];
            self.audio_type   = row[14];
            self.tag_version  = row[15];
            self.play_count   = row[16];
            self.play_date    = row[17];
            self.genre_id     = row[18];
            self.file_size    = row[19];
            self.year         = row[20];
            self.fuzzy_name   = unicode(row[21], "utf8");
            self.mod_time     = row[22];

class MetaData:
    def __init__(self, row = None):
        if not row:
            self.sync_timestamp = None;
            self.archive_size = None;
            self.artist_count = 0;
            self.album_count = 0;
            self.track_count = 0;
            self.total_time = 0;
        else:
            self.sync_timestamp = row[0];
            self.archive_size   = row[1];
            self.artist_count   = row[2];
            self.album_count    = row[3];
            self.track_count    = row[4];
            self.total_time     = row[5];

class UI:
    def __init__(self, row = None):
        if not row:
            self.main_window_pos_x  = None;
            self.main_window_pos_y  = None;
            self.main_window_width  = None;
            self.main_window_height = None;
        else:
            self.main_window_pos_x  = row[0];
            self.main_window_pos_y  = row[1];
            self.main_window_width  = row[2];
            self.main_window_height = row[3];


class DatabaseException(Exception):
   def __init__(self, msg):
      Exception.__init__(self, msg);

class Database:

    def __init__(self, archive_config):
        self.config = archive_config;
        self.conn = None;
        self.cursor = None;

    def connect(self):
        pass;

    def disconnect(self):
        try:
            self.conn and self.conn.close();
            self.cursor and self.cursor.close();
        except sqlite.ProgrammingError:
            pass;
        self.conn = None;
        self.cursor = None;

    def commit(self):
        self._checkState();
        self.conn.commit();

    def clearSync(self):
        self._checkState();
        self.cursor.execute('UPDATE artists SET sync = 0');
        self.cursor.execute('UPDATE albums SET sync = 0');
        self.cursor.execute('UPDATE tracks SET sync = 0');

    def getArtist(self, id = None, archive_file = None, sync = False):
        self._checkState();
        if id:
            self.cursor.execute('SELECT * FROM artists WHERE id=%d', (id));
        elif archive_file:
            name = self.dbString(archive_file.tag.getArtist());
            self.cursor.execute('SELECT * FROM artists WHERE name=%s', (name));
        else:
            raise DatabaseException("Need an id/name");

        row = self.cursor.fetchone();
        if not row:
            return None;
        artist = Artist(row);
        if sync:
            self._sync("artists", artist.id);
        return artist;

    def getAlbum(self, id = None, archive_file = None, artist = None,
                 sync = False):
        self._checkState();
        if id:
            self.cursor.execute('SELECT * FROM albums WHERE id=%d', (id));
        elif archive_file and artist:
            name = self.dbString(archive_file.tag.getAlbum());
            year = archive_file.tag.getYear();
            self.cursor.execute('SELECT * FROM albums WHERE name=%s AND '\
                                'artist_id=%d AND year=%s',
                                (name, artist.id, year));
        else:
            raise DatabaseException("Need an id or archive_file/artist");

        row = self.cursor.fetchone();
        if not row:
            return None;
        album = Album(row);
        if sync:
            self._sync("albums", album.id);
        return album;

    def getTrack(self, id = None, archive_file = None, path = None,
                 sync = False):
        self._checkState();
        if id:
            self.cursor.execute('SELECT * FROM tracks WHERE id=%d', (id));
        elif archive_file:
            self.cursor.execute('SELECT * FROM tracks WHERE path=%s',
                                (archive_file.path));
        elif path:
            self.cursor.execute('SELECT * FROM tracks WHERE path=%s', (path));
        else:
            raise DatabaseException("Need an archive_file or id");

        row = self.cursor.fetchone();
        if not row:
            return None;
        track = Track(row);
        if sync:
            self._sync("tracks", track.id);
        return track;

    # XXX: Until I figure out how to do portable row id stuff, these need to be
    # implemented in the derived classes.
    def addArtist(self, name):
        pass;
    def addAlbum(self, name, year, artist):
        pass;
    def addTrack(self, audio_file, artist, album):
        pass;

    def getMetaData(self):
        self._checkState();
        self.cursor.execute("SELECT * from meta_data;");
        # XXX: User needs to be able to select a row
        row = self.cursor.fetchone();
        if row:
            return MetaData(row);
        return None;

    def updateMetaData(self):
        self._checkState();
        metadata = MetaData();
        metadata.sync_timestamp = datetime.datetime.now();

        self.cursor.execute("SELECT count(id) from artists");
        metadata.artist_count = int(self.cursor.fetchone()[0]);

        self.cursor.execute("SELECT count(id) from albums");
        metadata.album_count = int(self.cursor.fetchone()[0]);

        self.cursor.execute("SELECT count(id) from tracks");
        metadata.track_count = int(self.cursor.fetchone()[0]);

        self.cursor.execute("SELECT sum(time) from tracks");
        metadata.total_time   = int(self.cursor.fetchone()[0]);
        sz = long(0);
        self.cursor.execute("SELECT file_size from tracks");
        for row in self.cursor.fetchall():
            sz += long(row[0]);
        metadata.archive_size = "%s" % utils.formatSize(sz);

        self.cursor.execute("INSERT INTO meta_data "\
                            "(sync_timestamp, archive_size, "\
                            "artist_count, album_count, "\
                            "track_count, total_time) "\
                            "VALUES (%s, %s, %d, %d, %d, %d)",
                            (str(metadata.sync_timestamp),
                             metadata.archive_size,
                             metadata.artist_count, metadata.album_count,
                             metadata.track_count, metadata.total_time));
        return metadata;

    def getUIProps(self):
        self._checkState();
        self.cursor.execute("SELECT * from ui;");
        row = self.cursor.fetchone();
        if row:
            return UI(row);
        return None;

    def updateUIProps(self, ui):
        self._checkState();
        self.cursor.execute("UPDATE ui SET "\
                            "main_window_pos_x=%d, main_window_pos_y=%d, "\
                            "main_window_width=%d, main_window_height=%d",
                            (ui.main_window_pos_x, ui.main_window_pos_y,
                             ui.main_window_width, ui.main_window_height));

    def dbString(self, s, apply_default = True):
        if not s and apply_default:
            s = unicode(STR_UNKNOWN);
        elif not s and s != None:
            s = u"";
        elif s == None:
            return None;

        assert(isinstance(s, unicode));
        # Encode raw bytes for the db
        s = s.encode("utf-8");
        return s.strip("\x00");

    def _fuzzyString(self, s):
        assert(isinstance(s, unicode));
        fuzzy_str = unicode(re.compile("[^\w]",
                            re.UNICODE).subn(u'', s)[0].lower());
        assert(isinstance(fuzzy_str, unicode));
        return fuzzy_str;

    def _artistSortName(self, a):
        sort_name = a;
        if a.find("The ") == 0:
            sort_name = a[len("The "):] + u", The";
        assert(isinstance(sort_name, unicode));
        return sort_name;


    def _sync(self, table, id):
        self.cursor.execute('UPDATE %s SET sync = 1 WHERE id="%d"',
                            (table, id));

    def _checkState(self):
        if not self.conn or not self.cursor:
            raise DatabaseException("Database not connected.");

try:
    import sqlite;
    SQLITE_SUPPORT = 1;

    class SQLiteDatabase(Database):

        def __init__(self, archive_config):
            Database.__init__(self, archive_config);
            # XXX: assert db_type
            db = self.config.db_name;
            if not os.path.isfile(db):
                # TODO: Create an empty db
                raise DatabaseException("SQLite database not found: %s" % (db));
            # Test the database
            self.connect();
            self.disconnect();

        def connect(self):
            self.conn = sqlite.connect(self.config.db_name, 
                                       encoding = "utf-8");
            self._verifySchema();
            self.cursor = self.conn.cursor();

        def addArtist(self, name):
            assert(isinstance(name, unicode));
            self._checkState();

            artist = Artist();
            artist.name = name;
            artist.fuzzy_name = self._fuzzyString(name);
            artist.sort_name = self._artistSortName(name);
            artist.date_added = datetime.date.today();
            self.cursor.execute('INSERT INTO artists (name, date_added, '\
                                '                     fuzzy_name, sort_name) '\
                                'VALUES (%s, %s, %s, %s)',
                                (self.dbString(artist.name),
                                 str(artist.date_added),
                                 self.dbString(artist.fuzzy_name),
                                 self.dbString(artist.sort_name)));
            artist.id = self.cursor.lastrowid;

            self._sync("artists", artist.id);
            return artist;

        def addAlbum(self, archive_file, artist):
            self._checkState();
            album = Album();
            album.name = archive_file.tag.getAlbum();
            album.fuzzy_name = self._fuzzyString(album.name);
            album.date_added = datetime.date.today();
            album.year = archive_file.tag.getYear();
            album.artist_id = artist.id;
            self.cursor.execute('INSERT INTO albums '\
                                '(name, artist_id, year, date_added, '\
                                ' fuzzy_name, compilation) '\
                                'VALUES (%s, %d, %s, %s, %s, %d)',
                                (self.dbString(album.name),
                                 album.artist_id, album.year,
                                 str(album.date_added),
                                 self.dbString(album.fuzzy_name), 0));
            album.id = self.cursor.lastrowid;
            album.sync = True;

            self._sync("albums", album.id);
            return album;

        def _trackFromFile(self, archive_file, artist, album):
            t = Track();
            t.name = archive_file.tag.getTitle();
            assert(isinstance(t.name, unicode));
            t.fuzzy_name = self._fuzzyString(t.name);
            assert(isinstance(t.fuzzy_name, unicode));
            # Note: paths go in as is.
            t.path = archive_file.path;
            t.path = t.path;
            (t.track_num, t.track_total) = archive_file.tag.getTrackNum()
            t.time = archive_file.audio_file.getPlayTime();
            t.date_added = datetime.date.today();
            (t.vbr, t.bitrate) = archive_file.audio_file.getBitRate();
            t.sample_freq = archive_file.audio_file.header.sampleFreq;
            t.mode = archive_file.audio_file.header.mode;
            t.tag_version = "ID3 %s" % (archive_file.tag.getVersionStr());
            t.genre_id = None;
            try:
                genre = archive_file.tag.getGenre();
                if genre:
                    t.genre_id = genre.getId();
            except eyeD3.GenreException, ex:
                # XXX: eyeD3 may be getting more relaxed genre support...
                pass;
            t.file_size = archive_file.audio_file.getSize();
            t.year = archive_file.tag.getYear();
            t.mod_time = archive_file.mod_time;
            t.play_count = archive_file.tag.getPlayCount();
            if t.play_count == None:
                t.play_count = 0;

            return t;

        def updateTrack(self, id, archive_file, artist, album):
            self._checkState();
            t = self._trackFromFile(archive_file, artist, album);
            self.cursor.execute('UPDATE tracks SET '\
                                'name = %s, artist_id = %d, album_id = %d,'\
                                'track_num = %s, track_total = %s, time = %d,'\
                                'bitrate = %d, vbr = %d, sample_freq = %d,'\
                                'mode = %s, audio_type = %s, tag_version = %s,'\
                                'genre_id = %s, file_size = %d, year = %s,'\
                                'fuzzy_name = %s, mod_time = %d '\
                                'WHERE id = %d',
                                (t.name, artist.id, album.id, 
                                 t.track_num, t.track_total, t.time,
                                 t.bitrate, t.vbr, t.sample_freq,
                                 t.mode, "MP3", t.tag_version,
                                 t.genre_id, t.file_size, t.year,
                                 t.fuzzy_name, t.mod_time, id));
            # The play count is NOT updated above, since the DB
            # is the keeper of the most current value.  A play count is used
            # in addTrack though.
            self._sync("tracks", id);
            return t;


        def addTrack(self, archive_file, artist, album):
            self._checkState();
            t = self._trackFromFile(archive_file, artist, album);
            # Note, that %s is used for track_num, track_total, and genre_id,
            # below. This is so that when sqlite _quotes None, we get 'NULL',
            # which is what I want.  Other wise I'd have to stuff '0' in there.
            self.cursor.execute('INSERT INTO tracks '\
                                '(name, path, artist_id, album_id, '\
                                'track_num, track_total, time, date_added,'\
                                'bitrate, vbr, sample_freq, mode, audio_type, '\
                                'tag_version, play_count, play_date, '\
                                'genre_id, file_size, year, '\
                                'fuzzy_name, mod_time) '\
                                'VALUES (%s, %s, %d, %d, %s, %s, %d, %s, '\
                                '%d, %d, %d, %s, %s, %s, %d, %s, %s, %d, '\
                                '%s, %s, %d)',
                                (t.name, t.path, artist.id, album.id,
                                 t.track_num, t.track_total, t.time,
                                 str(t.date_added), t.bitrate, t.vbr,
                                 t.sample_freq, t.mode, "MP3", t.tag_version,
                                 t.play_count, None, t.genre_id, t.file_size,
                                 t.year, t.fuzzy_name, t.mod_time));
            t.id = self.cursor.lastrowid;
            self._sync("tracks", t.id);
            return t;

        def trackPlayed(self, track_id):
            config.app_log.debug("Updating track played info");
            self._checkState();
            self.cursor.execute('UPDATE tracks '\
                                'SET play_count = ' \
                                '(SELECT play_count FROM tracks '\
                                ' WHERE id = %d) + 1'\
                                'WHERE id = %d' % (track_id, track_id));
            self.cursor.execute('UPDATE tracks '\
                                'SET play_date = "%s" WHERE id = %d' %\
                                (str(datetime.datetime.now()), track_id));

        def savePlaylist(self, pl):
            assert(isinstance(pl, Playlist));
            self._checkState();

            # If the playlist already exists delete its tracks, and update.
            pl_name = pl.getName();
            pl_id = self.getPlaylistId(pl.getName());
            if pl_id != None:
                if pl.getCurrentIndex() != None:
                    self.cursor.execute('UPDATE playlists '\
                                        'SET current_track = %d '\
                                        'WHERE id = %d',
                                        (pl.getCurrentIndex(), pl_id));
                self.cursor.execute('DELETE FROM playlist_tracks '\
                                    'WHERE pid = %d' % pl_id);
            else:
                # New playlist.
                self.cursor.execute('INSERT INTO playlists '\
                                    '(name, current_track) '\
                                    'VALUES (%s, %d)',
                                    (self.dbString(pl_name),
                                     pl.getCurrentIndex()));

            # Add tracks to link table
            for t in pl:
                self.cursor.execute('INSERT INTO playlist_tracks '\
                                    '(pid, tid) VALUES (%d, %d)',
                                    (pl_id, t.id));

        def getPlaylistId(self, name):
            row = self.getPlaylistRow(name = name);
            if not row:
                return None;
            return row[0];

        def getPlaylistName(self, id):
            row = self.getPlaylistRow(id = id);
            if not row:
                return None;
            return unicode(row[1], "utf8");

        def getPlaylistRow(self, id = None, name = None):
            assert(id or (name and isinstance(name, unicode)));
            self._checkState();
            if id != None:
                self.cursor.execute('SELECT * FROM playlists WHERE id=%d',
                                    (id));
            else:
                self.cursor.execute('SELECT * FROM playlists WHERE name=%s',
                                    (self.dbString(name)));
            return self.cursor.fetchone()

        def getPlaylist(self, id = None, name = None):
            assert(id or (name and isinstance(name, unicode)));
            if id != None:
                pl_row = self.getPlaylistRow(id = id);
            else:
                pl_row = self.getPlaylistRow(name = name);
            if not pl_row:
                return None;

            pl_id   = pl_row[0];
            pl_curr = pl_row[2];
            # There must be one
            assert(pl_id != None);
            self.cursor.execute('SELECT * FROM playlist_tracks AS plt, '\
                                'tracks AS t WHERE plt.pid = %d AND '\
                                't.id = plt.tid', (pl_id));
            pl = Playlist(name, self);
            for row in self.cursor.fetchall():
                # Chop off 2 playlist_tracks cols.
                track = Track(row[2:]);
                pl.append(track);
            if len(pl):
                pl.setNextIndex(pl_curr);
            return pl;
            
        def updateAlbumCovers(self, album):
            assert(album);
            self._checkState();
            self.cursor.execute("UPDATE albums SET "\
                                "small_cover=%s, "\
                                "medium_cover=%s, "\
                                "large_cover=%s "\
                                'WHERE id = %d',
                                (self.dbString(album.small_cover, False),
                                 self.dbString(album.medium_cover, False),
                                 self.dbString(album.large_cover, False),
                                 album.id));

        def setCompilation(self, album, bool):
            assert(album);
            self._checkState();
            self.cursor.execute("UPDATE albums SET "\
                                "compilation=%d "\
                                'WHERE id = %d',
                                (bool, album.id));

        def _getUnsynced(self, col):
            self._checkState();
            retval = [];
            self.cursor.execute("SELECT * from %s WHERE sync = 0" % (col));
            for row in self.cursor.fetchall():
                # XXX: I'm sure that with more python fu this could be cooler
                if col == "tracks":
                    retval.append(Track(row));
                elif col == "albums":
                    retval.append(Album(row));
                elif col == "artists":
                    retval.append(Artist(row));
            return retval;

        def _delete(self, col, rowid):
            self._checkState();
            self.cursor.execute("DELETE from %s WHERE id = %d" % (col, rowid));

        def removeArtist(self, artist):
            self._delete("artists", artist.id);
        def removeAlbum(self, album):
            self._delete("albums", album.id);
        def removeTrack(self, track):
            self._delete("tracks", track.id);

        def getUnsyncedArtists(self):
            return self._getUnsynced("artists");
        def getUnsyncedAlbums(self):
            return self._getUnsynced("albums");
        def getUnsyncedTracks(self):
            return self._getUnsynced("tracks");

        def getArtists(self):
            self._checkState();
            artists = [];
            self.cursor.execute("SELECT * from artists");
            for row in self.cursor.fetchall():
                artists.append(Artist(row));
            artists.sort(utils.artistNameCompare);
            return artists;

        def getAlbums(self):
            self._checkState();
            albums = [];
            self.cursor.execute("SELECT * from albums");
            for row in self.cursor.fetchall():
                albums.append(Album(row));
            albums.sort(utils.albumNameCompare);
            return albums;

        def getGenres(self):
            self._checkState();
            genres = [];
            # XXX: Genres SUCK!   Attached to track or album??
            self.cursor.execute("SELECT * from albums");
            for row in self.cursor.fetchall():
                albums.append(Album(row));
            albums.sort(utils.albumNameCompare);
            return albums;

        def getTracks(self):
            self._checkState();
            self.cursor.execute("SELECT * from tracks");
            tracks = [];
            for row in self.cursor.fetchall():
                tracks.append(Track(row));
            return tracks;


        def _verifySchema(self):
            cursor = self.conn.cursor();
            cursor.execute("SELECT tbl_name FROM sqlite_master "\
                           "WHERE type='table' ORDER BY tbl_name");
            tables = [];
            for row in cursor.fetchall():
                tables.append(row.tbl_name);
            if tables != ["albums", "artists", "genres", "meta_data",
                          "playlist_tracks", "playlists", "tracks", "ui"]:
                raise DatabaseException("Don't understand database schema: " +\
                                        str(tables));

except ImportError, ex:
    SQLITE_SUPPORT = 0;

try:
    import MySQLdb;
    import MySQLdb.cursors;
    MYSQL_SUPPORT = 1;

    class MySQLDatabase(Database):
        def __init__(self, archive_config):
            Database.__init__(self, archive_config);

        def addArtist(self, artist):
            self.cursor.execute("INSERT INTO artists (name) VALUES (%s)",
                                (artist));
            return self.cursor.insert_id();

except ImportError, ex:
    MYSQL_SUPPORT = 0;

def createDatabase(config):
    if config.db_type == config.SQLITE and SQLITE_SUPPORT:
        return SQLiteDatabase(config);
    elif config.db_type == config.MYSQL and MYSQL_SUPPORT:
        return MySQLDatabase(config);
    else:
        raise DatabaseException("'%s' is not a supported database type" %\
                                (config.db_type));

import os.path, random;

class Playlist(list):

    def __init__(self, name, db, db_tracks = None, path = None, first = None):
        list.__init__(self);

        assert(name and isinstance(name, unicode) and db);
        self._name = name;
        self._db = db;

        # Handle a playlist of database track objects
        if db_tracks:
            for t in db_tracks:
                assert(isinstance(t, Track));
                self.append(t);
        elif path:
            self.load(path);
        self._shuffle = False;
        self._repeat = False;
        self._reset(first);
        self._lock = threading.RLock();

    def clear(self):
        self._lock.acquire();
        while (len(self)):
            self.pop();
        self._lock.release();

    def remove(self, t):
        self._lock.acquire();
        if isinstance(t, Track):
            t = self.index(t);

        # Update current and queue indices
        if self._current != None and t < self._current:
            self._current -= 1;
        new_queue = list(self._queue);
        if t in new_queue:
            new_queue.remove(t);
        for i in range(0, len(new_queue)):
            if t < new_queue[i]:
                new_queue[i] -= 1;
        self._queue = new_queue;

        del self[t];
        self._lock.release();
    # Overridden in terms of self.remove
    def pop(self, i = None):
        if i == None:
            i = len(self) - 1;
        t = self[i];
        self.remove(i);
        return t;

    def insert(self, i, track):
        self._lock.acquire();
        orig_size = len(self);

        # Update current and queue indices
        if self._current != None and i <= self._current:
            self._current += 1;
        new_queue = list(self._queue);
        for j in range(0, len(new_queue)):
            if i < new_queue[j]:
                new_queue[j] += 1;
        self._queue = new_queue;

        list.insert(self, i, track);

        if orig_size == 0:
            self._reset();
        self._lock.release();
    # Overridden in terms of self.insert
    def append(self, track):
        self.insert(len(self), track);

    # Reset state. Note, this method SHOULD be called locked.
    def _reset(self, first_track = None):
        # id to name caches.
        self._artist_cache = {};
        self._album_cache = {};

        # Members used for iterating the playlist
        if first_track != None:
            self._next = self._current = first_track;
        elif len(self):
            self._next = self._current = 0;
        else:
            self._next = self._current = None;
        self._queue = [];
        self._shuffle_history = [];
        self._shuffle_tracks = range(0, len(self));
        random.seed(None);

    def load(self, path):
        self._lock.acquire();
        self.clear();
        # Extended m3u is accepted, although the ext info is not parsed.
        pl_file = file(path);
        self._db.connect();
        for path in pl_file:
            if path[0] == '#':
                continue;
            path = os.path.realpath(os.path.abspath(path)).strip();
            # XXX: Tracks in the playlist must also be in the database
            t = self._db.getTrack(path = path);
            if not t:
                t = Track();
                t.path = path;
                print "track not in db: %s" % path;
                # TODO: Handle tracks that are not in DB
                continue;
            self.append(t);
        self._db.disconnect();
        self._reset();
        self._lock.release();

    def getName(self):
        self._lock.acquire();
        name = self._name;
        self._lock.release();
        return name;
    def setName(self, name):
        assert(name);
        self._lock.acquire();
        self._name = name;
        self._lock.release();

    def getArtist(self, id):
        self._lock.acquire();
        try:
            a = self._artist_cache[id];
        except KeyError:
            self._db.connect();
            a = self._db.getArtist(id = id);
            assert(a);
            self._artist_cache[id] = a;
            self._db.disconnect();
        self._lock.release();
        return a;

    def getAlbum(self, id):
        self._lock.acquire();
        try:
            a = self._album_cache[id];
        except KeyError:
            self._db.connect();
            a = self._db.getAlbum(id = id);
            self._album_cache[id] = a;
            self._db.disconnect();
        self._lock.release();
        return a;

    def enqueue(self, index_list):
        self._lock.acquire();
        for index in index_list:
            if index in self._queue:
                self._queue.remove(index);
            self._queue.append(index);
        self._lock.release();
    def getQueue(self):
        return self._queue;
    def dequeue(self, index_list):
        self._lock.acquire();
        for index in index_list:
            try:
                self._queue.remove(index);
            except ValueError:
                pass;
        self._lock.release();

    # Playlist iteration methods
    def setShuffle(self, b):
        self._lock.acquire();
        if self._shuffle:
            # Reset shuffle state
            self._shuffle_tracks = range(0, len(self));
        self._shuffle = b;
        self._lock.release();
    def isShuffled(self):
        self._lock.acquire();
        b = self._shuffle;
        self._lock.release();
        return b;

    def setRepeat(self, b):
        self._lock.acquire();
        self._repeat = b;
        self._lock.release();
    def isRepeating(self):
        self._lock.acquire();
        b = self._repeat;
        self._lock.release();
        return b;

    def getNextIndex(self):
        self._lock.acquire();
        i = self._next;
        self._lock.release();
        return i;
    def setNextIndex(self, n):
        if n == None:
            pass;
        elif n < 0:
            n = len(self) - 1;
        elif n >= len(self):
            n = 0;
        self._lock.acquire();
        self._next = n;
        self._lock.release();

    # Returns a tuple for the "next" playlist track.
    # retval[0] - The playlist position
    # retval[1] - The eyeTunex.database.Track object
    def getNext(self):
        self._lock.acquire();
        if len(self) == 0:
            self._lock.release();
            return None;

        assert(self._current >= 0 and self._current < len(self));
        # Handle a specific next track request. Yes, this trumps _queue
        if self._next != None:
            self._current = self._next;
            self._next = None;
            next = (self._current, self[self._current]);
            if self._shuffle:
                # Remove the track so it won't be played again
                self._shuffle_tracks.remove(self._current);
                self._shuffle_history.append(next);
            self._lock.release();
            return next;

        # Handle play queue
        if self._queue:
            self._current = self._queue[0];
            self._queue = self._queue[1:];
            next = (self._current, self[self._current]);
            # XXX: History
            self._lock.release();
            return next;

        # Handle repeat mode.
        if self._repeat:
            next = (self._current, self[self._current]);
            if self._shuffle and (next not in self._shuffle_history):
                self._shuffle_history.append(next);
            self._lock.release();
            return next;

        next = None;
        if not self._shuffle:
            self._current += 1;
            if self._current >= len(self):
                self._current = 0;
            next = (self._current, self[self._current]);
        else:
            # Shuffle mode
            if len(self._shuffle_tracks) == 0:
                self._shuffle_tracks = range(0, len(self));
            self._current = random.choice(self._shuffle_tracks);
            next = (self._current, self[self._current]);
            # Remove the track so it won't be played again
            self._shuffle_tracks.remove(self._current);
            self._shuffle_history.append(next);
        assert(next);
        self._lock.release();
        return next;
    
    def getPrev(self):
        self._lock.acquire();
        if len(self) == 0:
            self._lock.release();
            return None;
        assert(self._current >= 0 and self._current < len(self));

        # XXX: Handle _queue history
        if not self._shuffle:
            self._current -= 1;
            if self._current < 0:
                self._current = len(self) - 1;
            self._lock.release();
            return (self._current, self[self._current]);
        elif len(self._shuffle_history) == 0:
            # There aint no goin back
            self._lock.release();
            return (self._current, self[self._current]);
        else:
            prev = self._shuffle_history.pop();
            self._current = prev[0];
            self._lock.release();
            return prev;

    # The last playlist index returned from getNext()
    def getCurrentIndex(self):
        self._lock.acquire();
        i = self._current;
        self._lock.release();
        return i;
    def setCurrentIndex(self, n):
        assert(n >= 0 and n < len(self));
        self._lock.acquire();
        self._current = n;
        self._lock.release();
    def getCurrent(self):
        self._lock.acquire();
        if self._current == None:
            return None;
        curr = self[self._current];
        self._lock.release();
        return curr;

    def save(self):
        self._db.connect();
        self._lock.acquire();
        self._db.savePlaylist(self);
        self._lock.release();
        self._db.commit();
        self._db.disconnect();
        pass;

    def export(self, type):
        self._lock.acquire();
        # XXX: Todo
        self._lock.release();
