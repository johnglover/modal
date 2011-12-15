import numpy as np
import matplotlib.pyplot as plt

def scheme(n, scheme=0):
    colours = [["#81aac4", "#95b2c4", "#aab9c3", "#c5a483", "#c5ad97", "#c4b7aa"],
               ["#d1ccbb", "#d2cfbf", "#c7cdc1", "#9baca1", "#5f585a", "#7f7777"],
               ["#81aac4", "#81aac4", "#81aac4", "#7f7777", "#7f7777", "#7f7777", "#9baca1"]]
    styles = [["-", "--", ":", "-", "--", ":"],
              ["-", "--", ":", "-", "--", ":"],
              ["-", "--", ":", "-", "--", ":"]]
    if scheme < 0 or scheme >= len(colours) or scheme >= len(styles):
        raise Exception("Unknown colour scheme:", scheme)
    return colours[scheme][0:n], styles[scheme][0:n]

def plot_onsets(onsets, max_height=1.0):
    y = [max_height, -max_height]
    for onset in onsets:
        x = [onset, onset]
        plt.plot(x, y, 'r--')
        
def plot_detection_function(det_func, hop_size=1, colour=None):
    df = np.zeros(len(det_func) * hop_size)
    sample_offset = 0
    for frame in det_func:
        df[sample_offset:sample_offset+hop_size] = frame
        sample_offset += hop_size
    if colour:
        plt.plot(df, color=colour)
    else:
        plt.plot(df, '0.4')  
    
def dr_fpr_bars(nlp_drs, lp_drs, nlp_fprs, lp_fprs, details, 
                x_axis_label, x_tick_labels, file_name=""):
    x_axis = np.arange(len(x_tick_labels))
    width = 0.4 
    nlp_colour = "#a2b2a7"
    lp_colour = "#81aac4"
    
    details_font = {'family' : 'serif',
                    'color'  : 'black',
                    'weight' : 'normal',
                    'size'   : 12,
                   }

    # write details
    plt.figure(1, figsize=(9, 12))
    plt.figtext(0.1, 0.93, details, details_font)
    
    # plot detection rates
    ax = plt.subplot(2, 1, 1)
    plt.title("Detection Rates")
    ax.set_ylabel("Percentages")
    ax.set_xlabel(x_axis_label)
    nlp = plt.bar(x_axis, nlp_drs, width, color=nlp_colour)
    lp = plt.bar(x_axis+width, lp_drs, width, color=lp_colour)
    ax.legend((nlp[0], lp[0]), ("No Linear Prediction", "Linear Prediction"))
    ax.set_xticks(x_axis+width)
    ax.set_xticklabels(x_tick_labels)
    
    # plot false positive rates
    ax = plt.subplot(2, 1, 2)
    plt.title("False Positive Rates")
    ax.set_ylabel("Percentages")
    ax.set_xlabel(x_axis_label)
    nlp = plt.bar(x_axis, nlp_fprs, width, color=nlp_colour)
    lp = plt.bar(x_axis+width, lp_fprs, width, color=lp_colour)
    ax.legend((nlp[0], lp[0]), ("No Linear Prediction", "Linear Prediction"))
    ax.set_xticks(x_axis+width)
    ax.set_xticklabels(x_tick_labels)
    
    # save
    if file_name:
        print "Writing", file_name
        plt.savefig(file_name)
