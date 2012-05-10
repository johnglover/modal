Installation
============


Required Dependencies
---------------------

* Python_ (2.6.* or 2.7.*)
* NumPy_ (1.4+)
* SciPy_ (0.8+)
* FFTW3_ (3.2+)

.. _Python: http://www.python.org
.. _SciPy: http://www.scipy.org
.. _NumPy: http://www.numpy.org
.. _FFTW3: http://www.fftw.org


Optional Dependencies
---------------------

* h5py_ for accessing the sample database, but not needed otherwise.
  (tested with 1.3.1 and HDF5_ version 1.8.4-patch1)
* Matplotlib_ for plotting (1.0+).
* Nose_ to run the unit tests.
* PyYAML_ to import/export metadata from YAML files. (3.10+).

.. _h5py: http://code.google.com/p/h5py
.. _HDF5: http://www.hdfgroup.org/HDF5
.. _Matplotlib: http://matplotlib.sourceforge.net
.. _Nose: http://somethingaboutorange.com/mrl/projects/nose
.. _PyYAML: http://pyyaml.org/wiki/PyYAML


Installing Modal
----------------

First build the extension module (so that the SWIG wrapper files are created) by running
the following command in the root folder:

    $ python setup.py build

Then to install the module in your Python site-packages directory:

    $ python setup.py install
