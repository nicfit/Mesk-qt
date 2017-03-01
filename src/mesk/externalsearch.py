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
#  $Id: albumcover.py,v 1.2 2004/12/10 03:14:25 travis Exp $
################################################################################
import sys, time, os.path;
from qt import *;
import amazon;
from Queue import *;

# Image sizes
IMG_SMALL  = 0x1;
IMG_MEDIUM = 0x2;
IMG_LARGE  = 0x4;

class Album(object):
   def __init__(self, bag):
      self.bag = bag;

   def getTitle(self):
      return self.bag.ProductName.encode("utf-8");

   def getArtist(self):
      return self.bag.Artists.Artist.encode("utf-8");

   def getReleaseDate(self):
      if hasattr(self.bag, "ReleaseDate"):
         return self.bag.ReleaseDate.encode("utf-8");
      else:
         return None;

   def getLabel(self):
      if hasattr(self.bag, "Manufacturer"):
         return self.bag.Manufacturer.encode("utf-8");
      else:
         return None;

   def getNumTracks(self):
      t = self.getTracks();
      if t: 
         return len(t);
      else:
         return 0;

   def getTracks(self):
      if hasattr(self.bag, "Tracks"):
         tracks = [];
         for t in self.bag.Tracks.Track:
            tracks.append(t.encode("utf-8"));
         return tracks;
      else:
         return None;

   def getImageURL(self, size):
      if size == IMG_SMALL and hasattr(self.bag, "ImageUrlSmall"):
         return self.bag.ImageUrlSmall.encode("utf-8");
      elif size == IMG_MEDIUM and hasattr(self.bag, "ImageUrlMedium"):
         return self.bag.ImageUrlMedium.encode("utf-8");
      elif size == IMG_LARGE and hasattr(self.bag, "ImageUrlLarge"):
         return self.bag.ImageUrlLarge.encode("utf-8");
      else:
         return None;

   def getURL(self):
      return self.bag.URL.encode("utf-8");

   def getAmazonPrice(self):
       try:
           return self.bag.OurPrice.encode("utf-8");
       except AttributeError:
           return None;

   def getUsedPrice(self):
      if hasattr(self.bag, "UsedPrice"):
         return self.bag.UsedPrice.encode("utf-8");
      else:
         return None;

   def __str__(self):
      s = "";
      s += "\nTitle: %s" % self.getTitle();
      s += "\nArtist: %s" % self.getArtist();
      s += "\nRelease Date: %s" % self.getReleaseDate();
      s += "\nLabel: %s" % self.getLabel();
      s += "\nTracks:"
      c = 1;
      n = self.getNumTracks();
      tracks = self.getTracks();
      if tracks:
         u = "";
         for t in tracks:
            s += "\n\t(%d/%s%d) %s" % \
                  (c, u, n, t);# u is an empty string; I had to do it though >:)
            c += 1;
      else:
         s += "\nNo tracks! :(";
      s += "\nImage URL (Large): %s" % self.getImageURL(IMG_LARGE);
      s += "\nImage URL (Medium): %s" % self.getImageURL(IMG_MEDIUM);
      s += "\nImage URL (Small): %s" % self.getImageURL(IMG_SMALL);
      s += "\nAmazon Price: %s" % self.getAmazonPrice();
      s += "\nUsed Price: %s" % self.getUsedPrice();
      s += "\nSee Amazon: %s" % self.getURL();
      # XXX: There is a lot of other stuff in the amazon search result.
      # See the README
      return s;

class ExternalSearchThread(QThread):
    # We need a reference to prevent GC

    def __init__(self, config):
        QThread.__init__(self);
        self._queue = Queue(-1);
        amazon.setLicense(config.getAmazonKeyFile());
        self._config = config;
        self._stopped = False;

    def stop(self):
        self._config.getLog().debug("ExternalSearchThread stopped");
        self.search(None, None, None, None);

    def search(self, artist, album, cb, cb_arg):
        self._queue.put((artist, album, cb, cb_arg));

    def run(self):
        self._config.getLog().debug("ExternalSearchThread started");
        while not self._stopped:
            (artist, album, cb, cb_arg) = self._queue.get();
            if not artist and not album and not cb:
                self._stopped = True;
            else:
                assert(artist and cb);
                if album:
                    query = artist.name + " " + album.name;
                else:
                    query = artist.name;

                albumList = [];
                try:
                    # Loop to get all the result "pages". An AmazonError kicks
                    # us out of the loop.
                    n = 1;
                    while 1:
                        results = amazon.searchByKeyword(query,
                                                         product_line = "music",
                                                         page = n);
                        n += 1;
                        for res in results:
                            albumList.append(Album(res));
                except amazon.NoLicenseKey, ex:
                    assert(0); pass;
                except amazon.AmazonError, ex:
                    # This is trown when there are no more result pages.
                    pass;
                # Invlode the user callback with the results.
                cb(artist, album, albumList, cb_arg);
        self._config.getLog().debug("ExternalSearchThread finished");

class AlbumCoverMgr(object):
    def __init__(self, config):
        self._config = config;
        self._external_search = ExternalSearchThread(config);
        self._external_search.start();
    def __del__(self):
        self._external_search.stop();

    def get(self, artist, album, cb, cb_arg):
        # TODO
        pass;
