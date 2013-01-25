#include "test_onsetdetection.h"

using namespace modal;

void TestOnsetDetection::setUp() {
    a = new sample[5];
    for(int i = 0; i < 5; i++) {
        a[i] = 0.f;
    }
}

void TestOnsetDetection::tearDown() {
    delete[] a;
}

void TestOnsetDetection::test_mean() {
    a[0] = 1.0;
    a[1] = 4.0;
    a[2] = 5.0;
    CPPUNIT_ASSERT_DOUBLES_EQUAL(mean(a, 5), 2.0, PRECISION);
    CPPUNIT_ASSERT_DOUBLES_EQUAL(mean(a, 0), 0.0, PRECISION);
}

void TestOnsetDetection::test_median() {
    a[0] = 1.0;
    a[1] = 2.0;
    a[2] = 3.0;
    a[3] = 4.0;
    a[4] = 5.0;
    CPPUNIT_ASSERT_DOUBLES_EQUAL(median(a, 5), 3.0, PRECISION);
    a[2] = 6.0;
    CPPUNIT_ASSERT_DOUBLES_EQUAL(median(a, 5), 4.0, PRECISION);
}

void TestOnsetDetection::test_is_onset() {
    RTOnsetDetection od;
    CPPUNIT_ASSERT(!od.is_onset(0.1));
    CPPUNIT_ASSERT(!od.is_onset(0.6));
    CPPUNIT_ASSERT(!od.is_onset(0.7));
    CPPUNIT_ASSERT(od.is_onset(0.5));
}
