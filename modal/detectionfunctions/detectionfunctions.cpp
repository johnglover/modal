#include "detectionfunctions.h"
#include "mq.h"

/* ------------------------------------------------------------------------- */
/* Windowing
 */

void hann_window(int window_size, sample* window)
{
	int i;
	for(i = 0; i < window_size; i++)
	{
		window[i] *= 0.5 * (1.0 - cos(2.0*M_PI*i/(window_size-1)));
	}
}

/* ------------------------------------------------------------------------- */
/* Linear Prediction
 */

void burg(int signal_size, sample* signal, int order,
		  int num_coefs, sample* coefs)
{
	/* initialise f and b - the forward and backwards predictors */
	sample* f = (sample*)calloc(signal_size, sizeof(sample));
	sample* b = (sample*)calloc(signal_size, sizeof(sample));
	sample* temp_coefs = (sample*)calloc(num_coefs+1, sizeof(sample));
	sample* reversed_coefs = (sample*)calloc(num_coefs+1, sizeof(sample));
	sample temp;
	int k;
	for(k = 0; k < signal_size; k++)
	{
		f[k] = b[k] = signal[k];
	}
	int f_loc = 0;
	int n = 0;
	sample mu = 0.0;
	sample sum = 0.0;
	sample fb_sum = 0.0;
	temp_coefs[0] = 1.0;
	int c = 0;

	for(k = 0; k < order; k++)
	{
		/* update f_loc, which keeps track of the first element in f
		 * this takes 1 element from the start of f each time.
		 */
		f_loc += 1;
		/* calculate mu */
		sum = 0.0;
		fb_sum = 0.0;
		for(n = f_loc; n < num_coefs; n++)
		{
			sum += (f[n]*f[n]) + (b[n-f_loc]*b[n-f_loc]);
			fb_sum += (f[n]*b[n-f_loc]);
		}

		if(sum > 0)
		{
			/* check for division by zero */
			mu = -2.0 * fb_sum / sum;
		}
		else
		{
			mu = 0.0;
		}

		/* update coefficients */
		c += 1;
		for(n = 0; n <= c; n++)
		{
			reversed_coefs[n] = temp_coefs[c-n];
		}
		for(n = 0; n <= c; n++)
		{
			temp_coefs[n] += mu * reversed_coefs[n];
		}
		/* update f and b */
		for(n = f_loc; n < num_coefs; n++)
		{
			temp = f[n];
			f[n] += mu * b[n-f_loc];
			b[n-f_loc] += mu * temp;
		}
	}

	memcpy(coefs, &temp_coefs[1], sizeof(sample)*num_coefs);

	free(f);
	free(b);
	free(temp_coefs);
	free(reversed_coefs);
}

void linear_prediction(int signal_size, sample* signal,
					   int num_coefs, sample* coefs,
					   int num_predictions, sample* predictions)
{
	/* check that the number of coefficients does not exceed the
	 * number of samples in the signal
	 */
	/* todo */
	/* check that the number of predictions does not exceed the
	 * number of coefficients
	 */
	/* todo */
	int i, j;

	for(i = 0; i < num_predictions; i++)
	{
		/* Each sample in the num_coefs past samples is multiplied
		 * by a coefficient the corresponding coefficient. Results are summed.
		 */
		predictions[i] = 0.0;
		for(j = 0; j < i; j++)
		{
			predictions[i] -= coefs[j] * predictions[i-1-j];
		}
		for(j = i; j < num_coefs; j++)
		{
			predictions[i] -= coefs[j] * signal[signal_size-1-j+i];
		}
	}
}

/* ------------------------------------------------------------------------- */
/* Onset Detection Function
 */

int OnsetDetectionFunction::get_sampling_rate()
{
    return sampling_rate;
}

int OnsetDetectionFunction::get_frame_size()
{
    return frame_size;
}

int OnsetDetectionFunction::get_hop_size()
{
    return hop_size;
}

void OnsetDetectionFunction::set_sampling_rate(int value)
{
    sampling_rate = value;
}

void OnsetDetectionFunction::set_frame_size(int value)
{
    frame_size = value;
}

void OnsetDetectionFunction::set_hop_size(int value)
{
    hop_size = value;
}

void OnsetDetectionFunction::process(int signal_size, sample* signal,
                                     int odf_size, sample* odf)
{
    sample odf_max = 0.0;
	int sample_offset = 0;
	int frame = 0;

	while(sample_offset <= signal_size - frame_size)
	{
		odf[frame] = process_frame(frame_size, &signal[sample_offset]);

		/* keep track of the maximum so we can normalise later */
		if(odf[frame] > odf_max)
		{
			odf_max = odf[frame];
		}
		sample_offset += hop_size;
		frame++;
	}

	/* normalise ODF */
	if(odf_max)
	{
		for(int i = 0; i < odf_size; i++)
		{
			odf[i] /= odf_max;
		}
	}
}

/* ------------------------------------------------------------------------- */
/* Energy
 */

sample EnergyODF::process_frame(int signal_size, sample* signal)
{
    /* calculate signal energy */
    sample energy = 0.0;
    sample diff;
    int i;
    for(i = 0; i < frame_size; i++)
    {
        energy += signal[i] * signal[i];
    }
    /* get the energy difference between current and previous frame */
    diff = fabs(energy - prev_energy);
    prev_energy = energy;
    return diff;
}

/* ------------------------------------------------------------------------- */
/* SpectralDifference
 */

SpectralDifferenceODF::SpectralDifferenceODF()
{
    prev_amps = NULL;
    in = NULL;
    out = NULL;
	p = fftw_plan_dft_r2c_1d(frame_size, in, out, FFTW_ESTIMATE);
    reset();
}

SpectralDifferenceODF::~SpectralDifferenceODF()
{
    if(window) delete [] window;
    if(prev_amps) delete [] prev_amps;
    if(in) fftw_free(in);
    if(out) fftw_free(out);
    fftw_destroy_plan(p);
}

void SpectralDifferenceODF::reset()
{
    num_bins = (frame_size/2) + 1;

    if(window) delete [] window;
    window = new sample[frame_size];
    for(int i = 0; i < frame_size; i++)
    {
        window[i] = 1.0;
    }
    hann_window(frame_size, window);

    if(prev_amps) delete [] prev_amps;
    prev_amps = new sample[num_bins];
    for(int i = 0; i < num_bins; i++)
    {
        prev_amps[i] = 0;
    }

    if(in) fftw_free(in);
    in = (sample*) fftw_malloc(sizeof(sample) * frame_size);

    if(out) fftw_free(out);
	out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * num_bins);

    fftw_destroy_plan(p);
	p = fftw_plan_dft_r2c_1d(frame_size, in, out, FFTW_ESTIMATE);
}

void SpectralDifferenceODF::set_frame_size(int value)
{
    frame_size = value;
    reset();
}

sample SpectralDifferenceODF::process_frame(int signal_size, sample* signal)
{
    sample sum = 0.0;
    sample amp;
    int bin;

    /* do a FFT of the current frame */
    memcpy(in, &signal[0], sizeof(sample)*frame_size);
    window_frame(in);
    fftw_execute(p);

    /* calculate the amplitude differences between bins from consecutive frames */
    sum = 0.0;
    for(bin = 0; bin < num_bins; bin++)
    {
        amp = sqrt((out[bin][0]*out[bin][0]) + (out[bin][1]*out[bin][1]));
        sum += fabs(prev_amps[bin] - amp);
        prev_amps[bin] = amp;
    }

    return sum;
}

/* ------------------------------------------------------------------------- */
/* Complex
 */

ComplexODF::ComplexODF()
{
    prev_amps = NULL;
    prev_phases = NULL;
    prev_phases2 = NULL;
    in = NULL;
    out = NULL;
	p = fftw_plan_dft_r2c_1d(frame_size, in, out, FFTW_ESTIMATE);
    reset();
}

ComplexODF::~ComplexODF()
{
    if(window) delete [] window;
    if(prev_amps) delete [] prev_amps;
    if(prev_phases) delete [] prev_phases;
    if(prev_phases2) delete [] prev_phases2;
    if(in) fftw_free(in);
    if(out) fftw_free(out);
    fftw_destroy_plan(p);
}

void ComplexODF::reset()
{
    num_bins = (frame_size/2) + 1;

    if(window) delete [] window;
    window = new sample[frame_size];
    for(int i = 0; i < frame_size; i++)
    {
        window[i] = 1.0;
    }
    hann_window(frame_size, window);

    if(prev_amps) delete [] prev_amps;
    prev_amps = new sample[num_bins];
    for(int i = 0; i < num_bins; i++)
    {
        prev_amps[i] = 0;
    }

    if(prev_phases) delete [] prev_phases;
    prev_phases = new sample[num_bins];
    for(int i = 0; i < num_bins; i++)
    {
        prev_phases[i] = 0;
    }

    if(prev_phases2) delete [] prev_phases2;
    prev_phases2 = new sample[num_bins];
    for(int i = 0; i < num_bins; i++)
    {
        prev_phases2[i] = 0;
    }

    if(in) fftw_free(in);
    in = (sample*) fftw_malloc(sizeof(sample) * frame_size);

    if(out) fftw_free(out);
	out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * num_bins);

    fftw_destroy_plan(p);
	p = fftw_plan_dft_r2c_1d(frame_size, in, out, FFTW_ESTIMATE);
}

void ComplexODF::set_frame_size(int value)
{
    frame_size = value;
    reset();
}

sample ComplexODF::process_frame(int signal_size, sample* signal)
{
    sample phase_prediction;
    fftw_complex prediction;
    sample sum = 0.0;

    // do a FFT of the current frame
    memcpy(in, &signal[0], sizeof(sample)*frame_size);
    window_frame(in);
    fftw_execute(p);

    // calculate sum of prediction errors
    for(int bin = 0; bin < num_bins; bin++)
    {
        /* Magnitude prediction is just the previous magnitude.
         * Phase prediction is the previous phase plus the difference between
         * the previous two frames
         */
        phase_prediction = (2.0 * prev_phases[bin]) - prev_phases2[bin];
        /* bring it into the range +- pi */
        while(phase_prediction > M_PI) phase_prediction -= 2.0 * M_PI;
        while(phase_prediction < M_PI) phase_prediction += 2.0 * M_PI;
        /* convert back into the complex domain to calculate stationarities */
        prediction[0] = prev_amps[bin] * cos(phase_prediction);
        prediction[1] = prev_amps[bin] * sin(phase_prediction);
        /* get stationarity measures in the complex domain */
        sum += sqrt(((prediction[0] - out[bin][0])*(prediction[0] - out[bin][0])) +
                    ((prediction[1] - out[bin][1])*(prediction[1] - out[bin][1])));
        prev_amps[bin] = sqrt((out[bin][0]*out[bin][0]) + (out[bin][1]*out[bin][1]));
        prev_phases2[bin] = prev_phases[bin];
        prev_phases[bin] = atan2(out[bin][1], out[bin][0]);
    }

    return sum;
}

/* ------------------------------------------------------------------------- */
/* LinearPrediction
 */


/* ------------------------------------------------------------------------- */
/* LPEnergy
 */


LPEnergyODF::LPEnergyODF()
{
    init();
}

LPEnergyODF::~LPEnergyODF()
{
    destroy();
}

void LPEnergyODF::init()
{
    coefs = new sample[order];
    for(int i = 0; i < order; i++)
    {
        coefs[i] = 0;
    }

    prev_values = new sample[order];
    for(int i = 0; i < order; i++)
    {
        prev_values[i] = 0;
    }
}

void LPEnergyODF::destroy()
{
    if(coefs) delete [] coefs;
    if(prev_values) delete [] prev_values;
}

sample LPEnergyODF::process_frame(int signal_size, sample* signal)
{
    sample odf = 0.0;
    sample prediction = 0.0;

	/* calculate signal energy */
    sample energy = 0.0;
    for(int i = 0; i < frame_size; i++)
    {
        energy += signal[i] * signal[i];
    }

    /* get LP coefficients */
    burg(order, prev_values, order, order, coefs);
    /* get the difference between current and predicted energy values */
    linear_prediction(order, prev_values, order, coefs, 1, &prediction);
    odf = fabs(energy - prediction);

    /* move energies 1 frame back then update last energy */
    for(int i = 0; i < order-1; i++)
    {
        prev_values[i] = prev_values[i+1];
    }
    prev_values[order-1] = energy;
    return odf;
}

/* ------------------------------------------------------------------------- */
/* LPSpectralDifference
 */

LPSpectralDifferenceODF::LPSpectralDifferenceODF()
{
    prev_amps = NULL;
    in = NULL;
    out = NULL;
	p = fftw_plan_dft_r2c_1d(frame_size, in, out, FFTW_ESTIMATE);
    init();
}

LPSpectralDifferenceODF::~LPSpectralDifferenceODF()
{
    destroy();
}

void LPSpectralDifferenceODF::init()
{
    coefs = new sample[order];
    num_bins = (frame_size/2) + 1;

    if(window) delete [] window;
    window = new sample[frame_size];
    for(int i = 0; i < frame_size; i++)
    {
        window[i] = 1.0;
    }
    hann_window(frame_size, window);

    prev_amps = new sample*[num_bins];
    for(int i = 0; i < num_bins; i++)
    {
        prev_amps[i] = new sample[order];
        for(int j = 0; j < order; j++)
        {
            prev_amps[i][j] = 0.0;
        }
    }

    in = (sample*) fftw_malloc(sizeof(sample) * frame_size);
	out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * num_bins);
	p = fftw_plan_dft_r2c_1d(frame_size, in, out, FFTW_ESTIMATE);
}

void LPSpectralDifferenceODF::destroy()
{
    if(window) delete [] window;
    if(coefs) delete [] coefs;
    if(prev_amps) 
    {
        for(int i = 0; i < num_bins; i++)
        {
            if(prev_amps[i]) delete [] prev_amps[i];
        }
        delete [] prev_amps;
    }
    if(in) fftw_free(in);
    if(out) fftw_free(out);
    fftw_destroy_plan(p);

    window = NULL;
    coefs = NULL;
    prev_amps = NULL;
    in = NULL;
    out = NULL;
}

void LPSpectralDifferenceODF::set_frame_size(int value)
{
    destroy();
    frame_size = value;
    init();
}

sample LPSpectralDifferenceODF::process_frame(int signal_size, sample* signal)
{
    sample sum = 0.0;
    sample amp = 0.0;
    sample prediction = 0.0;

    // do a FFT of the current frame
    memcpy(in, &signal[0], sizeof(sample)*frame_size);
    window_frame(in);
    fftw_execute(p);

    // calculate the amplitude differences between bins from consecutive frames 
    for(int bin = 0; bin < num_bins; bin++)
    {
        amp = sqrt((out[bin][0]*out[bin][0]) + (out[bin][1]*out[bin][1]));
        /* get LP coefficients */
        burg(order, prev_amps[bin], order, order, coefs);
        /* get the difference between current and predicted values */
        linear_prediction(order, prev_amps[bin], order, coefs, 1, &prediction);
        sum += fabs(amp - prediction);
        /* move frames back by 1 */
        for(int j = 0; j < order-1; j++)
        {
            prev_amps[bin][j] = prev_amps[bin][j+1];
        }
        prev_amps[bin][order-1] = amp;
    }

    return sum;
}

/* ------------------------------------------------------------------------- */
/* LPComplex
 */

LPComplexODF::LPComplexODF()
{
    prev_frame = NULL;
    distances = NULL;
    in = NULL;
    out = NULL;
	p = fftw_plan_dft_r2c_1d(frame_size, in, out, FFTW_ESTIMATE);
    init();
}

LPComplexODF::~LPComplexODF()
{
    destroy();
}

void LPComplexODF::init()
{
    coefs = new sample[order];
    num_bins = (frame_size/2) + 1;

    if(window) delete [] window;
    window = new sample[frame_size];
    for(int i = 0; i < frame_size; i++)
    {
        window[i] = 1.0;
    }
    hann_window(frame_size, window);

    distances = new sample*[num_bins];
    for(int i = 0; i < num_bins; i++)
    {
        distances[i] = new sample[order];
        for(int j = 0; j < order; j++)
        {
            distances[i][j] = 0.0;
        }
    }

    prev_frame = new fftw_complex[num_bins];
    for(int i = 0; i < num_bins; i++)
    {
        prev_frame[i][0] = 0.0;
        prev_frame[i][1] = 0.0;
    }

    in = (sample*) fftw_malloc(sizeof(sample) * frame_size);
	out = (fftw_complex*) fftw_malloc(sizeof(fftw_complex) * num_bins);
	p = fftw_plan_dft_r2c_1d(frame_size, in, out, FFTW_ESTIMATE);
}

void LPComplexODF::destroy()
{
    if(window) delete [] window;
    if(coefs) delete [] coefs;
    if(distances) 
    {
        for(int i = 0; i < num_bins; i++)
        {
            if(distances[i]) delete [] distances[i];
        }
        delete [] distances;
    }
    if(prev_frame) delete [] prev_frame;
    if(in) fftw_free(in);
    if(out) fftw_free(out);
    fftw_destroy_plan(p);

    window = NULL;
    coefs = NULL;
    distances = NULL;
    prev_frame = NULL;
    in = NULL;
    out = NULL;
}

void LPComplexODF::set_frame_size(int value)
{
    destroy();
    frame_size = value;
    init();
}

sample LPComplexODF::process_frame(int signal_size, sample* signal)
{
    sample sum = 0.0;
    sample amp = 0.0;
    sample prediction = 0.0;
    sample distance = 0.0;

    // do a FFT of the current frame
    memcpy(in, &signal[0], sizeof(sample)*frame_size);
    window_frame(in);
    fftw_execute(p);

    for(int bin = 0; bin < num_bins; bin++)
    {
        distance = sqrt((out[bin][0]-prev_frame[bin][0])*(out[bin][0]-prev_frame[bin][0]) +
                        (out[bin][1]-prev_frame[bin][1])*(out[bin][1]-prev_frame[bin][1]));

        /* get LP coefficients */
        burg(order, distances[bin], order, order, coefs);
        /* get the difference between current and predicted values */
        linear_prediction(order, distances[bin], order, coefs, 1, &prediction);
        sum += fabs(distance - prediction);

        /* update distances */
        for(int j = 0; j < order-1; j++)
        {
            distances[bin][j] = distances[bin][j+1];
        }
        distances[bin][order-1] = distance;

        /* update previous frame */
        prev_frame[bin][0] = out[bin][0];
        prev_frame[bin][1] = out[bin][1];
    }

    return sum;
}

/* ------------------------------------------------------------------------- */
/* PeaksODF
 */

PeakODF::PeakODF()
{
    mq_params = (MQParameters*)malloc(sizeof(MQParameters));
    mq_params->max_peaks = 20;
    mq_params->frame_size = frame_size;
    mq_params->num_bins = (frame_size/2) + 1;
    mq_params->peak_threshold = 0.1;
    mq_params->matching_interval = 200.0;
    mq_params->fundamental = 44100.0 / frame_size; /* TODO: change to params->sampling_rate */
    init_mq(mq_params);
}

PeakODF::~PeakODF()
{
    destroy_mq(mq_params);
    free(mq_params);
}

void PeakODF::reset()
{
    reset_mq(mq_params);
    destroy_mq(mq_params);
    mq_params->frame_size = frame_size;
    mq_params->num_bins = (frame_size/2) + 1;
    mq_params->fundamental = 44100.0 / frame_size; /* TODO: change to params->sampling_rate */
    init_mq(mq_params);
}

void PeakODF::set_frame_size(int value)
{
    frame_size = value;
    reset();
}

int PeakODF::get_max_peaks()
{
    return mq_params->max_peaks;
}

void PeakODF::set_max_peaks(int value)
{
    mq_params->max_peaks = value;
}

sample PeakODF::get_distance(Peak* peak1, Peak* peak2)
{
    return 0.0;
}

sample PeakODF::process_frame(int signal_size, sample* signal)
{
    PeakList* peaks = track_peaks(find_peaks(frame_size, &signal[0], mq_params),
                                  mq_params);

    /* calculate the amplitude differences between bins from consecutive frames */
    sample sum = 0.0;
    while(peaks && peaks->peak)
    {
        sum += get_distance(peaks->peak, peaks->peak->prev);
        peaks = peaks->next;
    }
    return sum;
}

sample UnmatchedPeaksODF::get_distance(Peak* peak1, Peak* peak2)
{
    if(peak1 && !peak2)
    {
        return peak1->amplitude;
    }
    return 0.0;
}

sample PeakAmpDifferenceODF::get_distance(Peak* peak1, Peak* peak2)
{
    if(peak1 && !peak2)
    {
        return peak1->amplitude;
    }
    return fabs(peak1->amplitude - peak2->amplitude);
}

//sample peak_distance(Peak* peak1, Peak* peak2, int distance_type)
//{
//    if(distance_type == DISTANCE_AMP)
//    {
//        if(!peak2)
//        {
//            return peak1->amplitude;
//        }
//        else
//        {
//            return fabs(peak1->amplitude - peak2->amplitude);
//        }
//    }
//    else if(distance_type == DISTANCE_FREQ)
//    {
//        if(!peak2)
//        {
//            return peak1->frequency;
//        }
//        else
//        {
//            return fabs(peak1->frequency - peak2->frequency);
//        }
//    }
//    else if(distance_type == DISTANCE_COMPLEX)
//    {
//        if(!peak2)
//        {
//            return peak1->amplitude;
//        }
//        else
//        {
//            return sqrt(((peak1->amplitude - peak2->amplitude) * (peak1->amplitude - peak2->amplitude)) +
//                        ((peak1->frequency - peak2->frequency) * (peak1->frequency - peak2->frequency)));
//        }
//    }
//    else if(distance_type == DISTANCE_UNMATCHED_AMP)
//    {
//        if(!peak2)
//        {
//            return peak1->amplitude;
//        }
//        else
//        {
//            return 0.0;
//        }
//    }
//    else
//    {
//        return 0.0;
//    }
//}

