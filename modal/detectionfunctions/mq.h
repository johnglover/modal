#ifndef _MQ_H
#define _MQ_H

#include <fftw3.h>
#include <math.h>
#include "detectionfunctions.h"

typedef double sample;

typedef struct Peak
{
    float amplitude;
    float frequency;
    float phase;
    int bin;
    struct Peak* next;
    struct Peak* prev;
} Peak;

typedef struct PeakList
{
    struct PeakList* next;
    struct PeakList* prev;
    struct Peak* peak;
} PeakList;

typedef struct MQParameters
{
    int frame_size;
    int max_peaks;
    int num_bins;
    sample peak_threshold;
    sample fundamental;
    sample matching_interval;
    sample* window;
    sample* fft_in;
	fftw_complex* fft_out;
	fftw_plan fft_plan;
    PeakList* prev_peaks;
} MQParameters;

int init_mq(MQParameters* params);
void reset_mq(MQParameters* params);
int destroy_mq(MQParameters* params);
void delete_peak_list(PeakList* peak_list);

PeakList* sort_peaks_by_frequency(PeakList* peak_list, int num_peaks);

PeakList* find_peaks(int signal_size, sample* signal, MQParameters* params);
PeakList* track_peaks(PeakList* peak_list, MQParameters* params);
                    
#endif
