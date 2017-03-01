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
#  $Id: GstAudioControl.py,v 1.25 2004/12/27 21:37:09 travis Exp $
################################################################################

import os, gobject;
os.environ['PYGTK_USE_GIL_STATE_API'] = '';
gobject.threads_init();
import gst;

from qt import *;
import mesk;
from mesk import *;

class GstAudioControl(AudioControl, QObject):

    UPDATE_INTERVAL_MS = 500;
    FILE_SRC   = 1;
    STREAM_SRC = 2;
    CD_SRC     = 3

    def __init__(self, player_widget, config, pl):
        QObject.__init__(self);
        assert(player_widget);
        QObject.connect(player_widget, PYSIGNAL("play"), self.play);
        QObject.connect(player_widget, PYSIGNAL("stop"), self.stop);
        QObject.connect(player_widget, PYSIGNAL("pause"), self.pause);
        QObject.connect(player_widget, PYSIGNAL("next"), self.next);
        QObject.connect(player_widget, PYSIGNAL("prev"), self.prev);

        self.player_widget = player_widget;
        QObject.connect(player_widget.track_slider, SIGNAL("sliderPressed()"),
                        self._trackSliderPressed);
        QObject.connect(player_widget.track_slider, SIGNAL("sliderReleased()"),
                        self._trackSliderReleased);
        QObject.connect(player_widget.track_slider, SIGNAL("sliderMoved(int)"),
                        self._trackSliderMoved);

        self.log = mesk.config.app_log;
        self._gap_delay = config.getGapDelay();
        self.config = config;

        self.pipeline = None;
        self.curr_src_type = self.FILE_SRC;
        self._createPipeline(self.FILE_SRC);

        self.tick_timer = QTimer(self.player_widget);
        QObject.connect(self.tick_timer, SIGNAL("timeout()"),
                        self._tick);

        self.setPlaylist(pl);
        self._rewind_flag = False;
        self._rewind_set = False;

    def _createPipeline(self, src_type):
        if self.pipeline:
            self.pipeline.set_state(gst.STATE_NULL);
            del self.pipeline;

        pipeline = gst.element_factory_make("thread", "pipeline");
        pipeline.connect("error", self._gst_errorCB);
        self.pipeline = pipeline;

        if src_type == self.STREAM_SRC:
            waiting_bin = gst.element_factory_make("thread", "waiting_bin");
            src_thread = gst.element_factory_make("thread", "src_thread");
            pipeline.add_many(waiting_bin, src_thread);

        src = gst.element_factory_make("gnomevfssrc", "src");
        if src_type == self.STREAM_SRC:
            src_thread.add(src);
        else:
            pipeline.add(src);
        self.src = src;

        if src_type == self.STREAM_SRC:
            queue = gst.element_factory_make("queue", "queue");
            queue.set_property("max-size-bytes", 64 * 1024)
            queue.connect("overrun", self._queueFullCB);
            src_thread.add(queue);

        typefind = gst.element_factory_make("typefind", "typefind");
        if src_type == self.STREAM_SRC:
            waiting_bin.add(typefind);
        else:
            pipeline.add(typefind);

        decoder = gst.element_factory_make("spider", "decoder");
        src.connect("eos", self._gst_eosCB);
        if src_type == self.STREAM_SRC:
            waiting_bin.add(decoder);
        else:
            pipeline.add(decoder);
        self.decoder = decoder;
        
        volume = gst.element_factory_make("volume", "volume");
        if src_type == self.STREAM_SRC:
            waiting_bin.add(volume);
        else:
            pipeline.add(volume);
        volume.set_property('volume', 1.00)
        self.volume = volume;

        audioconvert = gst.element_factory_make("audioconvert", "audioconvert");
        if src_type == self.STREAM_SRC:
            waiting_bin.add(audioconvert);
        else:
            pipeline.add(audioconvert);

        audioscale = gst.element_factory_make("audioscale", "audioscale");
        if src_type == self.STREAM_SRC:
            waiting_bin.add(audioscale);
        else:
            pipeline.add(audioscale);

        audio_sink = self._createAudioSink();
        if src_type == self.STREAM_SRC:
            waiting_bin.add(audio_sink);
        else:
            pipeline.add(audio_sink);
        self.audio_sink = audio_sink;

        gst.element_link_many(decoder, volume, audioconvert, audioscale,
                              audio_sink);

        if src_type == self.STREAM_SRC:
            gst.element_link_many(src, queue, typefind, decoder);
        else:
            gst.element_link_many(src, typefind, decoder);

        self.pipeline.set_state(gst.STATE_READY)

    def _createAudioSink(self):
        config_sink = self.config.getAudioSink();
        if config_sink == self.config.AUDIO_OSS:
            self.log.debug("GstAudioControl using OSS");
            audio_sink = gst.element_factory_make("osssink", "audio_sink");
        elif config_sink == self.config.AUDIO_ALSA:
            self.log.debug("GstAudioControl using ALSA");
            audio_sink = gst.element_factory_make("alsasink", "audio_sink");
        elif config_sink == self.config.AUDIO_ESD:
            self.log.debug("GstAudioControl using ESD");
            audio_sink = gst.element_factory_make("esdsink", "audio_sink");
        else:
            # Config should have cause this
            assert(0);
        return audio_sink;

    def setPlaylist(self, pl):
        assert(isinstance(pl, database.Playlist));
        self._playlist = pl;
        if self.isStopped():
            self._advancePlaylist();
    def getPlaylist(self):
        return self._playlist;

    def _advancePlaylist(self, forward = True):
        assert(self.isStopped());
        next = None;
        if forward:
            next = self._playlist.getNext();
        else:
            if self._rewind_flag:
                self._rewind_flag = False;
                self.play();
            else:
                next = self._playlist.getPrev();
        if next and next[0] != None:
            self.setSourceTrack(next[1]);

    # Signals emmitted by this class
    # audioPlaying(int) - The track started playing
    # audioStopped(int) - The track stopped playing
    # audioPaused(int) - The track paused playing
    # audioComplete(int) - The track played until the end
    # audioSkipped(int) - The track was skipped.

    def play(self):
        if self.isPlaying():
            return;
        self.player_widget.stop_button.setEnabled(True);
        self.pipeline.set_state(gst.STATE_PLAYING)
        self._startPlayTick();
        self.emit(PYSIGNAL("audioPlaying(int)"),
                  (self._playlist.getCurrentIndex(),));

    def stop(self):
        if self.isStopped():
            return;
        self.pipeline.set_state(gst.STATE_READY)
        self._stopPlayTick();
        self.player_widget.stop_button.setEnabled(False);
        self.player_widget.displayTime(0);
        self.emit(PYSIGNAL("audioStopped(int)"),
                  (self._playlist.getCurrentIndex(),));

    def pause(self):
        if self.isPaused():
            return;
        self._stopPlayTick();
        self.pipeline.set_state(gst.STATE_PAUSED);
        self.audio_sink.set_state(gst.STATE_NULL);
        self.emit(PYSIGNAL("audioPaused(int)"),
                  (self._playlist.getCurrentIndex(),));

    def next(self):
        self.stop();
        self.emit(PYSIGNAL("audioSkipped(int)"),
                  (self._playlist.getCurrentIndex(),));
        if self._playlist.isRepeating():
            self._playlist.setNextIndex(self._playlist.getCurrentIndex() + 1);
        self._advancePlaylist();
        self.play();

    def prev(self):
        self.stop();
        self.emit(PYSIGNAL("audioSkipped(int)"),
                  (self._playlist.getCurrentIndex(),));
        if self._playlist.isRepeating():
            self._playlist.setNextIndex(self._playlist.getCurrentIndex() - 1);
        # Going backward with 'False'
        self._advancePlaylist(False);
        self.play();

    def seek(self, pos):
        pos = long(pos * 1000000000);
        event = gst.event_new_seek(gst.FORMAT_TIME |
                                   gst.SEEK_METHOD_SET |
                                   gst.SEEK_FLAG_FLUSH, pos);
        self.audio_sink.send_event(event);
        self.pipeline.set_state(gst.STATE_PLAYING);

    def isPlaying(self):
        return self.pipeline.get_state() == gst.STATE_PLAYING
    def isPaused(self):
        return self.pipeline.get_state() == gst.STATE_PAUSED
    def isStopped(self): 
        return self.pipeline.get_state() == gst.STATE_READY

    def setSourceTrack(self, track):
        assert(track);
        self._setSourceURI(track.path);
        self.player_widget.track_slider.setMaxValue(track.time);
    def _setSourceURI(self, uri):
        # Strip file:// since the file sink does not deal with it.
        if uri.find("file://") == 0:
            uri = uri[len("file://"):];
        self.src.set_property('location', uri)

    def getLength(self):
        return self.decoder.query(gst.QUERY_TOTAL,
                                  gst.FORMAT_TIME) / gst.SECOND;
    def getPosition(self):
        return self.audio_sink.query(gst.QUERY_POSITION,
                                     gst.FORMAT_TIME) / gst.SECOND;

    def _trackSliderPressed(self):
        self._stopPlayTick();
        self.pipeline.set_state(gst.STATE_PAUSED);
    def _trackSliderReleased(self):
        self._startPlayTick();
        loc = self.player_widget.track_slider.value();
        self.seek(loc);
    def _trackSliderMoved(self, val):
        loc = self.player_widget.track_slider.value();
        if loc >= 0:
            self.player_widget.displayTime(loc);


    def _startPlayTick(self):
        self.tick_timer.start(self.UPDATE_INTERVAL_MS, False);
        self._rewind_set = False;
    def _stopPlayTick(self):
        self.tick_timer.stop();
        self._rewind_set = False;

    def _tick(self):
        # Update the track position slider.
        len = self.getLength();
        pos = self.getPosition();
        if not self._rewind_set and pos >= 2:
            # When the track is 2 seconds in, hitting "previous" will
            # rewind the track, not go to the previous track.
            self._rewind_set = True;
            self._rewind_flag = True;
        assert(pos >= 0);
        self.player_widget.displayTime(pos);

    def _gst_eosCB(self, sink):
        # Neet to jump off the gst thread and onto Qt's.
        QTimer.singleShot(self._gap_delay, self._enqueueNext);
    def _enqueueNext(self):
        self.player_widget.displayTime(0);
        self.pipeline.set_state(gst.STATE_READY);
        self.emit(PYSIGNAL("audioComplete(int)"),
                  (self._playlist.getCurrentIndex(),));
        self._advancePlaylist();
        self.play();

    def _gst_errorCB(self, bin, element, error, debug):
        self.log.error("GStreamer error [%s]; bin [%s]; element [%s]; "\
                       "debug [%s]" %\
                       (str(error), str(bin), str(element), str(debug)));

    def _queueFullCB(self, queue, data):
        # TODO
        print "Queue Full CB"

