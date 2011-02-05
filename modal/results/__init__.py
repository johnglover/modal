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
import h5py

class Result(object):
    def __init__(self):
        self.name = ""
        self.file = ""
        self.odf_type = ""
        self.frame_size = 0
        self.hop_size = 0
        self.smooth_type = 0
        self.detection_rate = 0
        self.false_positive_rate = 0
        self.prediction_frames = 1
        self.prediction_type = ""
        self.match_time = 0
        self.threshold_type = 0
        self.onset_location = 0
        self.nearest_onsets = []


class ResultSet(set):
    def __init__(self):
        set.__init__(self)
        self.db_path = modal.results_path
        self.audio_file = ""
        self.run = ""
        self.match_time = ""
        self.detection_type = "median-peak"
        
    def add_total_results(self):
        pass
        
    def add_file_results(self):
        try:
            db = h5py.File(self.db_path)
            if not self.audio_file:
                for a_file in db['files']:
                    file = db[a_file]
                    self._add_results_for_file(file)
            else:
                # only add results for the given file
                file = db['files'][self.audio_file]
                self._add_results_for_file(file)
        finally:
            db.close()
            
    def _add_results_for_file(self, file):
        if not self.run:
            for analysis in file:
                r = file[analysis]
                self._add_results_for_run(r)
        else:
            # only add data for the given analysis run
            run = file[analysis]
            self._add_results_for_run(run)
        
    def _add_results_for_run(self, run):
        if not self.match_time:
            for match_time in run:
                self._add_result(run, match_time)
        else:
            self._add_result(run, match_time)
            
    def _add_result(self, run, match_time):
        if not self.detection_type in run[match_time]:
            return
        mt = run[match_time][self.detection_type]
        r = Result()
        r.match_time = int(match_time)
        r.name = run.name.split("/")[-1]
        r.file = run.parent.name.split("/")[-1]
        r.odf_type = run.attrs['odf_type']
        r.frame_size = run.attrs['frame_size']
        r.hop_size = run.attrs['hop_size']
        r.prediction_frames = run.attrs['prediction_frames']
        r.prediction_type = run.attrs['prediction_type']
        r.smooth_type = run.attrs['smooth_type']
        r.threshold_type = mt.attrs['threshold_type']
        r.onset_location = mt.attrs['onset_location']
        r.detection_rate = mt.attrs['detection_rate']
        r.false_positive_rate = mt.attrs['false_positive_rate']
        if 'nearest_onsets' in mt:
            for o in mt['nearest_onsets']:
                r.nearest_onsets.append(o)
        self.add(r)
    
    def subset(self, **kwargs):
        ss = ResultSet()
        sets = []
        for k in kwargs:
            # make a subset for each argument
            s = set()
            for r in self:
                if getattr(r, k) == kwargs[k]:
                    s.add(r)
            sets.append(s)
        # return the intersection of the lists
        return ss.union(reduce(set.intersection, sets))
    
    def get_all(self, var):
        s = set()
        for result in self:
            s.add(getattr(result, var))
        return sorted(s)
    
    def average(self, var):
        if len(self):
            avg = 0
            for result in self:
                avg += getattr(result, var)
            return float(avg) / len(self)
        
    def highest(self, var):
        vars = self.get_all(var)
        if vars:
            max_val = max(vars)
            return self.subset(**{var:max_val})
    
    def lowest(self, var):
        vars = self.get_all(var)
        if vars:
            min_val = min(vars)
            return self.subset(**{var:min_val})
    
    def maximum(self, var, val):
        s = ResultSet()
        for result in self:
            if getattr(result, var) <= val:
                s.add(result)
        return s
    
    def minimum(self, var, val):
        s = ResultSet()
        for result in self:
            if getattr(result, var) >= val:
                s.add(result)
        return s
