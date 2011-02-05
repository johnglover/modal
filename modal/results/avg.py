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
from modal.ui.plot import scheme
import matplotlib.pyplot as plt
import h5py
import numpy as np
import os

# plot results to files?
plot_results = True
# result types to calculate
cd_percentage = False
f_measure = True
precision = True
recall = True
false_positive_rate = False

# ODFs to include in results 
odfs = ["EnergyODF", "SpectralDifferenceODF", "ComplexODF", 
        "LPEnergyODF", "LPSpectralDifferenceODF", "LPComplexODF", 
        "PeakAmpDifferenceODF"]
# shorter names for plotting
odf_names = ["Energy", "SpecDiff", "Complex", 
             "LPE", "LPSD", "LPCD",
             "PAD"]

# -----------------------------------------------------------------------------

num_onsets = modal.num_onsets()
db = h5py.File(modal.results_path, "r")

if plot_results:
    if not os.path.exists('images'):
        os.mkdir('images')

try:

    # CD percentage
    if cd_percentage:
        results = {}
        for odf in odfs:
            avg = 0.0
            num_results = 0
            for analysis in db['totals/analysis']:
                if db['totals/analysis'][analysis].attrs['odf_type'] == odf:
                    a = db['totals/analysis'][analysis]
                    cdp = (a.attrs['correctly_detected']*100.0)/num_onsets
                    avg += cdp
                    num_results += 1
            results[odf] = avg/num_results

        print "Correctly Detected Percentage"
        print "-----------------------------"
        for odf in odfs:
            print odf + ": " + str(results[odf])
        print

        if plot_results:
            image_file = "images/avg_cd_percentage.png"
            results = [results[odf] for odf in odfs]

            indexes = np.arange(len(odfs))
            width = 0.8
            colours, styles = scheme(len(odfs))
            fig = plt.figure(1, figsize=(12, 8))
            plt.title("Average Detection Percentage")
            ax = plt.axes()
            ax.autoscale(False, 'y')
            ax.set_ylim(0.0, 110.0)
            bars = ax.bar(indexes, results, width, color=colours[0])
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x()+bar.get_width()/2., 1.05*height, '%f'%height,
                        ha='center', va='bottom')
            ax.set_ylabel("Detection Percentage")
            ax.set_xlabel("Detection Functions")
            ax.set_xticks(indexes+0.4)
            ax.set_xticklabels(odf_names)
            plt.savefig(image_file, bbox_inches='tight')

    # F-Measure
    if f_measure:
        results = {}
        for odf in odfs:
            results[odf] = db['totals/odfs'][odf].attrs['f_measure']
            
        if plot_results:
            image_file = "images/avg_f_measure.png"
            results = [results[odf] for odf in odfs]
            indexes = np.arange(len(odfs))
            width = 0.8
            colours, styles = scheme(len(odfs))
            fig = plt.figure(2, figsize=(12, 8))
            plt.title("Average F-Measure")
            ax = plt.axes()
            ax.autoscale(False, 'y')
            ax.set_ylim(0.0, 1.4)
            bars = ax.bar(indexes, results, width, color=colours[0])
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x()+bar.get_width()/2., 1.05*height, '%f'%height,
                        ha='center', va='bottom')
            ax.set_ylabel("F-measure")
            ax.set_xlabel("Detection Functions")
            ax.set_xticks(indexes+0.4)
            ax.set_xticklabels(odf_names)
            plt.savefig(image_file, bbox_inches='tight')

    # Precision
    if precision:
        results = {}
        for odf in odfs:
            results[odf] = db['totals/odfs'][odf].attrs['precision']
            
        if plot_results:
            image_file = "images/avg_precision.png"
            results = [results[odf] for odf in odfs]
            indexes = np.arange(len(odfs))
            width = 0.8
            colours, styles = scheme(len(odfs))
            fig = plt.figure(3, figsize=(12, 8))
            plt.title("Average Precision")
            ax = plt.axes()
            ax.autoscale(False, 'y')
            ax.set_ylim(0.0, 1.0)
            bars = ax.bar(indexes, results, width, color=colours[0])
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x()+bar.get_width()/2., 1.05*height, '%f'%height,
                        ha='center', va='bottom')
            ax.set_ylabel("Precision")
            ax.set_xlabel("Detection Functions")
            ax.set_xticks(indexes+0.4)
            ax.set_xticklabels(odf_names)
            plt.savefig(image_file, bbox_inches='tight')

    # Recall
    if recall:
        results = {}
        for odf in odfs:
            results[odf] = db['totals/odfs'][odf].attrs['recall']
            
        if plot_results:
            image_file = "images/avg_recall.png"
            results = [results[odf] for odf in odfs]
            indexes = np.arange(len(odfs))
            width = 0.8
            colours, styles = scheme(len(odfs))
            fig = plt.figure(4, figsize=(12, 8))
            plt.title("Average Recall")
            ax = plt.axes()
            ax.autoscale(False, 'y')
            ax.set_ylim(0.0, 1.0)
            bars = ax.bar(indexes, results, width, color=colours[0])
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x()+bar.get_width()/2., 1.05*height, '%f'%height,
                        ha='center', va='bottom')
            ax.set_ylabel("Recall")
            ax.set_xlabel("Detection Functions")
            ax.set_xticks(indexes+0.4)
            ax.set_xticklabels(odf_names)
            plt.savefig(image_file, bbox_inches='tight')

    # False positive rate
    if false_positive_rate:
        results = {}
        for odf in odfs:
            results[odf] = db['totals/odfs'][odf].attrs['false_positive_rate']
            
        if plot_results:
            image_file = "images/avg_false_positive_rate.png"
            results = [results[odf] for odf in odfs]
            indexes = np.arange(len(odfs))
            width = 0.8
            colours, styles = scheme(len(odfs))
            fig = plt.figure(5, figsize=(12, 8))
            plt.title("Average False Positive Rate")
            ax = plt.axes()
            ax.autoscale(False, 'y')
            ax.set_ylim(0.0, 100.0)
            bars = ax.bar(indexes, results, width, color=colours[0])
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x()+bar.get_width()/2., 1.05*height, '%f'%height,
                        ha='center', va='bottom')
            ax.set_ylabel("False Positive Rate")
            ax.set_xlabel("Detection Functions")
            ax.set_xticks(indexes+0.4)
            ax.set_xticklabels(odf_names)
            plt.savefig(image_file, bbox_inches='tight')
finally:
    db.close()

