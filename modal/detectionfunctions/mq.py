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

# Adapted from the simpl sinusoidal modelling library.
# See http://simplsound.sourceforge.net for more information.

import numpy as np

class Peak(object):
    def __init__(self):
        self.amplitude = 0.0
        self.frequency = 0.0
        self.phase = 0.0
        self.bin_number = 0
        self.next_peak = None
        self.prev_peak = None

def compare_peak_amps(peak_x, peak_y):
    """Compares two peaks, and returns 1, 0 or -1 if the first has a greater
    amplitude than the second, they have the same amplitude, or the second has
    a greater amplitude than the first respectively.
    Can be used to sort lists of peaks."""
    if peak_x.amplitude > peak_y.amplitude:
        return 1
    elif peak_x.amplitude < peak_y.amplitude:
        return -1
    else:
        return 0

def compare_peak_freqs(peak_x, peak_y):
    """Compares two peaks, and returns 1, 0 or -1 if the first has a greater
    frequency than the second, they have the same frequency, or the second has
    a greater frequency than the first respectively.
    Can be used to sort lists of peaks."""
    if peak_x.frequency > peak_y.frequency:
        return 1
    elif peak_x.frequency < peak_y.frequency:
        return -1
    else:
        return 0

class MQPeakDetection(object):
    """Peak detection, based on the McAulay and Quatieri (MQ) algorithm.
    A peak is defined as the point in the spectrum where the slope changes from
    position to negative. Hamming window is used, window size must be (at least) 
    2.5 times the average pitch. During voiced sections of speech, the window size
    is updated every 0.25 secs, to the average pitch.
    Unlike the sinusoidal modelling algorithm, this uses a fixed window size."""
    def __init__(self, max_peaks, sampling_rate, window_size):
        self._max_peaks = max_peaks
        self._sampling_rate = sampling_rate
        self._window_size = window_size
        self._fundamental = float(self._sampling_rate / self._window_size)
        self._peak_threshold = 0.1
        
    def find_peaks(self, spectrum):
        """Selects the highest peaks from the given spectral frame, up to a maximum of 
        self._max_peaks peaks."""
        peaks = []
        prev_mag = np.abs(spectrum[0])
        current_mag = np.abs(spectrum[1])
        next_mag = 0.0

        # find all peaks in the spectrum
        for bin in range(2, len(spectrum)-1):
            next_mag = np.abs(spectrum[bin])
            if (current_mag > prev_mag and 
                current_mag > next_mag and 
                current_mag > self._peak_threshold):
                p = Peak()
                p.amplitude = current_mag
                p.bin_number = bin - 1
                p.frequency = (bin - 1) * self._fundamental
                p.phase = np.angle(spectrum[bin-1])
                peaks.append(p)
            prev_mag = current_mag
            current_mag = next_mag

        # sort peaks, largest amplitude first, and up to a max of self._max_peaks
        peaks.sort(cmp=compare_peak_amps)
        peaks.reverse()
        if len(peaks) > self._max_peaks:
            peaks = peaks[0:self._max_peaks]
        # put back into frequency order
        peaks.sort(cmp=compare_peak_freqs)
        return peaks


class MQPartialTracking(object):
    "Partial tracking, based on the McAulay and Quatieri (MQ) algorithm"    
    def __init__(self, max_peaks):
        self._max_peaks = max_peaks
        self._matching_interval = 200  # peak matching interval (in Hz)
        #self._matching_amp_factor = 1.25
        self._prev_peaks = None

    def _find_closest_match(self, peak, frame, backwards_match=True):
        """Find a candidate match for peak in frame if one exists. This is the closest
        (in frequency) match that is within self._matching_interval."""
        match = None
        free_peaks = []
        for p in frame:
            if backwards_match:
                if not p.prev_peak:
                    free_peaks.append(p)
            else:
                if not p.next_peak:
                    free_peaks.append(p)

        if free_peaks:
            min_distance = self._matching_interval
            match = None
            for p in free_peaks:
                distance = abs(peak.frequency - p.frequency)
                if (distance < min_distance and distance < self._matching_interval):
                    amp_diff = abs(peak.amplitude - p.amplitude)
                    #if amp_diff < self._matching_amp_factor * peak.amplitude:
                    min_distance = distance 
                    match = p
        return match
        
    def _get_free_peak_below(self, peak, frame):
        """Returns the closest unmatched peak in frame with a frequency less than peak.frequency."""
        # find peak in frame
        for peak_number, p in enumerate(frame):
            if p == peak:
                # go back through lower peaks (in order) and return the first unmatched
                current_peak = peak_number - 1
                while current_peak >= 0:
                    if not frame[current_peak].prev_peak:
                        return frame[current_peak]
                    current_peak -= 1
        return None
    
    def track_peaks(self, current_peaks):
        """
        1. If there is no peak within the matching interval, the track dies.
        If there is at least one peak within the matching interval, the closest match
        is declared a candidate match.

        2. If there is a candidate match from step 1, and it is not a closer match to
        any of the remaining unmatched frequencies, it is declared a definitive match.
        If the candidate match has a closer unmatched peak in the previous frame, it is
        not selected. Instead, the closest lower frequency peak to the candidate is
        checked. If it is within the matching interval, it is selected as a definitive
        match. If not, the track dies.
        In any case, step 1 is repeated on the next unmatched peak."""

        if self._prev_peaks:
            # find all matches for peaks in self._prev_peaks in the current frame
            for peak in self._prev_peaks:
                match = self._find_closest_match(peak, current_peaks)
                if match:
                    # is this match closer to any of the other unmatched peaks in prev_peaks?
                    closest_to_candidate = self._find_closest_match(match, self._prev_peaks, False)
                    if not closest_to_candidate == peak:
                        # see if the closest peak with lower frequency to the candidate is within
                        # the matching interval
                        lower_peak = self._get_free_peak_below(match, current_peaks)
                        if lower_peak:
                            if abs(lower_peak.frequency - peak.frequency) < self._matching_interval:
                                lower_peak.prev_peak = peak
                                peak.next_peak = lower_peak
                    # if closest_peak == peak, it is a definitive match
                    else:
                        match.prev_peak = peak
                        peak.next_peak = match

        self._prev_peaks = current_peaks
        return current_peaks
