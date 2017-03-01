################################################################################
#  Copyright (C) 2003  Travis Shirk <travis@pobox.com>
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
#  $Id: database-mysql.py,v 1.1 2004/09/05 03:43:42 travis Exp $
################################################################################
import eyeTunez.config;
import MySQLdb;
import MySQLdb.cursors;

class Database:
   type = None;
   host = None;
   user = None;
   password = None;
   name = None;
   conn = None;
   cursor = None;

   def __init__(self, config):
      try:
         self.type = config.get(config.DATABASE, "type");
         if self.type != "MySQL":
            raise DatabaseException("Currently, only MySQL is supported.");
         self.host = config.get(config.DATABASE, "host");
         self.user = config.get(config.DATABASE, "user");
         self.password = config.get(config.DATABASE, "pass");
         self.name = config.get(config.DATABASE, "name");
      except Exception, ex:
         raise DatabaseException(str(ex));


   def connect(self):
      try:
         self.conn = MySQLdb.connect(host=self.host, user=self.user,
                                     passwd=self.password, db=self.name,
                                     cursorclass=MySQLdb.cursors.DictCursor);
         self.cursor = self.conn.cursor();
      except MySQLdb.OperationalError, ex:
         raise DatabaseException(str(ex));

   def disconnect(self):
      if self.conn:
         self.conn.close();
      if self.cursor:
         self.cursor.close();

   def hasArtist(self, artist):
      self.cursor.execute("SELECT id FROM artist WHERE name=%s", (artist));
      return (self.cursor.fetchone() != None);

   # Returns the new artist Id.
   def addArtist(self, artist):
      self.cursor.execute("INSERT INTO artist (name) VALUES (%s)", (artist));
      return self.cursor.insert_id();

################################################################################
class DatabaseException(Exception):
   def __init__(self, msg):
      Exception.__init__(self, msg);

