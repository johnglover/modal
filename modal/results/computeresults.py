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
from modal.utils.progressbar import ProgressBar
import numpy as np
import h5py
import time

def find_matches(ar1, ar2, limit):
    """For each element in ar1, see if there is a matching
    element in ar2. A match is found if abs(ar1 - ar2) <= limit.
    Returns an array giving the position in ar2 of the match
    for the corresponding element in ar1. The value in the returned
    array is -1 if there is no match for this value. Each element
    can have at most 1 corresponding element (so each ar1 is mapped
    to at most 1 ar2 and vice versa).
    
    Example: If the first element in ar1 has a matching element
             at the 3rd element in ar2, and r is the return array,
             r[0] = 2"""
    matches = np.ones(len(ar1)) * -1
    paired1 = np.zeros(len(ar1))
    paired2 = np.zeros(len(ar2))
    n = 0 # the number of detected matches
    
    for i in range(len(ar1)):
        for j in range(len(ar2)):
            if np.abs(ar1[i]-ar2[j]) <= limit:
                # potential match
                if paired1[i] or paired2[j]:
                    continue
                else:
                    matches[i] = j
                    paired1[i] = 1
                    paired2[j] = 1
                    n += 1
    return n, matches

def nearest_match(n, values):
    """Returns the nearest value in values to n, or None values is None."""
    if not len(values):
        return None
    distance = abs(n - values[0])
    nearest = 0
    for i in range(1, len(values)):
        if abs(n - values[i]) < distance:
            nearest = i
            distance = abs(n - values[i])
    return values[nearest]

def add_params(group, target):
    """Add all members of target.attrs to the group.attrs"""
    for p in target.attrs:
        group.attrs[p] = target.attrs[p]

if __name__ == "__main__":
    print "Calculating results..."
    pb = ProgressBar()
    pb.start()
    current_file = 0
    start_time = time.time()
    
    try:
        onsets_db = h5py.File(modal.onsets_path, "r")
        analysis_db = h5py.File(modal.analysis_path, "r")
        results_db = h5py.File(modal.results_path)
        results_db.create_group('files')
        # onsets within this number of milliseconds of the manually entered
        # locations are said to be correctly detected
        match_time = 50
        # progress bar max value is the number of analysis files
        pb.maxval = len(analysis_db)
        # totals group
        results_db.create_group('totals')
        results_db['totals'].create_group('analysis')
        results_db['totals'].create_group('odfs')
        # dicts used to hold total results for each analysis type
        correctly_detected = {}
        false_negatives = {}
        false_positives = {}
        # dicts used to hold total results for each odf type
        odf_correctly_detected = {}
        odf_false_negatives = {}
        odf_false_positives = {}
        
        for audio_file in analysis_db:
            # create a group in the results db for this audio file
            if audio_file in results_db['files']:
                result_audio_group = results_db['files'][audio_file]
            else:
                result_audio_group = results_db['files'].create_group(audio_file)
                
            # get the correct information
            correct_locations = onsets_db[audio_file].attrs['onsets']
            sampling_rate = float(onsets_db[audio_file].attrs['sampling_rate'])
            match_samples = (sampling_rate/1000.0) * match_time
                    
            file = analysis_db[audio_file]
            for analysis in file:
                # create a group for this analysis in the totals group
                if not analysis in results_db['totals/analysis']:
                    t = results_db['totals/analysis'].create_group(analysis)
                    print file, file[analysis]
                    add_params(t, file[analysis]['odf'])

                # create a group for this analysis run in the files db
                if analysis in result_audio_group:
                    analysis_results = result_audio_group[analysis]
                else:
                    analysis_results = result_audio_group.create_group(analysis)
                    add_params(analysis_results, file[analysis]['odf'])

                r = analysis_results.create_group(str(match_time))
                odf_type = file[analysis]['odf'].attrs['odf_type']
                onsets = file[analysis]['onsets']
                # check to see how many of the correct onset locations
                # (entered manually) have a corresponding detected onset
                # corresponding onsets are those within self.match_time milliseconds
                # detection rate is calculated as a percentage of the number of
                # correct onset locations
                cd = find_matches(correct_locations, onsets,
                                  match_samples)[0]
                r.attrs['correctly_detected'] = cd
                if analysis in correctly_detected:
                    correctly_detected[analysis] += cd
                else:
                    correctly_detected[analysis] = cd 
                if odf_type in odf_correctly_detected:
                    odf_correctly_detected[odf_type] += cd
                else:
                    odf_correctly_detected[odf_type] = cd
                
                # false negatives
                fn = len(correct_locations) - cd
                r.attrs['false_negatives'] = fn
                if analysis in false_negatives:
                    false_negatives[analysis] += fn
                else:
                    false_negatives[analysis] = fn
                if odf_type in odf_false_negatives:
                    odf_false_negatives[odf_type] += fn
                else:
                    odf_false_negatives[odf_type] = fn
                
                # check to see how many of the detected onsets are false positives,
                # ie: they have no corresponding correct onset location
                num_matches = find_matches(onsets, correct_locations,
                                           match_samples)[0]
                fp = len(onsets) - num_matches
                r.attrs['false_positives'] = fp
                if analysis in false_positives:
                    false_positives[analysis] += fp
                else:
                    false_positives[analysis] = fp
                if odf_type in odf_false_positives:
                    odf_false_positives[odf_type] += fp
                else:
                    odf_false_positives[odf_type] = fp
                
                # for each detected onset, get distance in samples to nearest correct onset
                if len(onsets):
                    nearest_onsets = []
                    for onset in onsets:
                        n = nearest_match(onset, correct_locations) - onset
                        nearest_onsets.append(n)
                    r.create_dataset('nearest_onsets', data=nearest_onsets)
                # copy other onset detection parameters
                add_params(r, onsets)
                        
            # update progress bar
            current_file += 1
            pb.update(current_file)
        pb.finish()
        
        # save total results for each analysis run
        print "Calculating totals for analysis runs..."
        for analysis, cd in correctly_detected.iteritems():
            fn = false_negatives[analysis]
            fp = false_positives[analysis]
            p = float(cd) / (cd + fp)
            r = float(cd) / (cd + fn)
            f = (2.0 * r * p) / (p + r)
            fpr = (100.0 * fp) / (cd + fp)
            g = results_db['totals/analysis'][analysis]
            g.attrs['correctly_detected'] = cd
            g.attrs['false_negatives'] = fn
            g.attrs['false_positives'] = fp
            g.attrs['precision'] = p
            g.attrs['recall'] = r
            g.attrs['f_measure'] = f
            g.attrs['false_positive_rate'] = fpr
            
        # save total results for each ODF type
        print "Calculating totals for each Onset Detection Function..."
        for odf, cd in odf_correctly_detected.iteritems():
            fn = odf_false_negatives[odf]
            fp = odf_false_positives[odf]
            p = float(cd) / (cd + fp)
            r = float(cd) / (cd + fn)
            f = (2.0 * r * p) / (p + r)
            fpr = (100.0 * fp) / (cd + fp)
            odf_grp = results_db['totals/odfs'].create_group(odf)
            odf_grp.attrs['correctly_detected'] = cd
            odf_grp.attrs['false_negatives'] = fn
            odf_grp.attrs['false_positives'] = fp
            odf_grp.attrs['precision'] = p
            odf_grp.attrs['recall'] = r
            odf_grp.attrs['f_measure'] = f
            odf_grp.attrs['false_positive_rate'] = fpr
    
    finally:
        onsets_db.close()
        analysis_db.close()
        results_db.close()
        
    print "Done. Total running time:",
    run_time = time.time() - start_time
    print int(run_time / 60), "mins,", 
    print int(run_time % 60), "secs"
