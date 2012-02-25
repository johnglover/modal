import numpy as np
import scipy.signal
import mq
import lp

# -----------------------------------------------------------------------------
# Spectral processing

def toPolar(x, y):
    return (np.sqrt((x * x) + (y * y)), np.arctan2(y, x))

def toRectangular(mag, phase):
    return np.complex(mag * np.cos(phase),
                      mag * np.sin(phase))

# -----------------------------------------------------------------------------
# Low-pass filter

def lpf(signal, order, cutoff):
    "Low-pass FIR filter"
    filter = scipy.signal.firwin(order, cutoff)
    return np.convolve(signal, filter, 'same')

# -----------------------------------------------------------------------------
# Moving average

def moving_average(signal, num_points):
    """Smooth signal by returning a num_points moving average.
    The first and last num_points/2 are zeros.
    See: http://en.wikipedia.org/wiki/Moving_average"""
    ma = np.zeros(signal.size)
    # make sure num_points is odd
    if num_points % 2 == 0:
        num_points += 1
    n = int(num_points / 2)
    centre = n
    # for each num_points window in the signal, calculate the average
    while centre < signal.size - n:
        avg = 0.0
        for i in np.arange(centre - n, centre + n + 1):
            avg += signal[i]
        avg /= num_points
        ma[centre] = avg
        centre += 1
    return ma

# -----------------------------------------------------------------------------
# Savitzky-Golay

def savitzky_golay(signal, num_points):
    """Smooth a signal using the Savitzky-Golay algorithm.
    The first and last num_points/2 are zeros.
    See: http://www.statistics4u.com/fundstat_eng/cc_filter_savgolay.html"""
    sg = np.zeros(signal.size)
    # make sure num_points is valid. If not, use defaults
    if not num_points in [5, 7, 9, 11]:
        print "Invalid number of points to Savitzky-Golay algorithm, using default (5)."
        num_points = 5
    n = int(num_points / 2)
    centre = n
    # set up savitzky golay coefficients
    if num_points == 5:
        coefs = np.array([-3, 12, 17, 12, -3])
    elif num_points == 7:
        coefs = np.array([-2, 3, 6, 7, 6, 3, -2])
    elif num_points == 9:
        coefs = np.array([-21, 14, 39, 54, 59, 54, 39, 14, -21])
    elif num_points == 11:
        coefs = np.array([-36, 9, 44, 69, 84, 89, 84, 69, 44, 9, -36])
    # calculate denominator
    denom = np.sum(coefs)
    # for each num_points window in the signal, calculate the average
    while centre < signal.size - n:
        avg = 0.0
        c = 0
        for i in np.arange(centre - n, centre + n + 1):
            # calculate weighted average
            avg += signal[i] * coefs[c]
            c += 1
        avg /= denom
        sg[centre] = avg
        centre += 1
    return sg

# -----------------------------------------------------------------------------
# Normalise

def normalise(values):
    if np.max(np.abs(values)):
        values /= np.max(np.abs(values))

# -----------------------------------------------------------------------------
# Onset Detection Functions

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
            return moving_average(signal, self.smooth_window)
        elif self.smooth_type == self.SMOOTH_SAVITZKY_GOLAY:
            return savitzky_golay(signal, self.smooth_window)
        elif self.smooth_type == self.SMOOTH_LPF:
            return filter.lpf(signal, self.lpf_order, self.lpf_cutoff)
        # default action is not to smooth
        return signal

    def process_frame(self, frame):
        return 0.0

    def process(self, signal, detection_function):
        # give a warning if the hop size does not divide evenly into the signal size
        if len(signal) % self.hop_size != 0:
            print "Warning: hop size (%d) is not a factor of signal size (%d)" % \
                (self.hop_size, len(signal))
            # signal = np.hstack((signal, np.zeros(self.hop_size - (len(signal) % self.hop_size))))

        # make sure the given detection function array is large enough
        if len(detection_function) < len(signal) / self.hop_size:
            raise Exception("detection function not large enough: %d (need % d)" 
                % (len(detection_function), len(signal) / self.hop_size)
            )

        # get a list of values for each frame
        sample_offset = 0
        i = 0
        while sample_offset + self.frame_size <= len(signal):
            frame = signal[sample_offset:sample_offset + self.frame_size]
            detection_function[i] = self.process_frame(frame)
            sample_offset += self.hop_size
            i += 1

        # perform any post-processing on the ODF, such as smoothing or normalisation
        normalise(detection_function)
        self.det_func = detection_function
        return self.det_func

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
        self.num_bins = (self.frame_size / 2) + 1
        self.prev_amps = np.zeros(self.num_bins)

    def set_frame_size(self, frame_size):
        self._frame_size = frame_size
        self.window = np.hanning(frame_size)
        self.num_bins = (frame_size / 2) + 1
        self.prev_amps = np.zeros(self.num_bins)

    def process_frame(self, frame):
        # fft
        spectrum = np.fft.rfft(frame * self.window)
        # calculate spectral difference for each bin
        sum = 0.0
        for bin in range(self.num_bins):
            real = spectrum[bin].real
            imag = spectrum[bin].imag
            amp = np.sqrt((real * real) + (imag * imag))
            sum += np.abs(amp - self.prev_amps[bin])
            self.prev_amps[bin] = amp
        return sum


class ComplexODF(OnsetDetectionFunction):
    def __init__(self):
        OnsetDetectionFunction.__init__(self)
        self.window = np.hanning(self.frame_size)
        self.num_bins = (self.frame_size / 2) + 1
        self.prev_mags = np.zeros(self.num_bins)
        self.prev_phases = np.zeros(self.num_bins)
        self.prev_phases2 = np.zeros(self.num_bins)
        self.prediction = np.zeros(self.num_bins, dtype=np.complex)

    def set_frame_size(self, frame_size):
        self._frame_size = frame_size
        self.window = np.hanning(frame_size)
        self.num_bins = (frame_size / 2) + 1
        self.prev_mags = np.zeros(self.num_bins)
        self.prev_phases = np.zeros(self.num_bins)
        self.prev_phases2 = np.zeros(self.num_bins)
        self.prediction = np.zeros(self.num_bins, dtype=np.complex)

    def process_frame(self, frame):
        # fft
        spectrum = np.fft.rfft(frame * self.window)
        # calculate complex difference for each bin
        cd = 0.0
        for bin in range(self.num_bins):
            # magnitude prediction is just the previous magnitude
            # phase prediction is the previous phase plus the difference between 
            # the previous two frames
            predicted_phase = (2 * self.prev_phases[bin]) - self.prev_phases2[bin]
            # bring it into the range +- pi
            predicted_phase -= 2 * np.pi * np.round(predicted_phase / (2 * np.pi))
            # convert back into the complex domain to calculate stationarities
            self.prediction[bin] = toRectangular(self.prev_mags[bin], predicted_phase)
            # get stationarity measures in the complex domain
            real = (self.prediction[bin].real - spectrum[bin].real)
            real = real * real
            imag = (self.prediction[bin].imag - spectrum[bin].imag)
            imag = imag * imag
            cd += np.sqrt(real + imag)
            # update previous phase info for the next frame
            self.prev_phases2[bin] = self.prev_phases[bin]
            self.prev_mags[bin], self.prev_phases[bin] = toPolar(spectrum[bin].real,
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

    def max_odf_value(self):
        '''
        As amplitude values are assumed to be floating point numbers
        between 0 and 1, the maximum deviation in 1 frame is the number
        of peaks.
        '''
        return self._max_peaks


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
