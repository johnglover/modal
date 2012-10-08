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
except ImportError, ie:
    # if not found, use the python versions
    print ie
    print
    print 'Warning: C++ ODF implementions not found, using pure Python ODFs'
    from detectionfunctions import EnergyODF
    from detectionfunctions import SpectralDifferenceODF
    from detectionfunctions import ComplexODF
    from detectionfunctions import LPEnergyODF
    from detectionfunctions import LPSpectralDifferenceODF
    from detectionfunctions import LPComplexODF
    from detectionfunctions import PeakAmpDifferenceODF
