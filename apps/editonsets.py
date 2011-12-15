#!/usr/bin/env python

from PyQt4 import QtGui, QtCore
import os
import numpy as np
import h5py
import sndobj
from modal.ui.editonsetsui import Ui_MainWindow
# todo:
# - warn if saving over a file that already exists
# - add ability to delete files from database
# - add ability to set the texture of a file
# - fix bug displaying the end of a file when zoomed in

class AudioPlayer(QtCore.QObject):
    def __init__(self):
        QtCore.QObject.__init__(self)
        self._audio = None
        self._audio_pos = 0
        self._frame_size = 256
        self._frame = np.zeros(self._frame_size, dtype=np.float32)
        self._sndobj = sndobj.SndObj()
        self._output = sndobj.SndRTIO(2, sndobj.SND_IO)
        self._output.SetOutput(1, self._sndobj)
        self._output.SetOutput(2, self._sndobj)
        self._processing_thread = sndobj.SndThread()
        self._processing_thread.AddObj(self._sndobj)
        self._processing_thread.AddObj(self._output, sndobj.SNDIO_OUT)
        self._processing_thread.SetProcessCallback(self._update, ())
        
    def _update(self, data):
        self._update_audio()
        # emit current sample position
        self.emit(QtCore.SIGNAL("sampleChanged(int)"), self._audio_pos)
        
    def _update_audio(self):
        if self._audio_pos <= len(self._audio) - self._frame_size:
            self._frame = self._audio[self._audio_pos:self._audio_pos+self._frame_size]*32768
            self._audio_pos += self._frame_size
        else:
            self._frame = np.zeros(self._frame_size, dtype=np.float32)
        self._sndobj.PushIn(self._frame)
    
    def start(self):
        if self._processing_thread.GetStatus() == 0:
            self._processing_thread.ProcOn()
        
    def stop(self):
        if self._processing_thread.GetStatus() == 1:
            self._processing_thread.ProcOff()
        
    def set_audio(self, audio):
        self._audio = audio
        
    def set_play_pos(self, pos):
        self._audio_pos = pos
        
    def reset(self):
        self._audio_pos = 0
        self._frame = np.zeros(self._frame_size, dtype=np.float32)


class InteractiveGraphicsPixmapItem(QtGui.QGraphicsPixmapItem):
    def __init__(self):
        QtGui.QGraphicsPixmapItem.__init__(self)
        self.emitter = QtCore.QObject()
        
    def mousePressEvent(self, event):
        self.emitter.emit(QtCore.SIGNAL("mousePressedX(int)"), int(event.pos().x()))


class EditOnsetsApp(QtGui.QMainWindow):
    NEW_ONSET = 0
    MOVE_ONSET = 1
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.centralwidget.setFocus()
        # connect buttons
        self.connect(self.ui.import_audio, QtCore.SIGNAL("clicked()"), self.import_audio)
        self.connect(self.ui.save, QtCore.SIGNAL("clicked()"), self.save_to_db)
        self.connect(self.ui.play, QtCore.SIGNAL("clicked()"), self.play)
        self.connect(self.ui.stop, QtCore.SIGNAL("clicked()"), self.stop)
        self.connect(self.ui.back, QtCore.SIGNAL("clicked()"), self.back)
        self.connect(self.ui.zoom_in, QtCore.SIGNAL("clicked()"), self.zoom_in)
        self.connect(self.ui.zoom_out, QtCore.SIGNAL("clicked()"), self.zoom_out)
        self.connect(self.ui.new_onset, QtCore.SIGNAL("clicked()"), self.new_onset)
        self.connect(self.ui.move_onset, QtCore.SIGNAL("clicked()"), self.move_onset)
        self.connect(self.ui.delete_onset, QtCore.SIGNAL("clicked()"), self.delete_onset)
        # handle changes to the current onset number
        self.connect(self.ui.onset_number, QtCore.SIGNAL("valueChanged(int)"), 
                     self.onset_number_changed)
        # which onset tool is selected
        self.onset_tool = self.NEW_ONSET
        # main drawing scene
        self.scene = QtGui.QGraphicsScene()
        self.ui.audio_display.setScene(self.scene)
        self.audio_width = 5000
        self.scale = 500
        # setup for drawing the ruler
        self.ruler_height = 25
        self.ruler_image = QtGui.QImage(self.audio_width, 
                                        self.ruler_height, 
                                        QtGui.QImage.Format_RGB32)
        self.ruler_item = InteractiveGraphicsPixmapItem()
        self.scene.addItem(self.ruler_item)
        self.ruler_item.moveBy(0, -self.ruler_height)
        # handle mouse clicks on the ruler
        self.connect(self.ruler_item.emitter, QtCore.SIGNAL("mousePressedX(int)"),
                     self.ruler_clicked)
        # setup for drawing the audio waveform 
        self.audio_height = self.ui.audio_display.height() - self.ruler_height - 20
        self.audio_image = QtGui.QImage(self.audio_width, 
                                        self.audio_height, 
                                        QtGui.QImage.Format_RGB32)
        self.audio_item = InteractiveGraphicsPixmapItem()
        self.scene.addItem(self.audio_item)
        # handle mouse clicks on the audio waveform
        self.connect(self.audio_item.emitter, QtCore.SIGNAL("mousePressedX(int)"),
                     self.audio_clicked)
        # setup for drawing the current play position
        self.play_pos_image = QtGui.QImage(20, self.ruler_height + self.audio_height, 
                                           QtGui.QImage.Format_ARGB32_Premultiplied)
        self.play_pos_item = QtGui.QGraphicsPixmapItem()
        self.scene.addItem(self.play_pos_item)
        self.onset_items = []
        # load database
        self.db_path = "../data/onsets.hdf5"
        self.db = h5py.File(self.db_path)
        self._update_db_info()
        self.connect(self.ui.db_files, QtCore.SIGNAL("itemSelectionChanged()"), self.load_audio)
        # analysis info
        self.audio = np.array([], dtype=np.float32)
        self.sampling_rate = 44100
        self.current_onset = 0
        self.moving_onset = False
        self.onsets = np.array([], dtype=np.int32)
        # audio player
        self.audio_player = AudioPlayer()
        self.audio_player.set_audio(self.audio)
        self.connect(self.audio_player, QtCore.SIGNAL("sampleChanged(int)"), 
                     self.audio_sample_changed)
        
    def closeEvent(self, event):
        self.db.close()
        
    def keyPressEvent(self, event):
        if event.text() == " ":
            self.back()
        
    def _update_db_info(self):
        self.ui.db_files.clear()
        num_onsets = 0
        for sound in self.db:
            item = QtGui.QListWidgetItem(sound)
            self.ui.db_files.addItem(item)
            try:
                num_onsets += len(self.db[sound].attrs['onsets'])
            except:
                # if no onsets, just ignore
                pass
        self.ui.num_files.setText(str(len(self.db)))
        self.ui.num_onsets_in_db.setText(str(num_onsets))

    def import_audio(self):
        from scipy.io.wavfile import read
        file_path = QtGui.QFileDialog.getOpenFileName(self, 
                                                      'Import Audio File', '',
                                                      'Wav files (*.wav)')
        if file_path:
            file_path = str(file_path)
            audio_data = read(file_path)
            # convert to float between -1 and 1
            self.audio = np.asarray(audio_data[1], np.float32) / 32768.0
            self.audio_player.set_audio(self.audio)
            self.set_play_pos(0)
            self.audio_player.set_play_pos(0)
            self.sampling_rate = audio_data[0]
            self.onsets = np.array([], dtype=np.int32)
            # render
            self._render()
            self.ui.size.setText(str(len(self.audio)))
            self.ui.sampling_rate.setText(str(self.sampling_rate))
            self.ui.num_onsets.setText("0")
            # set default database path
            self.ui.db_path.setEnabled(True)
            self.ui.db_path.setText(os.path.basename(file_path))
            # enable new onset and save buttons
            if not self.ui.new_onset.isEnabled():
                self.ui.new_onset.setEnabled(True)
            if not self.ui.save.isEnabled():
                self.ui.save.setEnabled(True)
            
    def load_audio(self):
        if not self.ui.db_files.selectedItems():
            return
        selected_item = str(self.ui.db_files.selectedItems()[0].text())
        # compare selected to current file. If it's different, update
        current_name = self.ui.db_path.text()
        if current_name:
            current_name = str(current_name)
            if current_name == selected_item:
                return
        # set audio
        self.audio = np.asarray(self.db[selected_item], dtype=np.float32)
        self.audio_player.set_audio(self.audio)
        self.ui.size.setText(str(len(self.audio)))
        # set sampling rate
        self.sampling_rate = int(self.db[selected_item].attrs['sampling_rate'])
        self.ui.sampling_rate.setText(str(self.sampling_rate))
        # set onsets
        if len(self.db[selected_item].attrs['onsets']):
            self.onsets = self.db[selected_item].attrs['onsets']
        else:
            self.onsets = []
        self.current_onset = 0
        self.ui.num_onsets.setText(str(len(self.onsets)))
        # render
        self.set_play_pos(0)
        self.audio_player.set_play_pos(0)
        self._render()
        # set name
        self.ui.db_path.setEnabled(True)
        self.ui.db_path.setText(selected_item)
        # set type
        self.ui.type.setCurrentIndex(
            self.ui.type.findText(self.db[selected_item].attrs['type']))
        # set texture
        self.ui.texture.setCurrentIndex(
            self.ui.texture.findText(self.db[selected_item].attrs['texture']))
        # set comments
        self.ui.comments.setPlainText(self.db[selected_item].attrs['comments'])
        # enable new onset and save buttons
        self.ui.new_onset.setEnabled(True)
        self.ui.save.setEnabled(True)
        # if there are onsets, update the onset number selection and
        # the move onset button
        if len(self.onsets):
            self.ui.onset_number.setMaximum(len(self.onsets))
            self.ui.onset_number.setValue(self.current_onset+1)
            self.ui.onset_number.setEnabled(True)
            self.ui.move_onset.setEnabled(True)
        else:
            self.ui.onset_number.setEnabled(False)
            self.ui.onset_number.setMaximum(1)
            self.ui.move_onset.setEnabled(False)
                
    def save_to_db(self):
        name = self.ui.db_path.text()
        if name:
            name = str(name)
            self.current_onset = 0
            if name in self.db:
                # delete existing entry
                del self.db[name]
            self.db.create_dataset(name, data=self.audio)
            if len(self.onsets):
                self.db[name].attrs['onsets'] = self.onsets
            else:
                self.db[name].attrs['onsets'] = 0
            self.db[name].attrs['sampling_rate'] = self.sampling_rate
            self.db[name].attrs['type'] = str(self.ui.type.currentText())
            self.db[name].attrs['texture'] = str(self.ui.texture.currentText())
            self.db[name].attrs['comments'] = str(self.ui.comments.toPlainText())
            self._update_db_info()
            
    def play(self):
        self.audio_player.start()
        
    def stop(self):
        self.audio_player.stop()
        
    def back(self):
        self.set_play_pos(0)
        self.audio_player.reset()
        
    def zoom_in(self):
        if (self.audio_width + self.scale) < 10000:
            self.audio_width += self.scale
            self._render()
        
    def zoom_out(self):
        if (self.audio_width - self.scale) > 0:
            self.audio_width -= self.scale
            self._render()
            
    def new_onset(self):
        self.onset_tool = self.NEW_ONSET
        self.ui.new_onset.setChecked(True)
        self.ui.move_onset.setChecked(False)
        
    def _new_onset(self, location):
        # add 1 to the onset array length
        self.onsets.resize(len(self.onsets)+1)
        # add the new onset
        self.onsets[-1] = self._width_to_sample(location)
        # update the current onset location
        self.onsets.sort()
        self.current_onset = self._onset_num_with_value(self._width_to_sample(location))
        # update the GUI current onset selector
        self.ui.onset_number.setMaximum(len(self.onsets))
        self.ui.onset_number.setValue(self.current_onset+1)
        self.ui.num_onsets.setText(str(len(self.onsets)))
        # enable onset buttons
        self.ui.onset_number.setEnabled(True)
        self.ui.move_onset.setEnabled(True)
        # render onsets
        self._render_onsets()
        
    def move_onset(self):
        self.onset_tool = self.MOVE_ONSET
        self.ui.new_onset.setChecked(False)
        self.ui.move_onset.setChecked(True)
        
    def _move_onset(self, location):
        self.onsets[self.current_onset] = self._width_to_sample(location)
        self.onsets.sort()
        self.current_onset = self._onset_num_with_value(self._width_to_sample(location))
        self.ui.onset_number.setValue(self.current_onset+1)
        self._render_onsets()
        
    def delete_onset(self):
        self.onsets = np.delete(self.onsets, self.current_onset)
        if self.current_onset > 0:
            self.current_onset -= 1
        self.ui.onset_number.setMaximum(len(self.onsets))
        self.ui.onset_number.setValue(self.current_onset+1)
        self.ui.num_onsets.setText(str(len(self.onsets)))
        self._render_onsets()
            
    def onset_number_changed(self, value):
        self.current_onset = value -1
        self._render_onsets()
        
    def set_play_pos(self, x):
        self.play_pos = x
        self.play_pos_item.setPos(x-10, -self.ruler_height)
        # centre view on play position
#        w = self.ui.audio_display.width()/2
#        if x > w and x < self.ui.audio_display.horizontalScrollBar().maximum():
#            self.ui.audio_display.horizontalScrollBar().setSliderPosition(x-w)
        
    def audio_sample_changed(self, sample):
        self.set_play_pos(self._sample_to_width(sample))
        
    def ruler_clicked(self, x):
        self.set_play_pos(x)
        self.audio_player.set_play_pos(self._width_to_sample(x))
        
    def audio_clicked(self, x):
        if self.onset_tool == self.NEW_ONSET:
            self._new_onset(x)
        elif self.onset_tool == self.MOVE_ONSET:
            self._move_onset(x)
        
    def _render_ruler(self):
        # background
        self.ruler_image.fill(QtGui.qRgb(90, 90, 90))
        # setup painter for drawing the ruler lines
        p = QtGui.QPainter()
        p.begin(self.ruler_image)
        p.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(133, 133, 133)), 1, 
                            QtCore.Qt.SolidLine))
        # interval = how many pixels for 10ms of audio
        interval = int((441.0 / max(1, len(self.audio)/self.audio_width)) + 0.5)
        for i in range(1, min(self.audio_width, len(self.audio))):
            if i % (interval*10) == 0:
                p.drawLine(i, 0, i, self.ruler_height)
            elif i % interval == 0:
                p.drawLine(i, self.ruler_height/2, i, self.ruler_height)
        p.end()
        self.ruler_item.setPixmap(QtGui.QPixmap.fromImage(self.ruler_image))
        
    def _onset_num_with_value(self, value):
        # return the number of the onset with the given value
        for i in range(len(self.onsets)):
            if self.onsets[i] == value:
                return i
        return 0
            
    def _sample_to_height(self, sample):
        # receives a float between -1 and 1, scales it to an int between
        # self.audio_height and 0
        return (int((sample + 1.0) * self.audio_height/2) - self.audio_height) * -1
    
    def _sample_to_width(self, sample):
        # receive a sample position between 0 and len(self.audio) 
        # returns the corresponding pixel position between 0 and self.audio_width
        if len(self.audio) < self.audio_width:
            return sample
        else:
            return int(sample / (len(self.audio)/self.audio_width))
        
    def _width_to_sample(self, pixel):
        # receive a pixel x-axis coordinate between 0 and self.audio_width
        # return a sample position between 0 and len(self.audio)
        if len(self.audio) < self.audio_width:
            return pixel
        else:
            return pixel * int(len(self.audio)/self.audio_width)
    
    def _render_audio(self):
        self.audio_image.fill(QtGui.qRgb(255, 255, 255))
        sample = 0
        step = max(1, len(self.audio)/self.audio_width)
        last_height = self.audio_height/2
        
        p = QtGui.QPainter()
        p.begin(self.audio_image)
        p.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(127, 127, 127)), 1, 
                            QtCore.Qt.SolidLine))

        for i in range(1, min(self.audio_width, len(self.audio))):
            h = self._sample_to_height(self.audio[sample])
            p.drawLine(i-1, last_height, i, h)
            last_height = h
            sample += step
        p.end()
        self.audio_item.setPixmap(QtGui.QPixmap.fromImage(self.audio_image))
        
    def _clear_onsets(self):
        for item in self.onset_items:
            self.scene.removeItem(item)
        self.onset_items = []
    
    def _render_onsets(self):
        self._clear_onsets()
        for i, onset in enumerate(self.onsets):
            im = QtGui.QImage(2, self.audio_height, QtGui.QImage.Format_RGB32)
            if i == self.current_onset:
                im.fill(QtGui.qRgb(158, 0, 0))
            else:
                im.fill(QtGui.qRgb(96, 158, 127))
            item = QtGui.QGraphicsPixmapItem()
            item.setPixmap(QtGui.QPixmap.fromImage(im))
            item.setPos(self._sample_to_width(onset), 0)
            self.scene.addItem(item)
            self.onset_items.append(item)
    
    def _render_play_pos(self):
        p = QtGui.QPainter()
        p.begin(self.play_pos_image)
        # draw play position arrow
        p.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(0, 0, 0)), 1, 
                            QtCore.Qt.SolidLine))
        p.setBrush(QtGui.QBrush(QtGui.QColor(196, 232, 163)))
        p.drawPie(QtCore.QRect(0, self.ruler_height/2, 20, self.ruler_height), 60*16, 60*16)
        # draw play line
        p.setPen(QtGui.QPen(QtGui.QBrush(QtGui.QColor(107, 135, 165)), 2, 
                            QtCore.Qt.SolidLine))
        p.drawLine(10, self.ruler_height, 10, self.audio_height+self.ruler_height)
        p.end()
        self.play_pos_item.setPixmap(QtGui.QPixmap.fromImage(self.play_pos_image))
            
    def _render(self):
        self._render_ruler()
        self._render_audio()
        self._render_onsets()
        self._render_play_pos()
        self.ui.audio_display.horizontalScrollBar().setMinimum(0)
#        self.ui.audio_display.horizontalScrollBar().setMaximum(self.audio_width)
 
                
if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    edit_onsets = EditOnsetsApp()
    edit_onsets.show()
    sys.exit(app.exec_())
