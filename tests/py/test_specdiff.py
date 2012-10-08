import numpy as np
from nose.tools import assert_almost_equals
import modal

SpectralDifferenceODF = \
    modal.detectionfunctions.detectionfunctions.SpectralDifferenceODF
LPSpectralDifferenceODF = \
    modal.detectionfunctions.detectionfunctions.LPSpectralDifferenceODF

CSpectralDifferenceODF = \
    modal.detectionfunctions.pydetectionfunctions.SpectralDifferenceODF
CLPSpectralDifferenceODF = \
    modal.detectionfunctions.pydetectionfunctions.LPSpectralDifferenceODF


class TestODFs(object):
    FLOAT_PRECISION = 5  # number of decimal places to check for accuracy

    def test_py_c_equal(self):
        audio, sampling_rate, onsets = modal.get_audio_file('piano_G2.wav')
        audio = audio[0:4096]
        frame_size = 512
        hop_size = 512
        py_odf = SpectralDifferenceODF()
        py_odf.set_frame_size(frame_size)
        py_odf.set_hop_size(hop_size)
        c_odf = CSpectralDifferenceODF()
        c_odf.set_frame_size(frame_size)
        c_odf.set_hop_size(hop_size)
        # if necessary, pad the input signal
        if len(audio) % hop_size != 0:
            audio = np.hstack((
                audio, np.zeros(hop_size - (len(audio) % hop_size),
                                dtype=np.double)
            ))
        # get odf samples
        odf_size = len(audio) / hop_size
        py_samples = np.zeros(odf_size, dtype=np.double)
        c_samples = np.zeros(odf_size, dtype=np.double)
        py_odf.process(audio, py_samples)
        c_odf.process(audio, c_samples)

        assert len(py_samples) == len(c_samples)
        for i in range(len(py_samples)):
            assert_almost_equals(py_samples[i], c_samples[i],
                                 places=self.FLOAT_PRECISION)

    def test_py_c_equal_rt(self):
        audio, sampling_rate, onsets = modal.get_audio_file('piano_G2.wav')
        audio = audio[0:4096]
        frame_size = 256
        hop_size = 256
        py_odf = SpectralDifferenceODF()
        py_odf.set_frame_size(frame_size)
        py_odf.set_hop_size(hop_size)
        c_odf = CSpectralDifferenceODF()
        c_odf.set_frame_size(frame_size)
        c_odf.set_hop_size(hop_size)
        # if necessary, pad the input signal
        if len(audio) % hop_size != 0:
            audio = np.hstack((
                audio, np.zeros(hop_size - (len(audio) % hop_size),
                                dtype=np.double)
            ))
        # get odf samples
        audio_pos = 0
        while audio_pos <= len(audio) - frame_size:
            frame = audio[audio_pos:audio_pos + frame_size]
            py_odf_value = py_odf.process_frame(frame)
            c_odf_value = c_odf.process_frame(frame)
            assert_almost_equals(py_odf_value, c_odf_value,
                                 places=self.FLOAT_PRECISION)
            audio_pos += hop_size


class TestLPODFs(object):
    FLOAT_PRECISION = 5  # number of decimal places to check for accuracy
    order = 5

    def test_py_c_equal(self):
        audio, sampling_rate, onsets = modal.get_audio_file('piano_G2.wav')
        audio = audio[0:4096]
        frame_size = 512
        hop_size = 512
        py_odf = LPSpectralDifferenceODF()
        py_odf.set_frame_size(frame_size)
        py_odf.set_hop_size(hop_size)
        py_odf.set_order(self.order)
        c_odf = CLPSpectralDifferenceODF()
        c_odf.set_frame_size(frame_size)
        c_odf.set_hop_size(hop_size)
        c_odf.set_order(self.order)
        # if necessary, pad the input signal
        if len(audio) % hop_size != 0:
            audio = np.hstack((
                audio, np.zeros(hop_size - (len(audio) % hop_size),
                                dtype=np.double)
            ))
        # get odf samples
        odf_size = len(audio) / hop_size
        py_samples = np.zeros(odf_size, dtype=np.double)
        c_samples = np.zeros(odf_size, dtype=np.double)
        py_odf.process(audio, py_samples)
        c_odf.process(audio, c_samples)

        assert len(py_samples) == len(c_samples)
        for i in range(len(py_samples)):
            assert_almost_equals(py_samples[i], c_samples[i],
                                 places=self.FLOAT_PRECISION)

    def test_py_c_equal_rt(self):
        audio, sampling_rate, onsets = modal.get_audio_file('piano_G2.wav')
        audio = audio[0:4096]
        frame_size = 256
        hop_size = 256
        py_odf = LPSpectralDifferenceODF()
        py_odf.set_frame_size(frame_size)
        py_odf.set_hop_size(hop_size)
        c_odf = CLPSpectralDifferenceODF()
        c_odf.set_frame_size(frame_size)
        c_odf.set_hop_size(hop_size)
        # if necessary, pad the input signal
        if len(audio) % hop_size != 0:
            audio = np.hstack((
                audio, np.zeros(hop_size - (len(audio) % hop_size),
                                dtype=np.double)
            ))
        # get odf samples
        audio_pos = 0
        while audio_pos <= len(audio) - frame_size:
            frame = audio[audio_pos:audio_pos + frame_size]
            py_odf_value = py_odf.process_frame(frame)
            c_odf_value = c_odf.process_frame(frame)
            assert_almost_equals(py_odf_value, c_odf_value,
                                 places=self.FLOAT_PRECISION)
            audio_pos += hop_size
