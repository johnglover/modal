Musical Onset Database And Library (Modal)
==========================================

Modal is a cross-platform library for musical onset detection, written in C++ and Python.
It is provided here under the terms of the GNU General Public License.
It consists of code for several different types of Onset Detection Function (ODF), code for
real-time and non-real-time onset detection, and a means for comparing the performance of
different ODFs.

All ODFs are implemented in both C++ and Python. The code for Onset detection and ODF comparison
is currently only available in Python.

Modal also includes a database of musical samples with hand-annotated onset locations for ODF 
evaluation purposes. The database can be found in the downloads section, it is not included 
in the repository. 
The database is a hierarchical database, stored in the [HDF5](http://www.hdfgroup.org/HDF5/) format.


**Note:** The code needed to replicate the results from the paper
"Real-time Detection of Musical Onsets with Linear Prediction and Sinusoidal Modelling", published
in the EURASIP Journal on Advances in Signal Processing (2011) can now be found here:
http://github.com/johnglover/eurasip2011

All files copyright (c) 2010-2011 John Glover, National University of Ireland, Maynooth (unless otherwise specified)

Dependencies
------------

### All platforms

* [Python](http://www.python.org) - tested with 2.6
* [SciPy/NumPy](http://www.scipy.org) - tested with NumPy 1.4.1 and SciPy 0.8
* [FFTW3](http://www.fftw.org) - tested with version 3.2.2

Additionally, windows users will need:

* [MinGW/MSYS](http://www.mingw.org/)

### Optional

* [h5py](http://code.google.com/p/h5py) - tested with version 1.3.1 and HDF5 version 1.8.4-patch1. Used for accessing the
  sample database, but not needed otherwise.
* [Matplotlib (for plotting)](http://matplotlib.sourceforge.net) - Tested with version 1.0
* [Nose (for unit tests)](http://somethingaboutorange.com/mrl/projects/nose)


Installation
------------

First build the extension module (so that the SWIG wrapper files are created) by running
the following command in the root folder:

    $ python setup.py build

Then to install the module in your Python site-packages directory:

    $ python setup.py install


Use
---

Make sure that the variable `data_path` in the main `__init__.py` file corresponds to the directory
that your onset database is in, and that `onsets_path` corresponds to the name of the onset database.
This defaults to the `data` folder in the package directory.

Have a look at the examples in the `examples` folder for basic use. 


Contributing
------------

Send any comments, queries, suggestions or bug reports to john dot c dot glover at nuim dot ie.

