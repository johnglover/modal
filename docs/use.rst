Onset Detection
===============

Onset detection detects when a sound (typically a note in music) is played.
This tutorial_ describes onset detection in more detail, including
basics and descriptions of several algorithms.


General Use
===========

First, an audio file must be read. We can do that using SciPy's
wavfile_.

::

    filename = 'moanin_solo.wav'
    sampling_rate, audio = wavfile.read(file_name)
    audio = ascontiguousarray(audio, dtype=double)
    audio /= np.max(audio)

Our array has to be a contiguous array for ``odf.process(...)``, the reason we
use ``ascontiguousarray()``.

Then, we have to define our frame size and the hop size. These are how large
each window is and how large each step within the frame is respectively. These
define how many onsets you detect. Specifically, you detect ``len(audio) /
hop_size`` onsets.

::

    frame_size = 2048
    hop_size = 512

Then, we detect our onsets, setting parameters as appropriate.

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

can be used for ``modal.ComplexODF()``. Various parameters (``hop_size``,
``frame_size``) may have to be tuned.

After that intermediate step, we detect onsets.

::

    onset_det = od.OnsetDetection()
    onset_det.peak_size = 3
    onsets = onset_det.find_onsets(odf_values) * odf.get_hop_size()

This complete example can be found on Github_.



.. _Github: https://github.com/johnglover/modal/blob/master/modal/examples/example.py
.. _wavfile: http://docs.scipy.org/doc/scipy/reference/generated/scipy.io.wavfile.read.html
.. _tutorial: http://www.cs.bu.edu/~snyder/cs591/Handouts/bello_onset_tutorial.pdf


