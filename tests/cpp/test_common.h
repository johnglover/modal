#ifndef TEST_COMMON_H
#define TEST_COMMON_H

#include <iostream>
#include <vector>
#include <sndfile.hh>

#include "../../src/exceptions.h"

namespace modal
{

typedef double sample;
static const double PRECISION = 0.001;
static const char* TEST_AUDIO_FILE = "../tests/audio/flute.wav";

} // end of namespace modal

#endif
