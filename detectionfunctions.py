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

import spectralprocessing as sp
import mq
import linearprediction as lp
import stats
import filter
import numpy as np

class OnsetDetectionFunction(object):
    SMOOTH_NONE = 0
    SMOOTH_MOVING_AVERAGE = 1  # Moving average filter
    SMOOTH_SAVITZKY_GOLAY = 2  # Savitzky-Golay algorithm
    SMOOTH_LPF = 3  # low-pass filter
    
    def __init__(self):
        self.det_func = np.array([])
        self._sampling_rate = 44100
        self._frame_size = 512
        self._hop_size = 256 
        self.smooth_type = self.SMOOTH_NONE
        self.smooth_window = 5
        self.lpf_cutoff = 0.15
        self.lpf_order = 101

    sampling_rate = property(lambda self: self.get_sampling_rate(),
                             lambda self, x: self.set_sampling_rate(x))

    frame_size = property(lambda self: self.get_frame_size(),
                          lambda self, x: self.set_frame_size(x))

    hop_size = property(lambda self: self.get_hop_size(),
                        lambda self, x: self.set_hop_size(x))

    def get_sampling_rate(self):
        return self._sampling_rate

    def set_sampling_rate(self, sampling_rate):
        self._sampling_rate = sampling_rate

    def get_frame_size(self):
        return self._frame_size

    def set_frame_size(self, frame_size):
        self._frame_size = frame_size

    def get_hop_size(self):
        return self._hop_size

    def set_hop_size(self, hop_size):
        self._hop_size = hop_size
    
    def _smooth(self, signal):
        if self.smooth_type == self.SMOOTH_MOVING_AVERAGE:
            return stats.moving_average(signal, self.smooth_window)
        elif self.smooth_type == self.SMOOTH_SAVITZKY_GOLAY:
            return stats.savitzky_golay(signal, self.smooth_window)
        elif self.smooth_type == self.SMOOTH_LPF:
            return filter.lpf(signal, self.lpf_order, self.lpf_cutoff)
        # default action is not to smooth
        return signal 

    def process_frame(self, frame):
        return 0.0
        
    def process(self, signal):
        # pad the input signal if necessary
        if len(signal) % self.hop_size != 0:
            signal = np.hstack((signal, np.zeros(self.hop_size - (len(signal) % self.hop_size))))

        # get a list of values for each frame
        odf = []
        sample_offset = 0
        while sample_offset + self.frame_size <= len(signal):
            frame = signal[sample_offset:sample_offset + self.frame_size]
            odf.append(self.process_frame(frame))
            sample_offset += self.hop_size
        self.det_func = np.array(odf)

        # perform any post-processing on the ODF, such as smoothing or normalisation
        self.post_process()
        return self.det_func

    def post_process(self):
        self.det_func = stats.normalise(self.det_func)
    
    def smooth_type_string(self):
        if self.smooth_type == self.SMOOTH_MOVING_AVERAGE:
            "moving_average"
        elif self.smooth_type == self.SMOOTH_SAVITZKY_GOLAY:
            "savitzky_golay"
        elif self.smooth_type == self.SMOOTH_LPF:
            "lpf"
        elif self.smooth_type == self.SMOOTH_NONE:
            return "none"
        else:
            return "Unknown"
        

class EnergyODF(OnsetDetectionFunction):
    def __init__(self):
        OnsetDetectionFunction.__init__(self)
        self.prev_energy = 0.0

    def process_frame(self, frame):
        energy = 0.0
        for sample in frame:
            energy += (sample * sample)
        diff = abs(energy - self.prev_energy)
        self.prev_energy = energy
        return diff


class SpectralDifferenceODF(OnsetDetectionFunction):
    def __init__(self):
        OnsetDetectionFunction.__init__(self)
        self.window = np.hanning(self.frame_size)
        self.num_bins = (self.frame_size/2) + 1
        self.prev_amps = np.zeros(self.num_bins)

    def set_frame_size(self, frame_size):
        self._frame_size = frame_size
        self.window = np.hanning(frame_size)
        self.num_bins = (frame_size/2) + 1
        self.prev_amps = np.zeros(self.num_bins)

    def process_frame(self, frame):
        # fft
        spectrum = np.fft.rfft(frame*self.window)
        # calculate spectral difference for each bin
        sum = 0.0
        for bin in range(self.num_bins):
            real = spectrum[bin].real
            imag = spectrum[bin].imag
            amp = np.sqrt((real*real) + (imag*imag))
            sum += np.abs(amp - self.prev_amps[bin])
            self.prev_amps[bin] = amp
        return sum


class ComplexODF(OnsetDetectionFunction):
    def __init__(self):
        OnsetDetectionFunction.__init__(self)
        self.window = np.hanning(self.frame_size)
        self.num_bins = (self.frame_size/2) + 1
        self.prev_mags = np.zeros(self.num_bins)
        self.prev_phases = np.zeros(self.num_bins)
        self.prev_phases2 = np.zeros(self.num_bins)
        self.prediction = np.zeros(self.num_bins, dtype=np.complex)

    def set_frame_size(self, frame_size):
        self._frame_size = frame_size
        self.window = np.hanning(frame_size)
        self.num_bins = (frame_size/2) + 1
        self.prev_mags = np.zeros(self.num_bins)
        self.prev_phases = np.zeros(self.num_bins)
        self.prev_phases2 = np.zeros(self.num_bins)
        self.prediction = np.zeros(self.num_bins, dtype=np.complex)

    def process_frame(self, frame):
        # fft
        spectrum = np.fft.rfft(frame*self.window)
        # calculate complex difference for each bin
        cd = 0.0
        for bin in range(self.num_bins):
            # magnitude prediction is just the previous magnitude
            # phase prediction is the previous phase plus the difference between 
            # the previous two frames
            predicted_phase = (2 * self.prev_phases[bin]) - self.prev_phases2[bin]
            # bring it into the range +- pi
            predicted_phase -= 2 * np.pi * np.round(predicted_phase / (2*np.pi))
            # convert back into the complex domain to calculate stationarities
            self.prediction[bin] = sp.toRectangular(self.prev_mags[bin], predicted_phase)
            # get stationarity measures in the complex domain
            real = (self.prediction[bin].real - spectrum[bin].real)
            real = real*real
            imag = (self.prediction[bin].imag - spectrum[bin].imag)
            imag = imag*imag
            cd += np.sqrt(real + imag)
            # update previous phase info for the next frame
            self.prev_phases2[bin] = self.prev_phases[bin]
            self.prev_mags[bin], self.prev_phases[bin] = sp.toPolar(spectrum[bin].real,
                                                                    spectrum[bin].imag)
        return cd


class LinearPredictionODF(OnsetDetectionFunction):
    AUTOCORRELATION = 0
    BURG = 1
    
    def __init__(self):
        OnsetDetectionFunction.__init__(self)
        self._order = 5
        self.method = self.BURG

    order = property(lambda self: self.get_order(),
                     lambda self, x: self.set_order(x))

    def get_order(self):
        return self._order

    def set_order(self, order):
        self._order = order
 
    def get_coefs(self, samples, order):
        if self.method == self.AUTOCORRELATION:
            return lp.autocorrelation(samples, order)
        elif self.method == self.BURG:
            return lp.burg(samples, order)
        else:
            raise Exception("Unknown method specified for finding linear prediction coefficients")
        
    def get_prediction(self, samples, order=None):
        if order:
            return lp.predict(samples, self.get_coefs(samples, order), 1)[0]
        return lp.predict(samples, self.get_coefs(samples, self.order), 1)[0]
    
    
class LPEnergyODF(LinearPredictionODF):
    def __init__(self):
        LinearPredictionODF.__init__(self)
        self.prev_values = np.zeros(self.order)

    def process_frame(self, frame):
        energy = 0.0
        for sample in frame:
           energy += (sample * sample)
        odf = abs(energy - self.get_prediction(self.prev_values))
        self.prev_values = np.hstack((self.prev_values[1:], energy))
        return odf

            
class LPSpectralDifferenceODF(LinearPredictionODF):
    def __init__(self):
        LinearPredictionODF.__init__(self)
        self.window = np.hanning(self.frame_size)
        self.num_bins = (self.frame_size/2) + 1
        self.prev_amps = np.zeros((self.order + 1, self.num_bins))

    def set_frame_size(self, frame_size):
        self._frame_size = frame_size
        self.window = np.hanning(frame_size)
        self.num_bins = (frame_size/2) + 1
        self.prev_amps = np.zeros((self.order + 1, self.num_bins))

    def process_frame(self, frame):
        # fft
        spectrum = np.fft.rfft(frame*self.window)
        sum = 0.0
        for bin in range(self.num_bins):
            real = spectrum[bin].real
            imag = spectrum[bin].imag
            amp = np.sqrt((real*real) + (imag*imag))
            samples = self.prev_amps[0:self.order,bin]
            sum += np.abs(self.get_prediction(samples) - amp)
            self.prev_amps[-1][bin] = amp
        # move prev amps back 1 frame
        self.prev_amps = np.vstack((self.prev_amps[1:], np.zeros(self.num_bins)))
        return sum


class LPComplexODF(LinearPredictionODF):
    def __init__(self):
        LinearPredictionODF.__init__(self)
        self.window = np.hanning(self.frame_size)
        self.num_bins = (self.frame_size/2) + 1
        self.prev_frame = np.zeros(self.num_bins, dtype=np.complex)
        self.distances = np.zeros((self.order + 1, self.num_bins))

    def set_frame_size(self, frame_size):
        self._frame_size = frame_size
        self.window = np.hanning(frame_size)
        self.num_bins = (frame_size/2) + 1
        self.prev_frame = np.zeros(self.num_bins, dtype=np.complex)
        self.distances = np.zeros((self.order + 1, self.num_bins))

    def process_frame(self, frame):
        # fft
        spectrum = np.fft.rfft(frame*self.window)
        # calculate complex differences    
        sum = 0.0
        for bin in range(self.num_bins):
           distance = np.sqrt((spectrum[bin].real-self.prev_frame[bin].real)**2 +
                              (spectrum[bin].imag-self.prev_frame[bin].imag)**2)
           samples = self.distances[0:self.order,bin]
           sum += np.abs(self.get_prediction(samples) - distance)
           self.distances[-1][bin] = distance
           self.prev_frame[bin] = spectrum[bin]
        self.distances = np.vstack((self.distances[1:], np.zeros(self.num_bins)))
        return sum


class PeakODF(OnsetDetectionFunction):
    def __init__(self):
        OnsetDetectionFunction.__init__(self)
        self._max_peaks = 10
        self.pd = mq.MQPeakDetection(self._max_peaks, self._sampling_rate, self._frame_size)
        self.pt = mq.MQPartialTracking(self._max_peaks)
        self.window = np.hanning(self.frame_size)
        self.num_bins = (self.frame_size/2) + 1

    max_peaks = property(lambda self: self.get_max_peaks(),
                         lambda self, x: self.set_max_peaks(x))

    def get_max_peaks(self):
        return self._max_peaks

    def set_max_peaks(self, max_peaks):
        self._max_peaks = max_peaks
        self.pd = mq.MQPeakDetection(self._max_peaks, self._sampling_rate, self._frame_size)
        self.pt = mq.MQPartialTracking(self._max_peaks)

    def set_sampling_rate(self, sampling_rate):
        self._sampling_rate = sampling_rate
        self.pd = mq.MQPeakDetection(self._max_peaks, self._sampling_rate, self._frame_size)

    def set_frame_size(self, frame_size):
        self._frame_size = frame_size
        self.window = np.hanning(frame_size)
        self.num_bins = (frame_size/2) + 1
        self.pd = mq.MQPeakDetection(self._max_peaks, self._sampling_rate, self._frame_size)

    def get_distance(self, peak1, peak2):
        return 0.0

    def process_frame(self, frame):
        # fft
        spectrum = np.fft.rfft(frame*self.window)
        peaks = self.pd.find_peaks(spectrum)
        tracked_peaks = self.pt.track_peaks(peaks)
        # calculate odf
        sum = 0.0
        for peak in tracked_peaks:
            sum += self.get_distance(peak, peak.prev_peak)
        return sum


class PeakAmpDifferenceODF(PeakODF):
    def __init__(self):
        PeakODF.__init__(self)

    def get_distance(self, peak1, peak2):
        if not peak2:
            return peak1.amplitude
        else:
            return np.abs(peak1.amplitude - peak2.amplitude)


class PeakFreqDifferenceODF(PeakODF):
    def __init__(self):
        PeakODF.__init__(self)

    def get_distance(self, peak1, peak2):
        if not peak2:
            return peak1.frequency
        else:
            return np.abs(peak1.frequency - peak2.frequency)


class PeakDifferenceODF(PeakODF):
    def __init__(self):
        PeakODF.__init__(self)

    def get_distance(self, peak1, peak2):
        if not peak2:
            return peak1.amplitude
        else:
            return np.sqrt((peak1.amplitude - peak2.amplitude) **2 +
                           (peak1.frequency - peak2.frequency) **2)


class UnmatchedPeaksODF(PeakODF):
    def __init__(self):
        PeakODF.__init__(self)

    def get_distance(self, peak1, peak2):
        if not peak2:
            return peak1.amplitude
        else:
            return 0.0

