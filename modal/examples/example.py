import sys
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

odf = modal.ComplexODF()
odf.set_hop_size(hop_size)
odf.set_frame_size(frame_size)
odf.set_sampling_rate(sampling_rate)
odf_values = np.zeros(len(audio) / hop_size, dtype=np.double)
odf.process(audio, odf_values)

onset_det = od.OnsetDetection()
onset_det.peak_size = 3
onsets = onset_det.find_onsets(odf_values) * odf.get_hop_size()

# plot onset detection results
fig = plt.figure(1, figsize=(12, 12))
plt.subplot(3, 1, 1)
plt.title('Onset detection with ' + odf.__class__.__name__)
plt.plot(audio, '0.4')
plt.subplot(3, 1, 2)
trplot.plot_detection_function(onset_det.odf, hop_size)
trplot.plot_detection_function(onset_det.threshold, hop_size, "green")
plt.subplot(3, 1, 3)
trplot.plot_onsets(onsets, 1.0)
plt.plot(audio, '0.4')
plt.show()
