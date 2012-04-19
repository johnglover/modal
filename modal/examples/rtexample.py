import sys
import time
import numpy as np
import scipy.io.wavfile as wavfile
import matplotlib.pyplot as plt
import modal
import modal.onsetdetection as od
import modal.ui.plot as trplot

if len(sys.argv) != 2:
    print 'Usage: python', __file__, '<path to wav file>'
    sys.exit(1)

file_name = sys.argv[1]
sampling_rate, audio = wavfile.read(file_name)
audio = np.asarray(audio, dtype=np.double)
audio /= np.max(audio)

frame_size = 2048
hop_size = 512

odf = modal.PeakAmpDifferenceODF()
odf.set_frame_size(frame_size)
odf.set_hop_size(hop_size)
odf.set_sampling_rate(sampling_rate)
odf_values = []
onsets = []
threshold = []
onset_det = od.RTOnsetDetection()

# pad the input audio if necessary
if len(audio) % odf.get_frame_size() != 0:
    n_zeros = odf.get_frame_size() - (len(audio) % odf.get_frame_size())
    audio = np.hstack((audio, np.zeros(n_zeros, dtype=np.double)))

print "Audio file:", file_name
print "Total length:", float(len(audio)) / sampling_rate, "seconds"

start_time = time.time()
i = 0
audio_pos = 0
while audio_pos <= len(audio) - odf.get_frame_size():
    frame = audio[audio_pos:audio_pos + odf.get_frame_size()]
    odf_value = odf.process_frame(frame)
    odf_values.append(odf_value)
    det_results = onset_det.is_onset(odf_value, return_threshold=True)
    if det_results[0]:
        onsets.append(i * odf.get_hop_size())
    threshold.append(det_results[1])
    audio_pos += odf.get_hop_size()
    i += 1
run_time = time.time() - start_time

print "Number of onsets detected:", len(onsets)
print "Running time:", run_time, "seconds"
print "Seconds per frame:", run_time / i

# plot onset detection results
fig = plt.figure(1, figsize=(12, 12))
plt.subplot(3, 1, 1)
plt.title('Real-time onset detection with ' + odf.__class__.__name__)
plt.plot(audio, '0.4')
plt.subplot(3, 1, 2)
trplot.plot_detection_function(odf_values, odf.get_hop_size())
trplot.plot_detection_function(threshold, odf.get_hop_size(), "green")
plt.subplot(3, 1, 3)
trplot.plot_onsets(onsets)
plt.plot(audio, '0.4')
plt.show()
