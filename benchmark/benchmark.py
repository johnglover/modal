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
import modal.pydetectionfunctions as df
from modal.ui.plot import scheme
import numpy as np
import matplotlib.pyplot as plt
import timeit

odfs = [df.EnergyODF, df.SpectralDifferenceODF, df.ComplexODF,
        df.LPEnergyODF, df.LPSpectralDifferenceODF, df.LPComplexODF,
        df.PeakAmpDifferenceODF]
odf_names = ["Energy", "SD", "CD", "LPE", "LPSD", "LPCD", "PAD"]
num_runs = 5
num_repeats = 5
frame_size = 2048
hop_size = 512

file_name = 'drum-surdo-large-lick.wav'
audio, sampling_rate, reference_onsets = modal.get_audio_file(file_name)
# if necessary, pad the input signal
if len(audio) % hop_size != 0:
    audio = np.hstack((audio, np.zeros(hop_size - (len(audio) % hop_size),
                                       dtype=np.double)))
odf_samples = np.zeros(len(audio)/hop_size, dtype=np.double)
avg_run_times = []

for odf in odfs:
    o = odf()
    o.set_frame_size(frame_size)
    o.set_hop_size(hop_size)
    o.set_sampling_rate(sampling_rate)
    t = timeit.Timer("o.process(audio, odf_samples)", "from __main__ import o, audio, odf_samples")
    run_times = t.repeat(num_repeats, num_runs)
    avg = (sum(run_times) / num_repeats) / num_runs
    avg_run_times.append(avg)

indexes = np.arange(len(odfs))
width = 0.8
colours, styles = scheme(len(avg_run_times))
fig = plt.figure(1, figsize=(12, 8))
plt.title("Average Running Times")
ax = plt.axes()
bars = ax.bar(indexes, (np.array(avg_run_times)*100.0) / (float(len(audio))/sampling_rate),
              width, color=colours[0])
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x()+bar.get_width()/2., 1.05*height, '%f'%height,
            ha='center', va='bottom')
ax.set_ylabel("% of file length")
ax.set_xlabel("Detection Functions")
ax.set_xticks(indexes+0.4)
ax.set_xticklabels(odf_names)
ax.autoscale(False, 'y')
ax.set_ylim(0.0, 10.0)
#ax.text(0.02, 0.95, "frame size: " + str(frame_size),
        #transform=ax.transAxes)
#ax.text(0.02, 0.92, "hop size: " + str(hop_size),
        #transform=ax.transAxes)
plt.savefig("benchmark.png", bbox_inches='tight')
