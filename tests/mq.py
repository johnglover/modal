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

import modal
import modal.pydetectionfunctions as cdf 
import modal.mq as mq
import numpy as np
import unittest
import matplotlib.pyplot as plt

class TestMQ(unittest.TestCase):
    FLOAT_PRECISION = 5 # number of decimal places to check for accuracy
    max_peaks = 10
    
    def plot_py_pt(self): 
        audio, sampling_rate, onsets = modal.get_audio_file('piano_G2.wav')
        frame_size = 1024
        hop_size = 512
        pd = mq.MQPeakDetection(self.max_peaks, sampling_rate, frame_size)
        pd.return_type = mq.MQPeakDetection.RETURN_PEAKS
        pt = mq.MQPartialTracking(self.max_peaks)
        
        window = np.hanning(frame_size)
        frame1 = audio[0:frame_size] * window
        frame2 = audio[hop_size:frame_size+hop_size] * window
        spectrum1 = np.fft.rfft(frame1)
        spectrum2 = np.fft.rfft(frame2)
        peaks1 = pd.find_peaks(spectrum1)
        peaks2 = pd.find_peaks(spectrum2)
        partial1 = pt.track_peaks(peaks1)
        partial2 = pt.track_peaks(peaks2)

        for p in partial2:
            if p.prev_peak:
                freqs = [p.prev_peak.frequency, p.frequency]
                plt.plot(freqs, 'b-')
                plt.plot(freqs, 'ro')
            else:
                plt.plot([0.0, p.frequency], 'ro')
        plt.show()

    def plot_c_pt(self): 
        audio, sampling_rate, onsets = modal.get_audio_file('piano_G2.wav')
        frame_size = 1024
        hop_size = 512
        mq_params = cdf.MQParameters()
        mq_params.max_peaks = self.max_peaks
        mq_params.frame_size = frame_size
        mq_params.num_bins = int(frame_size/2) + 1
        mq_params.matching_interval = 100.0
        mq_params.fundamental = float(sampling_rate / frame_size)
        cdf.init_mq(mq_params)

        frame1 = audio[0:frame_size]
        frame2 = audio[hop_size:frame_size+hop_size]
        peaks1 = cdf.find_peaks(frame1, mq_params)
        peaks2 = cdf.find_peaks(frame2, mq_params)
        partial1 = cdf.track_peaks(peaks1, mq_params)
        partial2 = cdf.track_peaks(peaks2, mq_params)
        cdf.destroy_mq(mq_params)

        current = partial2
        while current and current.peak:
            if current.peak.prev:
                freqs = [current.peak.prev.frequency, current.peak.frequency]
                plt.plot(freqs, 'b-')
                plt.plot(freqs, 'ro')
            else:
                plt.plot([0.0, current.peak.frequency], 'ro')
            current = current.next
        plt.show()

    def test_find_peaks(self):
        audio, sampling_rate, onsets = modal.get_audio_file('piano_G2.wav')
        frame_size = 1024
        hop_size = 512
        window = np.hanning(frame_size)
        frame = audio[0:frame_size] * window
        spectrum = np.fft.rfft(frame)
        
        pd = mq.MQPeakDetection(self.max_peaks, sampling_rate, frame_size)
        py_peaks = pd.find_peaks(spectrum)
        py_peaks = [p.bin_number for p in py_peaks]

        mq_params = cdf.MQParameters()
        mq_params.max_peaks = self.max_peaks
        mq_params.frame_size = frame_size
        mq_params.num_bins = int(frame_size/2) + 1
        mq_params.peak_threshold = 0.1
        mq_params.matching_interval = 100.0
        mq_params.fundamental = float(sampling_rate / frame_size)
        cdf.init_mq(mq_params)
        c_peaks = cdf.find_peaks(audio[0:frame_size], mq_params)
        cdf.destroy_mq(mq_params)

        num_peaks = 0
        current_peak = c_peaks
        while current_peak:
            num_peaks += 1
            current_peak = current_peak.next
        self.assertEquals(len(py_peaks), num_peaks)

        current_peak = c_peaks
        for i in range(len(py_peaks)):
            self.assertEquals(py_peaks[i], current_peak.peak.bin)
            current_peak = current_peak.next
        cdf.delete_peak_list(c_peaks)

    def test_track_peaks(self):
        audio, sampling_rate, onsets = modal.get_audio_file('piano_G2.wav')
        frame_size = 1024
        hop_size = 512
        num_frames = 9
        window = np.hanning(frame_size)

        pd = mq.MQPeakDetection(self.max_peaks, sampling_rate, frame_size)
        pt = mq.MQPartialTracking(self.max_peaks)

        mq_params = cdf.MQParameters()
        mq_params.max_peaks = self.max_peaks
        mq_params.frame_size = frame_size
        mq_params.num_bins = int(frame_size/2) + 1
        mq_params.peak_threshold = 0.1
        mq_params.matching_interval = 200.0
        mq_params.fundamental = float(sampling_rate / frame_size)
        cdf.init_mq(mq_params)

        for i in range(num_frames):
            frame = audio[i*hop_size:(i*hop_size)+frame_size]
            spectrum = np.fft.rfft(frame*window)

            py_peaks = pd.find_peaks(spectrum)
            py_partial = pt.track_peaks(py_peaks)

            c_peaks = cdf.find_peaks(frame, mq_params)
            c_partial = cdf.track_peaks(c_peaks, mq_params)
            current_peak = c_partial

            current_peak = c_partial
            for peak in py_partial:
                if peak.prev_peak:
                    self.assertAlmostEquals(peak.prev_peak.frequency, current_peak.peak.prev.frequency,
                                            places=self.FLOAT_PRECISION)
                else:
                    self.assertEquals(current_peak.peak.prev, None)
                self.assertAlmostEquals(peak.frequency, current_peak.peak.frequency,
                                        places=self.FLOAT_PRECISION)
                current_peak = current_peak.next

        cdf.destroy_mq(mq_params)

if __name__ == '__main__':
    suite = unittest.TestSuite()
    #suite.addTest(TestMQ('plot_py_pt'))
    #suite.addTest(TestMQ('plot_c_pt'))
    suite.addTest(TestMQ('test_find_peaks'))
    suite.addTest(TestMQ('test_track_peaks'))
    unittest.TextTestRunner().run(suite)

