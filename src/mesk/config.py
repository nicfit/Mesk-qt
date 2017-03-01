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
#  $Id: config.py,v 1.17 2005/02/17 03:36:25 travis Exp $
################################################################################
import sys, os, os.path, ConfigParser;
import logging, logging.config;
from program_info import *;

# Config defaults
CONFIG_FILE_ENV_VAR = "%sRC" % (APPNAME.upper());
DEFAULT_CONFIG_FILE = os.path.expandvars("${HOME}/.%src" % (APPNAME.lower()));
DEFAULT_DATA_DIR  = os.path.expandvars("${HOME}/.%s" % (APPNAME.lower()));
DEFAULT_PLAYLIST_FILE  = "%s.m3u" % (APPNAME);

# A logger for basic operations
app_log = None;
# A logger for sync operations
sync_log = None;

def getDefaultConfigFile():
    if os.getenv(CONFIG_FILE_ENV_VAR):
        return os.getenv(CONFIG_FILE_ENV_VAR);
    return os.path.abspath(DEFAULT_CONFIG_FILE);
def getDefaultConfig():
    return Config(getDefaultConfigFile());

class ConfigException(Exception):
    def __init__(self, msg):
       Exception.__init__(self, msg);

# This class represents the Mesk configuration as a ConfigParser, but adds
# soem helpers for accessing ArchiveConfig objects.
class Config(ConfigParser.ConfigParser):
    MAIN_SECT = APPNAME.upper();
    AUDIO_SECT = "audio";

    AUDIO_OSS  = "oss";
    AUDIO_ALSA = "alsa";
    AUDIO_ESD  = "esd";

    file = None;
    _archive_names   = [];
    _archive_configs = {};
    _data_dir = None;
    audio_sink = AUDIO_OSS;
    gap_delay = None;

    def __init__(self, path):

        ConfigParser.ConfigParser.__init__(self);

        # Parse
        fp = file(path, "r");
        self.readfp(fp);
        fp.close();
        self.file = path;

        # Make the MAIN section the DEFAULTS
        self._defaults = {};
        for item in self.items(APPNAME.upper()):
            self._defaults[item[0]] = item[1];
 
        self._validate();

        # Config MESK.data_dir
        data_dir = self.get(self.MAIN_SECT, "data_dir");
        if not data_dir:
            data_dir = DEFAULT_DATA_DIR;
        data_dir = os.path.expandvars(data_dir);
        # Album covers go in data_dir for now.
        album_covers_dir = data_dir + os.sep + "album_covers";
        if not os.path.isdir(data_dir):
            sys.stdout.write("Making Mesk data dir: %s" % data_dir);
            os.mkdir(data_dir);
            os.mkdir(album_covers_dir);
        self._data_dir = data_dir;
        self._album_covers_dir = album_covers_dir;

        # Configure logging
        logging.config.fileConfig(path, {"data_dir": self._data_dir});
        global app_log;
        app_log = logging.getLogger("app");
        global sync_log;
        sync_log = logging.getLogger("sync");

        # Config audio
        audio_sink = self.get(self.AUDIO_SECT, "audio_sink");
        if audio_sink and audio_sink != self.AUDIO_OSS and\
           audio_sink != self.AUDIO_ESD and audio_sink != self.AUDIO_ALSA:
            raise ConfigException("Invalud audio.audio_sink value: %s" %\
                                  audio_sink);
        elif audio_sink:
            self._audio_sink = audio_sink;
        gd = self.get(self.AUDIO_SECT, "gap_delay");
        if gd:
            try:
                self._gap_delay = int(gd);
            except ValueError:
                raise ConfigException("Invalud audio.gap_delay value: %s" %\
                                      gd);
            if self._gap_delay <= 0:
                raise ConfigException("Invalud audio.gap_delay value: "\
                                      "%s <= 0" % self._gap_delay);

        names = self.get(self.MAIN_SECT, "archives");
        for a in names.split():
            self._archive_names.append(a);
            self._archive_configs[a] = ArchiveConfig(a, self);

    def getLog(self, which = "default"):
        global app_log;
        global sync_log;
        if which == "sync":
            return sync_log;
        else:
            return app_log;

    def getDataDir(self):
        return self._data_dir;
    def getAlbumCoversDir(self):
        return self._album_covers_dir;
    def getAudioSink(self):
        return self._audio_sink;
    def getGapDelay(self):
        return self._gap_delay;
    def getAmazonKeyFile(self):
        return self._data_dir + os.sep + "amazonkey.txt";

    def getDefaultPlaylist(self):
        return self._data_dir + os.sep + DEFAULT_PLAYLIST_FILE;

    def getArchiveNames(self):
        return self._archive_names;

    def getArchiveConfig(self, name):
        return self._archive_configs[name];

    def getFirstArchiveConfig(self):
        return self.getArchiveConfig(self._archive_names[0]);

    def archives(self):
        for a_name in self._archive_names:
            yield self._archive_configs[a_name];

    def _validate(self):
        if not self.has_option(APPNAME.upper(), "archives"):
            raise ConfigException("Missing %s:archives config" %\
                                  (APPNAME.upper()));
        archive_list = self.get(self.MAIN_SECT, "archives");
        for a in archive_list.split():
            if not self.has_section(a):
                raise ConfigException("No config section for '%s' found" % (a));

    def optionxform(self, optionstr):
        return str(optionstr);


class ArchiveConfig:
   SQLITE = "SQLite";
   MYSQL  = "MySQL";

   name         = None;
   root         = None;
   exclude_dirs = [];

   db_type = None;
   db_name = None;
   db_host = None;
   db_user = None;
   db_pass = None;

   def __init__(self, name, config):
      if not name:
          raise ConfigException("Archive MUST have a name");

      try:
         root = config.get(name, "root");
         if not os.path.isdir(root):
             raise IOError("No such file or directory: %s" % (root));
         self.root = root;

         self.exclude_dirs = [];
         if config.has_option(name, "exclude"):
             dirs = config.get(name, "exclude");
             for ed in dirs.split():
                 self.exclude_dirs.append(ed);

         db_type = config.get(name, "db_type");
         if db_type != self.SQLITE and db_type != self.MYSQL:
             raise ConfigException("Invalid db_type '%s'. Use 'SQLite' or "\
                                   "'MySQL'." % (db_type));

         # XXX: No database validation going on yet.
         self.db_type = db_type;
         db_name = config.get(name, "db_name");
         # If this is not a path (no os.sep chars) then it is relative to the
         # data_dir.
         if not os.sep in db_name:
             db_name = os.path.abspath(config.getDataDir() + os.sep + db_name);
         self.db_name = db_name;
         if self.db_type == self.MYSQL:
             self.db_host = config.get(name, "db_host");
             self.db_user = config.get(name, "db_user");
             self.db_pass = config.get(name, "db_pass");
      except Exception, ex:
         raise ConfigException(str(ex));
      self.name = name;

# Config file template
CONFIG_TEMPLATE = \
"""
[MESK]
; A list of music archives, each referring to a config section below.
; There archive name MUST NOT contain whitespace characters.
archives = Main
; The directory where databases are stored
data_dir = @DATA_DIR@

[Main]
; The root path to your tunez
root = @MAIN_ARCHIVE_ROOT@
; Directories to exclude from root.  These SHOULD end with '/' to prevent 
; partial mactches.
exclude = 
; The type of database backend used.  Current only 'SQLite' is supported.
db_type = SQLite
; The name of the database. In SQLite the name is the file path of the datbase
; file.
db_name = Main.db

;; Audio configuration
[audio]
; Output layers.  May be one of 'alsa', 'oss', or 'esd' depending on the
; gstreamer plugins available;
audio_sink = oss
; The number of milliseconds to pause between tracks.
gap_delay = 1000

;; Logging configuration
;; Described here: http://www.python.org/doc/2.3.4/lib/module-logging.html
[loggers]
keys = root,app,sync
[handlers]
keys = stderr,applog,synclog
[formatters]
keys = common,sync

[logger_root]
level = NOTSET
handlers = stderr
[logger_app]
level = DEBUG
handlers = applog
propogate = 0
qualname = app
[logger_sync]
level = INFO
handlers = synclog
propogate = 0
qualname = sync

[handler_stderr]
level = ERROR
class = StreamHandler
formatter = common
args = (sys.stderr,)
[handler_applog]
level = NOTSET
class = FileHandler
formatter = common
args = ('%(data_dir)s/mesk.log', 'a')
[handler_synclog]
level = NOTSET
class = FileHandler
formatter = sync
args = ('%(data_dir)s/sync.log', 'a')

[formatter_common]
level = NOTSET
format = %(asctime)s %(levelname)s %(message)s
datefmt =
[formatter_sync]
level = NOTSET
format = [%(levelname)s] %(message)s
datefmt =
""";

class ApplicationState:
    # This list contains tuple objects containing:
    # 0: The playlists database id
    # 1: An integer containing the current playlist position (0 indexed)
    playlists = [];
