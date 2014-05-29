Onset Detection
===============

The goal of musical onset detection is to identify the locations in an
audio signal where new sound events (such as musical notes) begin.
This tutorial_ describes onset detection in more detail, including
basics and descriptions of several algorithms.


General Use
===========

First, an audio file must be read. We can do that using SciPy's
wavfile_.

::

    filename = 'audio_input.wav'
    sampling_rate, audio = wavfile.read(file_name)
    audio = np.asarray(audio, dtype=np.double)
    audio /= np.max(audio)

Next, define the frame size and the hop size. These are how large
each analysis window is and how large each step between windows is respectively.

This will influence:

* How many onsets you can detect in a signal of a given length, as
  you can detect at most ``len(audio) / hop_size`` onsets.
* The accuracy of the onset detection, as most of the detection algorithms rely
  on detecting changes in audio spectra over time, and larger frame sizes result
  in higher frequency resolution in the spectra.

::

    frame_size = 2048
    hop_size = 512

Next, compute an onset detection function:

::

    odf = modal.ComplexODF()
    odf.set_hop_size(hop_size)
    odf.set_frame_size(frame_size)
    odf.set_sampling_rate(sampling_rate)
    odf_values = zeros(len(audio) / hop_size, dtype=double)
    odf.process(x, odf_values)

``odf.process(in, out)`` has `in` and `out` as input and output. It does not
modify ``x``, only ``odf_values``.

Any one of

:: 

    odf = modal.ComplexODF()
    odf = modal.EnergyODF()
    odf = modal.LPEnergyODF()
    odf = modal.LPSpectralDifferenceODF()
    odf = modal.LinearPredictionODF()
    odf = modal.PeakODF()
    odf = modal.PeakAmpDifferenceODF()
    odf = modal.OnsetDetectionFunction()

can be used instead of ``modal.ComplexODF()``. Various parameters (``hop_size``,
``frame_size``) may have to be tuned.

Finally, detect onsets:

::

    onset_det = od.OnsetDetection()
    onset_det.peak_size = 3
    onsets = onset_det.find_onsets(odf_values) * odf.get_hop_size()

This complete example can be found on Github_.

.. _Github: https://github.com/johnglover/modal/blob/master/modal/examples/example.py
.. _wavfile: http://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.read.html
.. _tutorial: http://www.cs.bu.edu/~snyder/cs591/Handouts/bello_onset_tutorial.pdf
