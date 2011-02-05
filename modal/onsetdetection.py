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

from modal import OnsetDetectionFunction 
from modal import LinearPredictionODF
from modal import EnergyODF
from modal import SpectralDifferenceODF
from modal import ComplexODF
from modal import LPEnergyODF
from modal import LPSpectralDifferenceODF
from modal import LPComplexODF
from modal import PeakAmpDifferenceODF
import modal
import numpy as np  

class ODFPeak(object):
    def __init__(self):
        self.location = 0
        self.value = 0
        self.threshold_at_peak = 0
        self.size = 0
    
class OnsetDetection(object):
    # threshold types
    THRESHOLD_NONE = 0
    THRESHOLD_FIXED = 1
    THRESHOLD_MEDIAN = 2
    # onset location in relation to peak
    ONSET_AT_PEAK = 0      # on the peak
    ONSET_AT_PEAK_DIFF = 1 # largest point in diff(odf) behind peak
    ONSET_AT_MINIMA = 2    # at the previous local minima
    ONSET_AT_THRESHOLD = 3 # last point before the peak where odf >= peak threshold
     
    def __init__(self):
        self.onsets = []
        self.odf = []
        self.threshold_type = self.THRESHOLD_MEDIAN
        self.threshold = None
        self.median_a = 0.1
        self.median_b = 1.0
        self.median_window = 9
        self.onset_location = self.ONSET_AT_PEAK
        # number of neighbouring samples on each side that a peak
        # must be larger than 
        self.peak_size = 1 
        self.peaks = []

    def _calculate_median_threshold(self):
        if not len(self.odf):
            return

        self.threshold = np.zeros(len(self.odf))
        for i in range(len(self.odf)):
           # make sure we have enough signal either side of i to calculate the 
           # median threshold
           start_sample = 0
           end_sample = len(self.odf)
           if i > (self.median_window / 2):
               start_sample = i - (self.median_window/2)
           if i < len(self.odf) - (self.median_window / 2):
               end_sample = i + (self.median_window/2) + 1
           median_samples = self.odf[start_sample:end_sample]
           self.threshold[i] = self.median_a + (self.median_b * np.median(median_samples))

    def find_peaks(self):
        self.peaks = []
        for i in range(len(self.odf)):
            # check that the current value is above the threshold
            if self.threshold_type != self.THRESHOLD_NONE:
                if self.threshold_type == self.THRESHOLD_MEDIAN:
                    if self.odf[i] < self.threshold[i]:
                        continue
                elif self.threshold_type == self.THRESHOLD_FIXED:
                    if self.odf[i] < self.threshold:
                        continue
            # find local maxima
            # peaks only need to be larger than the nearest self.peak_size neighbours
            # at boundaries
            forward_neighbours = min(self.peak_size, len(self.odf) - (i+1))
            backward_neighbours = min(self.peak_size, i)
            maxima = True
            # search all forward neighbours (up to a max of self.peak_size), testing to see
            # if the current sample is bigger than all of them
            for p in range(forward_neighbours):
                if self.odf[i] < self.odf[i+p+1]:
                    maxima = False
                    break
            # if it is less than 1 of the forward neighbours, no need to check backwards
            if not maxima:
                continue
            # now test the backwards neighbours
            for p in range(backward_neighbours):
                if self.odf[i] < self.odf[i-(p+1)]:
                    maxima = False
                    break
            if maxima:
                peak = ODFPeak()
                peak.location = i
                peak.value = self.odf[i]
                peak.threshold_at_peak = self.threshold[i]
                peak.size = self.peak_size
                self.peaks.append(peak)
        return self.peaks

    def get_peak(self, location):
        """Return the ODFPeak object with a given peak.location value.
        Returns None if no such peak exists."""
        if self.peaks:
            for p in self.peaks:
                if p.location == location:
                    return p
        return None
    
    def find_onsets(self, odf):
        self.onsets = []
        self.odf = odf
        if self.threshold_type == self.THRESHOLD_MEDIAN:
            self._calculate_median_threshold()
        self.find_peaks()

        prev_peak_location = 0
        for peak in self.peaks:
            onset_location = peak.location
            # if onset locations are peak locations, we're done

            if self.onset_location == self.ONSET_AT_PEAK_DIFF:
                # get previous peak_size/2 samples, including peak.location
                start = (peak.location+1) - (self.peak_size/2)
                if start < 0:
                    start = 0
                end = peak.location+1
                if end >= len(self.det_func):
                    end = len(self.det_func)-1
                samples = self.det_func[start:end]
                # get the point of biggest change in the samples
                samples_diff = np.diff(samples)
                max_diff = abs(samples_diff[-1])
                max_diff_pos = 0
                for i in range(1, len(samples_diff)):
                    if samples_diff[i] >= max_diff:
                        max_diff = samples_diff[i]
                        max_diff_pos = i
                onset_location = peak.location - (len(samples_diff)-max_diff_pos)

            elif self.onset_location == self.ONSET_AT_MINIMA:
                if peak.location > 1:
                    i = peak.location - 1
                    # find the nearest local minima behind the peak
                    while i > 1:
                        if (self.det_func[i] <= self.det_func[i+1] and
                            self.det_func[i] <= self.det_func[i-1]):
                            break
                        if (i-1) <= prev_peak_location:
                            break
                        i -= 1
                    onset_location = i

            elif self.onset_location == self.ONSET_AT_THRESHOLD:
                if peak.location > 1:
                    i = peak.location - 1
                    # find the last point before the peak where the
                    # odf is above the threshold
                    while i > 1:
                        if self.det_func[i-1] < peak.threshold_at_peak:
                            break
                        if (i-1) <= prev_peak_location:
                            break
                        i -= 1
                    onset_location = i

            self.onsets.append(onset_location)
            prev_peak_location = peak.location
        return np.array(self.onsets)
    
class RTOnsetDetection(object):
    def __init__(self):
        self.num_values = 10
        self.num_increasing_values = 1
        self.prev_values = np.zeros(self.num_values)
        self.threshold = 0.1
        self.mean_weight = 2.0 
        self.median_weight = 1.00 
        self.median_window = 7
        self.largest_peak = 0.0
        self.noise_ratio = 0.05
        self.increasing = True
    
    def is_onset(self, odf_value, return_threshold=False):
        result = False

        if ((self.prev_values[-1] > self.threshold) and 
            (self.prev_values[-1] > odf_value) and 
            (self.prev_values[-1] > self.prev_values[-2])):
                result = True

        # update threshold
        self.threshold = ((self.median_weight * np.median(self.prev_values)) +
                          (self.mean_weight * np.mean(self.prev_values)) +
                          (self.noise_ratio * self.largest_peak))

        # update values
        self.prev_values = np.hstack((self.prev_values[1:], odf_value))
        if result:
            if self.prev_values[-2] > self.largest_peak:
                self.largest_peak = self.prev_values[-2]
        if return_threshold:
            return result, self.threshold
        else:
            return result
