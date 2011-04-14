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
import modal.onsetdetection as od
import modal.ui.plot as trplot
import modal.detectionfunctions as df
import numpy as np
import matplotlib.pyplot as plt
import time

file_name = 'drum-surdo-large-lick.wav'
audio, sampling_rate, reference_onsets = modal.get_audio_file(file_name)
frame_size = 2048
hop_size = 512

odf = df.PeakAmpDifferenceODF()
odf.set_frame_size(frame_size)
odf.set_hop_size(hop_size)
odf.set_sampling_rate(sampling_rate)
odf_values = []
onsets = []
threshold = []
onset_det = od.RTOnsetDetection()

# pad the input audio if necessary
if len(audio) % odf.get_frame_size() != 0:
    audio = np.hstack((audio, np.zeros(odf.get_frame_size() - (len(audio) % odf.get_frame_size()),
                                       dtype=np.double)))
print "Audio file:", file_name
print "Total length:", float(len(audio))/sampling_rate, "seconds"

start_time = time.time()
i = 0
audio_pos = 0
while audio_pos <= len(audio) - odf.get_frame_size():
    frame = audio[audio_pos:audio_pos + odf.get_frame_size()]
    odf_value = odf.process_frame(frame)
    odf_values.append(odf_value)
    det_results = onset_det.is_onset(odf_value, True)
    if det_results[0]:
        onsets.append(i*odf.get_hop_size())
    threshold.append(det_results[1])
    audio_pos += odf.get_hop_size()
    i += 1
run_time = time.time() - start_time
print "Number of onsets detected:", len(onsets)
print "Running time:", run_time, "seconds"
print "Seconds per frame:", run_time/i
print

# plot onset detection results
fig = plt.figure(1, figsize=(12, 12))
plt.subplot(3,1,1)
plt.title('Real-time onset detection with ' + odf.__class__.__name__)
plt.plot(audio, '0.4')
plt.subplot(3,1,2)
trplot.plot_detection_function(odf_values, odf.get_hop_size())
trplot.plot_detection_function(threshold, odf.get_hop_size(), "green")
plt.subplot(3,1,3)
trplot.plot_onsets(onsets, 1.0)
plt.plot(audio, '0.4')
plt.show()
