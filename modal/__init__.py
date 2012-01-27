# import detection function classes
from detectionfunctions import OnsetDetectionFunction
from detectionfunctions import LinearPredictionODF
from detectionfunctions import PeakODF
from detectionfunctions import EnergyODF
from detectionfunctions import SpectralDifferenceODF
from detectionfunctions import ComplexODF
from detectionfunctions import LPEnergyODF
from detectionfunctions import LPSpectralDifferenceODF
from detectionfunctions import LPComplexODF
from detectionfunctions import PeakAmpDifferenceODF

# modal db imports
from db import data_path, onsets_path, \
    list_onset_files, list_onset_files_poly, num_onsets, \
    get_audio_file

