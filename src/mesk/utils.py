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
#  $Id: utils.py,v 1.7 2004/12/24 05:33:18 travis Exp $
################################################################################
import sys, os, re;
import datetime;

KB_BYTES = 1024;
MB_BYTES = 1048576;
GB_BYTES = 1073741824;
KB_UNIT = "KB";
MB_UNIT = "MB";
GB_UNIT = "GB";

def formatSize(sz):
    unit = "Bytes";
    if sz >= GB_BYTES:
        sz = float(sz) / float(GB_BYTES);
        unit = GB_UNIT;
    elif sz >= MB_BYTES:
        sz = float(sz) / float(MB_BYTES);
        unit = MB_UNIT;
    elif sz >= KB_BYTES:
        sz = float(sz) / float(KB_BYTES);
        unit = KB_UNIT;
    return "%.2f %s" % (sz, unit);

def formatTimeDelta(td):
    days = td.days;
    hours = td.seconds / 3600;
    mins = (td.seconds % 3600) / 60;
    secs = (td.seconds % 3600) % 60;
    tstr = "%02d:%02d:%02d" % (hours, mins, secs);
    if days:
        tstr = "%d days %s" % (days, tstr);
    return tstr;
    
def formatTrackTime(secs):
    hours = secs / 3600;
    mins = (secs % 3600) / 60;
    secs = (secs % 3600) % 60;
    tstr = "%02d:%02d" % (mins, secs);
    if hours:
        tstr = "%02d:%s" % (hours, tstr);
    return tstr;

# 'sort' comparators
def artistNameCompare(a1, a2):
    return cmp(a1.sort_name, a2.sort_name);
def albumNameCompare(a1, a2):
    return cmp(a1.name, a2.name);

def sanitizeFilename(s):
    return re.compile(os.sep).subn('-', s)[0];
