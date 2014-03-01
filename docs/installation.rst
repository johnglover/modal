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


Installing Modal dependencies on OS X (tested on 10.9.2)
--------------------------------------------------------

These instructions assume that you are using Homebrew_ to install packages.

    $ brew install fftw gsl libsndfile cmake gfortran

    $ brew install freetype libpng swig homebrew/science/hdf5

matplotlib currently does not find freetype2 when installed using homebrew,
so symlink it to /usr/local/include:

    $ ln -s /usr/local/Cellar/freetype/2.5.2/include/freetype2/ /usr/local/include/freetype

.. _Homebrew: http://mxcl.github.com/homebrew


Installing Modal dependencies on Linux (Ubuntu 12.04)
-----------------------------------------------------

    $ sudo apt-get install build-essential libfftw3-dev gsl-bin gsl0-dev libsndfile-dev cmake

    $ sudo apt-get install libblas-dev liblapack-dev gfortran

    $ sudo apt-get install libfreetype6-dev libpng-dev

    $ sudo apt-get install python-dev swig python-numpy python-scipy libhdf5-serial-dev


Installing Python dependencies (all platforms)
----------------------------------------------

These instructions assume that Python and pip are both installed.

Install Python dependencies:

    $ pip install numpy scipy matplotlib cython h5py nose


Installing Modal (all platforms)
--------------------------------

Install the C++ library:

    $ mkdir build_release && cd build_release

    $ cmake -D CMAKE_BUILD_TYPE=Release ..

    $ make

    $ make install

    $ cd ..

Install the Python module:

    $ python setup.py build

    $ python setup.py install
