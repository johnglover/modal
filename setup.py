"""Modal: Musical Onset Database And Library.

Modal is a cross-platform library for musical onset detection, written in C++ and Python.
It is provided here under the terms of the GNU General Public License.
It consists of code for several different types of Onset Detection Function (ODF) and code for
real-time and non-real-time onset detection.

All ODFs are implemented in both C++ and Python. The code for Onset detection and ODF comparison
is currently only available in Python.

Modal also includes a database of musical samples with hand-annotated onset locations for ODF 
evaluation purposes. The database can be found in the downloads section, it is not included 
in the repository. 
The database is a hierarchical database, stored in the HDF5 format.
"""
from setuptools import setup, Extension

try:
    import numpy
    try:
        numpy_include = numpy.get_include()
    except AttributeError:
        numpy_include = numpy.get_numpy_include()
except ImportError:
    print "Error: Numpy was not found."
    exit(1)

doc_lines = __doc__.split("\n")

detectionfunctions = Extension(
    "modal/detectionfunctions/_pydetectionfunctions", 
    sources=[
        "modal/detectionfunctions/detectionfunctions.cpp", 
        "modal/detectionfunctions/mq.cpp", 
        "modal/detectionfunctions/detectionfunctions.i"
    ],
    include_dirs=[numpy_include, '/usr/local/include'],
    libraries=['m', 'fftw3'],
    swig_opts=['-c++']
) 

setup(
    name='modal',
    description=doc_lines[0],
    long_description="\n".join(doc_lines[2:]),
    url='http://github.com/johnglover/modal',
    download_url='http://github.com/johnglover/modal',
    license='GPL',
    author='John Glover',
    author_email='john.c.glover@nuim.ie',
    platforms=["Linux", "Mac OS-X", "Unix", "Windows"],
    version='1.11',
    ext_modules=[detectionfunctions],
    packages=['modal', 'modal.data', 'modal.detectionfunctions', 'modal.ui', 'modal.utils'],
    scripts = ['bin/editonsets', 'bin/modaldb2audio']
)
