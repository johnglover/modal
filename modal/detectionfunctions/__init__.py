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

# onset detection function base classes
from detectionfunctions import OnsetDetectionFunction
from detectionfunctions import LinearPredictionODF
from detectionfunctions import PeakODF

# try to import the onset detection functions from the c extension module
try:
    from pydetectionfunctions import EnergyODF
    from pydetectionfunctions import SpectralDifferenceODF
    from pydetectionfunctions import ComplexODF
    from pydetectionfunctions import LPEnergyODF
    from pydetectionfunctions import LPSpectralDifferenceODF
    from pydetectionfunctions import LPComplexODF
    from pydetectionfunctions import PeakAmpDifferenceODF
# if not found, use the python versions
except:
    from detectionfunctions import EnergyODF
    from detectionfunctions import SpectralDifferenceODF
    from detectionfunctions import ComplexODF
    from detectionfunctions import LPEnergyODF
    from detectionfunctions import LPSpectralDifferenceODF
    from detectionfunctions import LPComplexODF
    from detectionfunctions import PeakAmpDifferenceODF
