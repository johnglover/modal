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
evaluation purposes. The database is a hierarchical database, stored in the [HDF5](http://www.hdfgroup.org/HDF5/) format,
and can be found [here](https://drive.google.com/file/d/1NA_QZ7r8fpl6xqmnCvPArv5Zo-70GFu9/view?usp=sharing).

**Note:** The code needed to replicate the results from the paper
"Real-time Detection of Musical Onsets with Linear Prediction and Sinusoidal Modelling", published
in the EURASIP Journal on Advances in Signal Processing (2011) can now be found here:
http://github.com/johnglover/eurasip2011


Documentation
-------------

Project documentation can viewed online at http://readthedocs.org/docs/modal/en/latest/.
