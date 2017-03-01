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
#  $Id: AudioControlWidget.py,v 1.8 2004/12/24 05:33:18 travis Exp $
################################################################################
import sys;
from qt import *;
import mesk;
from AudioControlWidgetBase import AudioControlWidgetBase;

play_image_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x18\x00\x00\x00\x18" \
    "\x08\x06\x00\x00\x00\xe0\x77\x3d\xf8\x00\x00\x00" \
    "\xfd\x49\x44\x41\x54\x48\x89\xed\xd2\x41\x2e\x43" \
    "\x51\x14\xc6\xf1\xff\x73\xce\xed\xe3\xde\x97\x97" \
    "\xd6\xa0\x6c\xa0\x42\x50\xf4\x99\x10\x7b\xb0\x0c" \
    "\x09\x06\x98\x62\x09\xc2\x16\x24\xac\x43\xc2\xb4" \
    "\xfb\xb0\x8c\x63\x20\x1d\xb6\x3d\xf7\xa5\x9d\xf5" \
    "\x1b\x9f\x7c\xbf\x73\x92\x03\xab\xcc\x89\x38\x66" \
    "\x2e\x81\x0a\xf8\x6d\x03\xac\x39\x66\xb6\x81\x31" \
    "\xd0\x2c\x0b\x98\xa4\x15\xe2\x06\x1e\xee\xef\x5a" \
    "\x21\x6e\x60\x23\x46\x6e\x6f\xae\xb3\x11\x37\xa0" \
    "\x22\x1c\x0e\x0f\x78\x7e\x7a\xcc\x42\xdc\x80\x88" \
    "\xa0\xa2\x34\xcd\x09\x6f\xaf\x2f\x6e\xc4\x7f\x81" \
    "\x0a\xaa\x8a\x6a\x60\x67\x30\xe0\xf3\xe3\xdd\x85" \
    "\xe4\x5d\xa0\x42\x50\x41\x83\xb2\xd5\xef\xf3\xf3" \
    "\xfd\x05\x30\x36\x33\x9b\xba\x58\x1e\xa0\x68\x08" \
    "\xac\x97\x25\x29\x55\x1c\x8f\x4e\x31\x33\x8a\xa2" \
    "\x28\x16\x02\x54\xa9\x22\xc6\x48\x4a\x89\xe1\xd1" \
    "\x68\x6e\x79\x16\x50\xd7\x35\x2a\x42\xaf\xb7\xc9" \
    "\xee\xde\xbe\xab\x1c\x32\xdf\xb4\xee\x76\xb3\xca" \
    "\xb3\x80\x4e\xd9\xe1\xec\xfc\x22\xab\xdc\x9b\x2b" \
    "\xc0\x00\x9b\xf5\x2d\xd3\xe2\xb9\x20\xf1\xdf\xbe" \
    "\xf0\xcd\x27\x69\xda\x6c\xee\xce\x32\xbb\x57\x01" \
    "\xe0\x0f\x2e\xfa\x3d\x63\x47\x25\x88\x6e\x00\x00" \
    "\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82"

pause_image_data = \
    "\x89\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d" \
    "\x49\x48\x44\x52\x00\x00\x00\x18\x00\x00\x00\x18" \
    "\x08\x06\x00\x00\x00\xe0\x77\x3d\xf8\x00\x00\x00" \
    "\xef\x49\x44\x41\x54\x48\x89\xed\x94\x31\x6e\xc2" \
    "\x30\x14\x40\x5f\xe2\x6f\x48\xe3\x28\x25\x12\x1c" \
    "\x00\xd1\xb5\x4b\x8f\x56\x16\x7a\x94\x6e\xbd\x59" \
    "\x17\x8e\x90\x11\xfc\xbb\xa0\x8a\x40\x3e\xb2\xab" \
    "\x54\x2c\x3c\xc9\x52\xf2\xbe\x94\x17\x7b\x30\x3c" \
    "\xb8\x37\x85\xe1\xd7\xc0\xf3\xe9\xd9\x03\x15\xb0" \
    "\x3f\xbd\x5f\x79\x55\xfd\x2e\x0a\xeb\x53\xe3\xbc" \
    "\x01\x7a\xb9\x54\xf5\xca\x9d\xf9\x51\xc4\xf0\x25" \
    "\xc0\x76\xfb\x4e\xd7\x75\x88\x08\xbb\xdd\xc7\xef" \
    "\xd0\xf2\x39\x01\x00\x42\x08\xbc\x6c\x36\x1c\x8e" \
    "\xc7\x24\x6f\xfe\xe9\x2d\x62\x8c\x74\x8b\x45\xb2" \
    "\x4f\x0d\x44\x80\xf9\x6c\x86\x88\x23\x84\x30\x18" \
    "\x5a\x3e\x27\x00\x40\xd3\x04\xbc\xf7\xd4\xa1\x4e" \
    "\xf2\xd9\x81\x29\xb8\x5b\x20\x02\xac\x56\x4b\x9a" \
    "\x26\x50\x3f\x0d\x8f\xc2\xf2\x39\x81\xc9\xb8\x19" \
    "\xa8\xaa\x39\xe2\x1c\xae\x2c\x92\x7c\x4e\xe0\x00" \
    "\x20\x4e\x10\x11\x4a\xe7\x06\x43\xcb\xe7\x04\x0a" \
    "\x00\xe7\x1c\x6d\xdb\xe2\xbd\x1f\x0c\x2d\x9f\xc3" \
    "\x2b\x13\x5d\x76\xd6\x0e\xf6\xaa\xca\xe5\xea\xfb" \
    "\xfe\x6b\xcc\x03\x9f\x7f\xde\xca\x83\x7f\xe7\x07" \
    "\xef\x4a\x66\xb5\xf6\xaa\x0b\x50\x00\x00\x00\x00" \
    "\x49\x45\x4e\x44\xae\x42\x60\x82"

class AudioControlWidget(AudioControlWidgetBase):
    PLAY  = 0;
    PAUSE = 1;
    _play_pause_state = PLAY;
    # XXX: Hardcoded language
    PLAY_TOOLTIP  = "Play Track";
    PAUSE_TOOLTIP = "Pause Track";

    def __init__(self, parent = None, name = None, flags = 0):
        AudioControlWidgetBase.__init__(self, parent, name, flags);

        self.play_pixmap = QPixmap();
        self.play_pixmap.loadFromData(play_image_data, "PNG");
        self.pause_pixmap = QPixmap();
        self.pause_pixmap.loadFromData(pause_image_data, "PNG")
        # The initial state for the button is PLAY
        self._setPlayPauseState(self.PLAY);

        self.connect(self.play_pause_button, SIGNAL("clicked()"),
                     self._playPauseCB);
        self.connect(self.stop_button, SIGNAL("clicked()"), self.stop);
        self.connect(self.next_button, SIGNAL("clicked()"), self.next);
        self.connect(self.prev_button, SIGNAL("clicked()"), self.prev);

        self.time_label.setText(mesk.utils.formatTrackTime(0));
        self._is_time_increasing = True;
        self.track_slider.setMinValue(0);
        self.track_slider.setMaxValue(0);
        self.track_slider.setEnabled(False);

    def isTimeIncreasing(self):
        return self._is_time_increasing;

    def displayTime(self, sec):
        n = sec;
        if not self._is_time_increasing:
            n = self.track_slider.maxValue() - sec;
        if n >= 0:
            self.time_label.setText(mesk.utils.formatTrackTime(n));
            self.track_slider.setValue(sec);

    def _playPauseCB(self):
        if self._play_pause_state == self.PLAY:
            self.play();
            self._setPlayPauseState(self.PAUSE);
        else:
            self.pause();
            self._setPlayPauseState(self.PLAY);

    def externalPlayPause(self, state):
        assert(state == self.PLAY or state == self.PAUSE);
        self._setPlayPauseState(state);

    def _setPlayPauseState(self, state):
        assert(state == self.PLAY or state == self.PAUSE);
        if state == self.PAUSE:
            self.play_pause_button.setPixmap(self.pause_pixmap);
            QToolTip.add(self.play_pause_button, self.PAUSE_TOOLTIP);
            self._play_pause_state = self.PAUSE;
            self.play_pause_button.update();
        else:
            self.play_pause_button.setPixmap(self.play_pixmap);
            QToolTip.add(self.play_pause_button, self.PLAY_TOOLTIP);
            self._play_pause_state = self.PLAY;
            self.play_pause_button.update();


    def play(self):
        self.emit(PYSIGNAL("play"), ());
        self.track_slider.setEnabled(True);
    def pause(self):
        self.emit(PYSIGNAL("pause"), ());
    def stop(self):
        self._setPlayPauseState(self.PLAY);
        self.track_slider.setValue(0);
        self.track_slider.setEnabled(False);
        self.emit(PYSIGNAL("stop"), ());
    def next(self):
        self.emit(PYSIGNAL("next"), ());
        self._setPlayPauseState(self.PAUSE);
    def prev(self):
        self.emit(PYSIGNAL("prev"), ());
        self._setPlayPauseState(self.PAUSE);

    def mouseReleaseEvent(self, mouse_event):
        # Toggle time display; counting up or counting down
        if self.childAt(mouse_event.x(), mouse_event.y()) == self.time_label:
            self._is_time_increasing = not self._is_time_increasing;

