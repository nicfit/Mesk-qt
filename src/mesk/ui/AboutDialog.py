# -*- coding: utf8 -*-
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
#  $Id: AboutDialog.py,v 1.2 2004/12/28 00:34:32 travis Exp $
################################################################################
import sys;
from mesk.program_info import *;
from qt import *;
from AboutDialogBase import AboutDialogBase;

ABOUT_LABEL =\
u"""<p align="center">
<b>%(APPNAME)s version %(VERSION)s</b><br/>
Written by Travis Shirk &lt;travis@pobox.com&gt;<br/>
Coyright 2005
</p>""";

PROPS =\
u"""Melvins, Modest Mouse, Cannibal Ox, Ambulance LTD, 764-Hero,
Reagan Youth, Isis, Refused, Gram Rabbit, Melt-Banana, Bloc Party, Hard Stance,
TV On The Radio, Unsane, The Unicorns, Fantômas, Government Issue, Burn,
Godflesh, Cult Of Luna, Enon, KMD, The Faint, Iceburn, Fugazi, The Cure, Spoon,
and Single Frame""";


class AboutDialog(AboutDialogBase):

    def __init__(self, parent = None, name = None, flags = 0):
        AboutDialogBase.__init__(self, parent = parent,
                                 name = "AboutDialogBase",
                                 modal = True, fl = flags);
        about_label_text = ABOUT_LABEL % {"APPNAME": APPNAME,
                                          "VERSION": VERSION};
        self.about_label.setText(QString(about_label_text));
        self.props_textedit.setText(QString(PROPS));


