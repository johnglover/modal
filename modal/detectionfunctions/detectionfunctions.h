#ifndef _DETECTIONFUNCTIONS_H
#define _DETECTIONFUNCTIONS_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fftw3.h>
#include <math.h>
#include "mq.h"
#include "exceptions.h"

typedef double sample;

void hann_window(int window_size, sample* window);

void burg(int signal_size, sample* signal, int order,
		  int num_coefs, sample* coefs);
void linear_prediction(int signal_size, sample* signal,
					   int num_coefs, sample* coefs,
					   int num_predictions, sample* predictions);

class OnsetDetectionFunction {
    protected:
        int sampling_rate;
        int frame_size;
        int hop_size;
        sample* window;

    public:
        OnsetDetectionFunction() {
            sampling_rate = 44100;
            frame_size = 512;
            hop_size = 256;
            window = NULL;
        }

        virtual void window_frame(sample* frame) {
            if(window) {
                for(int i = 0; i < frame_size; i++) {
                    frame[i] *= window[i];
                }
            }
        }

        virtual int get_sampling_rate();
        virtual int get_frame_size();
        virtual int get_hop_size();
        virtual void set_sampling_rate(int value);
        virtual void set_frame_size(int value);
        virtual void set_hop_size(int value);

        virtual sample process_frame(int signal_size, sample* signal) {
            return 0.0;
        }
        void process(int signal_size, sample* signal,
                     int odf_size, sample* odf);
};

class EnergyODF : public OnsetDetectionFunction {
    protected:
        sample prev_energy;

    public:
        EnergyODF() {
            prev_energy = 0.0;
        }
        sample process_frame(int signal_size, sample* signal);
};

class SpectralDifferenceODF : public OnsetDetectionFunction {
    protected:
        int num_bins;
        sample* prev_amps;
        sample* in;
        fftw_complex* out;
        fftw_plan p;

    public:
        SpectralDifferenceODF();
        ~SpectralDifferenceODF();
        void reset();
        virtual void set_frame_size(int value);
        sample process_frame(int signal_size, sample* signal);
};

class ComplexODF : public OnsetDetectionFunction {
    protected:
        int num_bins;
        sample* prev_amps;
        sample* prev_phases;
        sample* prev_phases2;  // 2 frames ago
        sample* in;
        fftw_complex* out;
        fftw_plan p;

    public:
        ComplexODF();
        ~ComplexODF();
        void reset();
        virtual void set_frame_size(int value);
        sample process_frame(int signal_size, sample* signal);
};

class LinearPredictionODF : public OnsetDetectionFunction {
    protected:
        int order;
        sample* coefs;

    public:
        LinearPredictionODF() {
            order = 5;
        }
        virtual void init() {}
        virtual void destroy() {}
        virtual int get_order() {
            return order;
        }
        virtual void set_order(int value) {
            destroy();
            order = value;
            init();
        }
};

class LPEnergyODF : public LinearPredictionODF {
    protected:
        sample* prev_values;

    public:
        LPEnergyODF();
        ~LPEnergyODF();
        void init();
        void destroy();
        sample process_frame(int signal_size, sample* signal);
};

class LPSpectralDifferenceODF : public LinearPredictionODF {
    protected:
        int num_bins;
        sample** prev_amps;
        sample* in;
        fftw_complex* out;
        fftw_plan p;

    public:
        LPSpectralDifferenceODF();
        ~LPSpectralDifferenceODF();
        void init();
        void destroy();
        virtual void set_frame_size(int value);
        sample process_frame(int signal_size, sample* signal);
};

class LPComplexODF : public LinearPredictionODF {
    protected:
        int num_bins;
        fftw_complex* prev_frame;
        sample** distances;
        sample* in;
        fftw_complex* out;
        fftw_plan p;

    public:
        LPComplexODF();
        ~LPComplexODF();
        void init();
        void destroy();
        virtual void set_frame_size(int value);
        sample process_frame(int signal_size, sample* signal);
};

struct MQParameters;
struct Peak;

class PeakODF : public OnsetDetectionFunction {
    protected:
        MQParameters* mq_params;

    public:
        PeakODF();
        virtual ~PeakODF();
        virtual void reset();
        virtual void set_frame_size(int value);
        virtual int get_max_peaks();
        virtual void set_max_peaks(int value);
        virtual sample max_odf_value() {
            return 0.f;
        }
        virtual sample get_distance(Peak* peak1, Peak* peak2);
        sample process_frame(int signal_size, sample* signal);
};

class UnmatchedPeaksODF : public PeakODF {
    public:
        sample get_distance(Peak* peak1, Peak* peak2);
};

class PeakAmpDifferenceODF : public PeakODF {
    public:
        sample get_distance(Peak* peak1, Peak* peak2);
        sample max_odf_value();
};

#endif
