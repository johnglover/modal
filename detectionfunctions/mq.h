/* Copyright (c) 2010 John Glover, National University of Ireland, Maynooth

 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */
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
