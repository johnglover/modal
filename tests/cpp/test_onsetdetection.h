#ifndef TEST_ONSETDETECTION_H
#define TEST_ONSETDETECTION_H

#include <cppunit/extensions/HelperMacros.h>

#include "../../src/onsetdetection.h"
#include "test_common.h"

namespace modal
{


class TestOnsetDetection : public CPPUNIT_NS::TestCase {
    CPPUNIT_TEST_SUITE(TestOnsetDetection);
    CPPUNIT_TEST(test_mean);
    CPPUNIT_TEST(test_median);
    CPPUNIT_TEST(test_is_onset);
    CPPUNIT_TEST_SUITE_END();

protected:
    sample* a;

    void test_mean();
    void test_median();
    void test_is_onset();

public:
    void setUp();
    void tearDown();
};


} // end of namespace modal

#endif
