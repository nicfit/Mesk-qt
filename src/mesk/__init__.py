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
#  $Id: __init__.py,v 1.19 2004/12/24 19:51:15 travis Exp $
################################################################################
import os;

import program_info;
import config;
import archive;
import database;
import utils;
import albumcover;

class AudioControl:
    def play(self):
        raise "Not implemented!";
    def stop(self):
        raise "Not implemented!";
    def pause(self):
        raise "Not implemented!";
    def next(self):
        raise "Not implemented!";
    def prev(self):
        raise "Not implemented!";

    def isPlaying(self):
        raise "Not implemented!";
    def isPaused(self):
        raise "Not implemented!";
    def isStopped(self): 
        raise "Not implemented!";

    def seek(self, pos):
        raise "Not implemented!";
    def getLength(self):
        raise "Not implemented!";
    def getPosition(self):
        raise "Not implemented!";

    # Signals
    # playlistPosChanged(int)

##------------------------------------------------------------------------------
if __name__ == "__main__":
    import sys;
    import config;
    import archive;

    profile = 0;
    
    config_file = config.getDefaultConfigFile();
    config = config.Config(config_file);
    for archive_config in config.archives():
        arch = archive.Archive(archive_config);
        if not profile:
            arch.sync();
            # TODO: Create a dummy playlist of all tracks for testing
        else:
            import profile;
            profile.run('arch.sync()', './sync-profile.txt');
            import pstats;
            p = pstats.Stats('./sync-profile.txt');
            p.sort_stats('cumulative').print_stats(100);

    sys.exit(0);

