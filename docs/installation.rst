Installation
============

Dependencies
------------

All platforms:

* [Python](http://www.python.org) - tested with 2.6
* [SciPy/NumPy](http://www.scipy.org) - tested with NumPy 1.4.1 and SciPy 0.8
* [FFTW3](http://www.fftw.org) - tested with version 3.2.2

Additionally, windows users will need:

* [MinGW/MSYS](http://www.mingw.org/)

Optional:

* [h5py](http://code.google.com/p/h5py) - tested with version 1.3.1 and HDF5 version 1.8.4-patch1. Used for accessing the
  sample database, but not needed otherwise.
* [Matplotlib (for plotting)](http://matplotlib.sourceforge.net) - Tested with version 1.0
* [Nose (for unit tests)](http://somethingaboutorange.com/mrl/projects/nose)
* [PyYAML](http://pyyaml.org/wiki/PyYAML) - Metadata can be exported/imported from YAML files. Tested with version 3.10.


Installing Modal
----------------

First build the extension module (so that the SWIG wrapper files are created) by running
the following command in the root folder:

    $ python setup.py build

Then to install the module in your Python site-packages directory:

    $ python setup.py install
