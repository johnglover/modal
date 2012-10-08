import numpy as np
from nose.tools import assert_almost_equals
import modal
import modal.detectionfunctions.pydetectionfunctions as cdf
import modal.detectionfunctions.mq as mq


class TestMQ(object):
    FLOAT_PRECISION = 5  # number of decimal places to check for accuracy
    max_peaks = 10

    def test_find_peaks(self):
        audio, sampling_rate, onsets = modal.get_audio_file('piano_G2.wav')
        frame_size = 1024
        window = np.hanning(frame_size)
        frame = audio[0:frame_size] * window
        spectrum = np.fft.rfft(frame)

        pd = mq.MQPeakDetection(self.max_peaks, sampling_rate, frame_size)
        py_peaks = pd.find_peaks(spectrum)
        py_peaks = [p.bin_number for p in py_peaks]

        mq_params = cdf.MQParameters()
        mq_params.max_peaks = self.max_peaks
        mq_params.frame_size = frame_size
        mq_params.num_bins = int(frame_size / 2) + 1
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
        assert len(py_peaks) == num_peaks

        current_peak = c_peaks
        for i in range(len(py_peaks)):
            assert py_peaks[i] == current_peak.peak.bin
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
        mq_params.num_bins = int(frame_size / 2) + 1
        mq_params.peak_threshold = 0.1
        mq_params.matching_interval = 200.0
        mq_params.fundamental = float(sampling_rate / frame_size)
        cdf.init_mq(mq_params)

        for i in range(num_frames):
            frame = audio[i * hop_size:(i * hop_size) + frame_size]
            spectrum = np.fft.rfft(frame * window)

            py_peaks = pd.find_peaks(spectrum)
            py_partial = pt.track_peaks(py_peaks)

            c_peaks = cdf.find_peaks(frame, mq_params)
            c_partial = cdf.track_peaks(c_peaks, mq_params)
            current_peak = c_partial

            current_peak = c_partial
            for peak in py_partial:
                if peak.prev_peak:
                    assert_almost_equals(peak.prev_peak.frequency,
                                         current_peak.peak.prev.frequency,
                                         places=self.FLOAT_PRECISION)
                else:
                    assert current_peak.peak.prev == None
                assert_almost_equals(peak.frequency,
                                     current_peak.peak.frequency,
                                     places=self.FLOAT_PRECISION)
                current_peak = current_peak.next

        cdf.destroy_mq(mq_params)
