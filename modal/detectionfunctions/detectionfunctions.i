%module pydetectionfunctions
%{
    #include "detectionfunctions.h"
    #include "mq.h"
    #define SWIG_FILE_WITH_INIT
%}

%include "numpy.i"

%init 
%{
    import_array();
%}

%apply(int DIM1, sample* INPLACE_ARRAY1)
{
    (int odf_size, sample* odf),
    (int signal_size, sample* signal),
    (int num_coefs, sample* coefs),
    (int num_predictions, sample* predictions),
    (int num_bins, sample* amplitudes),
    (int max_peaks, int* peaks)
}

%apply(int DIM1, int* INPLACE_ARRAY1)
{
    (int max_peaks, int* peaks)
}

%include "detectionfunctions.h" 
%include "mq.h"
