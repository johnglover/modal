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
from modal.analysis import RTOnsetAnalysis, OnsetAnalysisThread
import modal.detectionfunctions as df
import time

run_thread = OnsetAnalysisThread()
odfs = [df.EnergyODF, df.SpectralDifferenceODF, df.ComplexODF,
        df.LPEnergyODF, df.LPSpectralDifferenceODF, df.LPComplexODF,
        df.PeakAmpDifferenceODF]
frame_size = 2048
hop_size = 512
lp_order = 5
files = modal.list_onset_files()

for file in files:
    for odf in odfs:
        oa = RTOnsetAnalysis()
        oa.analysis_file = file
        oa.odf = odf()
        oa.odf.set_frame_size(frame_size)
        oa.odf.set_hop_size(hop_size)
        if issubclass(odf, modal.LinearPredictionODF):
            oa.odf.set_order(lp_order)
        run_thread.add(oa)

# -----------------------------------------------------------------------------------
# Do all analysis runs
start_time = time.time()
print "Starting analysis."
print "Press return to stop after the current analysis run"
print 
run_thread.start()
while not run_thread.finished.isSet():
    if raw_input() == "":
        run_thread.finished.set()
run_thread.join()
run_time = time.time() - start_time
print "Total running time:", 
print int(run_time / 60), "mins,", 
print int(run_time % 60), "secs"
