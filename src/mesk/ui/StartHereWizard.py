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
#  $Id: StartHereWizard.py,v 1.3 2004/12/28 05:01:50 travis Exp $
################################################################################
import sys;
from qt import *;
from StartHereWizardBase import StartHereWizardBase;

class StartHereWizard(StartHereWizardBase):

    def __init__(self, parent = None, name = None, flags = 0):
        StartHereWizardBase.__init__(self, parent = parent,
                                     name = "mesk.ui.StartHereWizard",
                                     modal = True, fl = flags);
        self.connect(self.cancelButton(), SIGNAL("clicked()"),
                     self._cancelled);
        self.connect(self.finishButton(), SIGNAL("clicked()"),
                     self._finished);
        self.setFinishEnabled(self.page(self.pageCount() - 1), True);

    def _cancelled(self):
        print "Cancelled"

    def _finished(self):
        print "Finished"

    def showPage(self, page):
        QWizard.showPage(self, page);

    def getResults(self):
        return None;

