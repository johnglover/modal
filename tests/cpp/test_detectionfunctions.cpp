#include "test_detectionfunctions.h"

using namespace modal;

void TestPeakODF::setUp() {
    _sf = SndfileHandle(TEST_AUDIO_FILE);

    if(_sf.error() > 0) {
        throw Exception(std::string("Could not open audio file: ") +
                        std::string(TEST_AUDIO_FILE));
    }
}

void TestPeakODF::test_basic() {
    std::vector<sample> audio(_sf.frames(), 0.0);
    _sf.read(&audio[0], (int)_sf.frames());

    int hop_size = _odf.get_hop_size();
    int frame_size = _odf.get_frame_size();
    std::vector<sample> odf_values;

    for(int i = 0; i <= audio.size() - frame_size; i += hop_size) {
        odf_values.push_back(_odf.process_frame(frame_size, &(audio[i])));
    }

    CPPUNIT_ASSERT(odf_values.size() > 0);

    for(int i = 0; i < odf_values.size(); i++) {
        CPPUNIT_ASSERT(odf_values[i] >= 0.0);
    }
}

void TestPeakODF::test_changing_hop_frame_sizes() {
    std::vector<sample> audio(_sf.frames(), 0.0);
    _sf.read(&audio[0], (int)_sf.frames());

    int hop_size = 256;
    int frame_size = 512;
    std::vector<sample> odf_values;

    _odf.set_hop_size(hop_size);
    _odf.set_frame_size(frame_size);

    for(int i = 0; i <= audio.size() - frame_size; i += hop_size) {
        odf_values.push_back(_odf.process_frame(frame_size, &(audio[i])));
    }

    CPPUNIT_ASSERT(odf_values.size() > 0);

    for(int i = 0; i < odf_values.size(); i++) {
        CPPUNIT_ASSERT(odf_values[i] >= 0.0);
    }

    hop_size = 256;
    frame_size = 256;
    odf_values.clear();

    _odf.reset();
    _odf.set_hop_size(hop_size);
    _odf.set_frame_size(frame_size);

    for(int i = 0; i <= audio.size() - frame_size; i += hop_size) {
        odf_values.push_back(_odf.process_frame(frame_size, &(audio[i])));
    }

    CPPUNIT_ASSERT(odf_values.size() > 0);

    for(int i = 0; i < odf_values.size(); i++) {
        CPPUNIT_ASSERT(odf_values[i] >= 0.0);
    }

    hop_size = 64;
    frame_size = 256;
    odf_values.clear();

    _odf.reset();
    _odf.set_hop_size(hop_size);
    _odf.set_frame_size(frame_size);

    for(int i = 0; i <= audio.size() - frame_size; i += hop_size) {
        odf_values.push_back(_odf.process_frame(frame_size, &(audio[i])));
    }

    CPPUNIT_ASSERT(odf_values.size() > 0);

    for(int i = 0; i < odf_values.size(); i++) {
        CPPUNIT_ASSERT(odf_values[i] >= 0.0);
    }
}
