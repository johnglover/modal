# Copyright (c) 2010 John Glover, National University of Ireland, Maynooth
# 
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of 
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

"""Modal: Musical Onset Database And Library.

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
The database is a hierarchical database, stored in the HDF5 format.
"""
from setuptools import setup, Extension

# get numpy include directory
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
detectionfunctions = Extension("modal/detectionfunctions/_pydetectionfunctions", 
                               sources=["modal/detectionfunctions/detectionfunctions.cpp", 
                                        "modal/detectionfunctions/mq.cpp", 
                                        "modal/detectionfunctions/detectionfunctions.i"],
                               include_dirs=[numpy_include, '/usr/local/include'],
                               libraries=['m', 'fftw3'],
                               swig_opts=['-c++']) 

setup(name='modal',
      description=doc_lines[0],
      long_description="\n".join(doc_lines[2:]),
      url='http://github.com/johnglover/modal',
      download_url='http://github.com/johnglover/modal',
      license='GPL',
      author='John Glover',
      author_email='john.c.glover@nuim.ie',
      platforms=["Linux", "Mac OS-X", "Unix", "Windows"],
      version='1.1',
      # requires=['numpy (>=1.0.1)'],
      ext_modules=[detectionfunctions],
      packages=['modal', 'modal.analysis', 'modal.data', 'modal.detectionfunctions',
                'modal.results', 'modal.ui', 'modal.utils'])
