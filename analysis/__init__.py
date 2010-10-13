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
from modal.utils.progressbar import ProgressBar
import h5py
import numpy as np
import time
from threading import Thread, Event

class OnsetAnalysis(object):
    def __init__(self):
        # onset detection parameters
        self.odf = None
        # if analysis results with the same name are already in the database
        # will be computed again if self.recalculate is True. Otherwise, this
        # run will be skipped
        self.recalculate = False
        # set to True to print out more information. Useful for debugging
        self.verbose = False
        # the file to analyse
        self.analysis_file = ""
        # path to onsets db
        self.onsets_path = modal.onsets_path
        # path to analysis db
        self.analysis_path = modal.analysis_path
        
    def _status(self, message):
        if self.verbose:
            print message

    def _get_analysis_name(self):
        if not self.odf:
            raise Exception("NoODF")

        name = self.odf.__class__.__name__  + "-"
        if hasattr(self.odf, 'order'):
            name += str(self.odf.get_order()) + "-"
        if hasattr(self.odf, 'max_peaks'):
            name += str(self.odf.get_max_peaks()) + "-"
        name += str(self.odf.get_frame_size()) + "-"
        name += str(self.odf.get_hop_size())
        return name
    
    def _save_odf_params(self, grp):
        """Save odf parameters as attributes in the HDF5
        subgroup db_group."""
        if not self.odf:
            raise Exception("NoODF")

        grp['odf'].attrs['odf_type'] =  self.odf.__class__.__name__
        grp['odf'].attrs['frame_size'] = str(self.odf.get_frame_size())
        grp['odf'].attrs['hop_size'] = str(self.odf.get_hop_size())
        if hasattr(self.odf, 'order'):
            grp['odf'].attrs['prediction_frames'] = str(self.odf.get_order())
        if hasattr(self.odf, 'max_peaks'):
            grp['odf'].attrs['max_peaks'] = str(self.odf.get_max_peaks())
            
    def onset_detection(self, audio_file):
        if not self.odf:
            raise Exception("NoODF")

        # pad the input audio if necessary
        if len(audio_file) % self.odf.get_frame_size() != 0:
            pad_size = self.odf.get_frame_size() - (len(audio_file) % self.odf.get_frame_size())
            audio_file = np.hstack((audio_file, np.zeros(pad_size, dtype=np.double)))
        # check that file is of the correct type
        if not audio_file.dtype == np.double:
            audio_file = np.asarray(audio_file, dtype=np.double)

        # RT onset detection
        odf_values = self.odf.process(audio_file)
        onset_det = od.OnsetDetection()
        onsets = onset_det.find_onsets(odf_values) * self.odf.get_hop_size()
        
        return odf_values, onsets
            
    def process(self):
        """Performs onset analysis on the given audio file.
        Results are saved in the analysis database.
        If self.recalculate is False, it will not recompute the results if
        analysis results with the same name already exist."""
        # check that analysis file has been set
        if not self.analysis_file:
            self._status("No analysis file specified, ignoring")
            return
        
        # connect to db
        try:
            analysis_db = h5py.File(self.analysis_path)
            onsets_db = h5py.File(self.onsets_path, 'r')
            
            # get the subgroup for this audio file
            if not self.analysis_file in analysis_db:
                audio_grp = analysis_db.create_group(self.analysis_file)
            else:
                audio_grp = analysis_db[self.analysis_file]
            # check to see if this analysis name already exists
            name = self._get_analysis_name()
            if name in audio_grp:
                if not self.recalculate:
                    self._status("Skipping analysis for " + self.analysis_file)
                    return
                else:
                    del audio_grp[name]
            grp = audio_grp.create_group(name)
            # get audio file to analyse
            start_time = time.time()
            audio_file = onsets_db[self.analysis_file]
            # do RT onset detection
            odf, onsets = self.onset_detection(audio_file)
            # calculate and save the onset detection function
            self._status("Calculating ODF/onsets for " + self.analysis_file + " - " + name)
            grp.create_dataset('odf', data=odf)
            self._save_odf_params(grp)
            # save onset locations
            if len(onsets):
                onsets_dset = grp.create_dataset('onsets', data=onsets)
            else:
                # can't create an empty dataset
                onsets_dset = grp.create_group('onsets')
            # finished - output analysis time
            run_time = time.time() - start_time
            done_msg = "Done, in "
            done_msg += str(int(run_time / 60)) + " mins, " 
            done_msg += str(int(run_time % 60)) + " secs\n"
            self._status(done_msg)
        finally:
            analysis_db.close()
            onsets_db.close()

        
class RTOnsetAnalysis(OnsetAnalysis):
    def onset_detection(self, audio_file):
        if not self.odf:
            raise Exception("NoODF")

        # pad the input audio if necessary
        if len(audio_file) % self.odf.get_frame_size() != 0:
            pad_size = self.odf.get_frame_size() - (len(audio_file) % self.odf.get_frame_size())
            audio_file = np.hstack((audio_file, np.zeros(pad_size, dtype=np.double)))
        # check that file is of the correct type
        if not audio_file.dtype == np.double:
            audio_file = np.asarray(audio_file, dtype=np.double)

        # RT onset detection
        onset_det = od.RTOnsetDetection()
        odf_values = []
        onsets = []
        i = 0
        p = 0
        while p <= len(audio_file) - self.odf.get_frame_size():
            frame = audio_file[p:p + self.odf.get_frame_size()]
            odf_value = self.odf.process_frame(frame)
            odf_values.append(odf_value)
            if onset_det.is_onset(odf_value):
                onsets.append(i * self.odf.get_hop_size())
            p += self.odf.get_hop_size()
            i += 1
        
        return np.array(odf_values), np.array(onsets)


class OnsetAnalysisThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.finished = Event()
        self.analysis_runs = []
        
    def add(self, analysis_run):
        self.analysis_runs.append(analysis_run)
        
    def num_runs(self):
        return len(self.analysis_runs)
        
    def run(self):
        pb = ProgressBar(maxval=self.num_runs())
        pb.start()
        
        for i in range(len(self.analysis_runs)):
            if not self.finished.isSet():
                self.analysis_runs[i].process()
                pb.update(i+1)
        pb.finish()
        self.finished.set()
        print "Analysis finished"
