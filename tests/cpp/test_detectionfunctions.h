#ifndef TEST_DETECTIONFUNCTIONS_H
#define TEST_DETECTIONFUNCTIONS_H

#include <cppunit/extensions/HelperMacros.h>

#include "../../modal/detectionfunctions/detectionfunctions.h"
#include "test_common.h"

namespace modal
{


class TestPeakODF : public CPPUNIT_NS::TestCase {
    CPPUNIT_TEST_SUITE(TestPeakODF);
    CPPUNIT_TEST(test_basic);
    CPPUNIT_TEST(test_changing_hop_frame_sizes);
    CPPUNIT_TEST_SUITE_END();

protected:
    PeakODF _odf;
    SndfileHandle _sf;

    void test_basic();
    void test_changing_hop_frame_sizes();

public:
    void setUp();
};


} // end of namespace modal

#endif
