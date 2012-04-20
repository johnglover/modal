#include "onsetdetection.h"

RTOnsetDetection::RTOnsetDetection() {
    n_prev_values = 10;
    prev_values = new sample[n_prev_values];
    for(int i = 0; i < n_prev_values; i ++) {
        prev_values[i] = 0.f;
    }

    threshold = 0.1f;
    mean_weight = 2.f;
    median_weight = 1.f;
    median_window = 7;
    largest_peak = 0.f;
    noise_ratio = 0.05f;
    max_threshold = 0.05f;
    max_odf_value = 0.f;
}

RTOnsetDetection::~RTOnsetDetection() {
    delete[] prev_values;
}

bool RTOnsetDetection::is_onset(sample odf_value) {
    bool result = false;

    if((prev_values[0] > threshold) &&
       (prev_values[0] > odf_value) &&
       (prev_values[0] > prev_values[1]) &&
       (odf_value > (max_threshold * max_odf_value))) {
        result = true;
    }

    // update threshold
    threshold = (median_weight * median(prev_values, n_prev_values)) +
                (mean_weight * mean(prev_values, n_prev_values)) +
                (noise_ratio * largest_peak);

    // update values
    for(int i = 1; i < n_prev_values - 1; i++) {
        prev_values[i] = prev_values[i + 1];
    }
    prev_values[0] = odf_value;

    if(result && (prev_values[1] > largest_peak)) {
        largest_peak = prev_values[1];
    }

    return result;
}

// ---------------------------------------------------------------------------

sample mean(sample arr[], int n) {
    if(n <= 0) {
        return 0.f;
    }

    sample m = 0.0;
    for(int i = 0; i < n; i++) {
        m += arr[i];
    }
    return m / n;
}

/*
 *  This routine is based on the algorithm described in
 *  "Numerical recipes in C", Second Edition,
 *  Cambridge University Press, 1992, Section 8.5, ISBN 0-521-43108-5
 *  This code by Nicolas Devillard - 1998. Public domain.
 *
 *  http://ndevilla.free.fr/median/median/index.html
 */

#define ELEM_SWAP(a,b) { register sample t=(a);(a)=(b);(b)=t; }

sample median(sample arr[], int n) {
    int low, high ;
    int median;
    int middle, ll, hh;

    low = 0 ; high = n-1 ; median = (low + high) / 2;
    for(;;) {
        /* One element only */
        if(high <= low) return arr[median];

        /* Two elements only */
        if(high == low + 1) {
            if(arr[low] > arr[high]) {
                ELEM_SWAP(arr[low], arr[high]);
            }
            return arr[median];
        }

        /* Find median of low, middle and high items; swap into position low */
        middle = (low + high) / 2;
        if(arr[middle] > arr[high]) ELEM_SWAP(arr[middle], arr[high]);
        if(arr[low] > arr[high]) ELEM_SWAP(arr[low], arr[high]);
        if(arr[middle] > arr[low]) ELEM_SWAP(arr[middle], arr[low]);

        /* Swap low item (now in position middle) into position (low+1) */
        ELEM_SWAP(arr[middle], arr[low+1]);

        /* Nibble from each end towards middle, swapping items when stuck */
        ll = low + 1;
        hh = high;
        for(;;) {
            do ll++; while(arr[low] > arr[ll]);
            do hh--; while(arr[hh]  > arr[low]);

            if(hh < ll) break;

            ELEM_SWAP(arr[ll], arr[hh]);
        }

        /* Swap middle item (in position low) back into correct position */
        ELEM_SWAP(arr[low], arr[hh]);

        /* Re-set active partition */
        if(hh <= median) low = ll;
        if(hh >= median) high = hh - 1;
    }
}

#undef ELEM_SWAP
