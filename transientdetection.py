# Copyright (c) 2010 John Glover, National University of Ireland, Maynooth
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import transients.onsetdetection as od
import numpy as np
from scipy.io.wavfile import read
import matplotlib.pyplot as plt
import time
        
def plot_det_func(det_func, hop_size):
    df = np.zeros(len(det_func) * hop_size)
    sample_offset = 0
    for frame in det_func:
        df[sample_offset:sample_offset+hop_size] = frame
        sample_offset += hop_size
    plt.plot(df, '0.4')
    
def plot_det_func_peaks(peaks, hop_size):
    for i in range(len(peaks)):
        plt.plot([peaks[i].location * hop_size], [peaks[i].value], 'ro')
    
def plot_transients(transient_markers):
    for m in transient_markers:
        plt.axvspan(m.start, m.end, facecolor='g', alpha=0.25)


class TransientMarker(object):
    def __init__(self):
        self.start = 0
        self.end = 0
        self.odf_peak = None
    
    
class TransientDetection(od.OnsetDetection):
    # transient is a fixed size, given as a number of frames, overlapping
    # by self.hop_size samples.
    DURATION_FIXED = 0
    # transient is taken as being the area from the onset to the point where
    # the detection function drops to the threshold value. Threshold can be fixed
    # or adaptive (moving)
    DURATION_THRESHOLD = 1
    
    def __init__(self):
        od.OnsetDetection.__init__(self)
        # onset detection parameters
        self.odf = od.LinearPredictionODF()
        self.frame_size = 512
        self.hop_size = self.frame_size/4
        self.smooth_type = od.OnsetDetectionFunction.SMOOTH_LPF
        self.threshold_type = self.THRESHOLD_FIXED
        self.threshold = 0.1
        self.peak_size = 15
        self.onset_location = self.ONSET_AT_THRESHOLD
        # transient duration parameters
        self.duration_type = self.DURATION_THRESHOLD
        self.transient_size = 2048 # in samples
        self.markers = []
        
    def find_transients(self, signal):
        self.markers = []
        self.find_onsets(signal)
        for onset_num, onset in enumerate(self.onsets):
            m = TransientMarker()
            m.odf_peak = onset.odf_peak
            # if it's not the first transient, make sure that the earliest
            # transient start time is > the last transient end time
            if self.markers:
                m.start = max(onset.location,
                              self.markers[-1].end)
            else:
                m.start = onset.location
            if self.duration_type == self.DURATION_FIXED:
                # if there is enough signal left, transient is just a fixed duration
                # not enough signal if we reach the end of the signal or we reach the next onset
                # if so, transient is the remainder of the signal
                m.end = min(m.start + self.transient_size, 
                            m.start + (signal.size - m.start))
            elif self.duration_type == self.DURATION_THRESHOLD:
                # find the next part of the detection function that is <= peak threshold
                # stop if we reach the next onset or the end of the signal
                i = onset.odf_peak.location
                next_onset_loc = self.det_func.size
                if onset_num < len(self.onsets) - 1:
                    next_onset_loc = self.onsets[onset_num+1].odf_location
                while i < next_onset_loc:
                    if self.det_func[i] <= onset.odf_peak.threshold_at_peak:
                        break
                    i += 1
                m.end = i * self.hop_size
            else:
                raise Exception("Invalid transient duration type: " + str(self.duration_type))                      
            self.markers.append(m)
        return self.markers
    
if __name__ == "__main__":
    start_time = time.time()
    audio_in_data = read('examples/audio/piano.wav')
    audio_in = np.asarray(audio_in_data[1], np.float32) / 32768.0
    
    td = TransientDetection()
    td.find_transients(audio_in)
    
    print "Running time:", time.time() - start_time, "seconds"
    
    plt.subplot(3, 1, 1)
    plt.plot(audio_in, '0.4')
    plt.subplot(3, 1, 2)
    plot_det_func(td.det_func, td.hop_size)
    plot_det_func_peaks(td.peaks, td.hop_size)
    plt.subplot(3, 1, 3)
    plt.plot(audio_in, '0.4')
    plot_transients(td.markers)
    plt.show()