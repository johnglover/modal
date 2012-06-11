#ifndef _ONSETDETECTION_H
#define _ONSETDETECTION_H

#include <string.h>

typedef double sample;

sample mean(sample arr[], int n);
sample median(sample arr[], int n);

class RTOnsetDetection {
    private:
        int n_prev_values;
        sample* prev_values;
        sample* prev_values_copy;  // needed to compute median as input array is modified
        sample threshold;
        sample mean_weight;
        sample median_weight;
        int median_window;
        sample largest_peak;
        sample noise_ratio;
        sample max_threshold;

    public:
        RTOnsetDetection();
        ~RTOnsetDetection();
        bool is_onset(sample odf_value);

        sample max_odf_value;
};

#endif
