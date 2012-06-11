#include <iostream>
#include <cppunit/ui/text/TextTestRunner.h>
#include <cppunit/TestResult.h>
#include <cppunit/TestResultCollector.h>
#include <cppunit/extensions/HelperMacros.h>
#include <cppunit/BriefTestProgressListener.h>
#include <cppunit/extensions/TestFactoryRegistry.h>
#include "../../src/onsetdetection.h"


class TestOnsetDetection : public CPPUNIT_NS::TestCase {
    CPPUNIT_TEST_SUITE(TestOnsetDetection);
    CPPUNIT_TEST(test_mean);
    CPPUNIT_TEST(test_median);
    CPPUNIT_TEST(test_is_onset);
    CPPUNIT_TEST_SUITE_END();

protected:
    static const double PRECISION = 0.001;
    sample* a;

    void test_mean() { 
        a[0] = 1.0;
        a[1] = 4.0;
        a[2] = 5.0;
        CPPUNIT_ASSERT_DOUBLES_EQUAL(mean(a, 5), 2.0, PRECISION);
        CPPUNIT_ASSERT_DOUBLES_EQUAL(mean(a, 0), 0.0, PRECISION);
    }

    void test_median() {
        a[0] = 1.0;
        a[1] = 2.0;
        a[2] = 3.0;
        a[3] = 4.0;
        a[4] = 5.0;
        CPPUNIT_ASSERT_DOUBLES_EQUAL(median(a, 5), 3.0, PRECISION);
        a[2] = 6.0;
        CPPUNIT_ASSERT_DOUBLES_EQUAL(median(a, 5), 4.0, PRECISION);
    }

    void test_is_onset() {
        RTOnsetDetection od; 
        CPPUNIT_ASSERT(!od.is_onset(0.1));
        CPPUNIT_ASSERT(!od.is_onset(0.6));
        CPPUNIT_ASSERT(!od.is_onset(0.7));
        CPPUNIT_ASSERT(od.is_onset(0.5));
    }

public:
    void setUp() {
        a = new sample[5];
        for(int i = 0; i < 5; i++) {
            a[i] = 0.f;
        }
    }

    void tearDown() {
        delete[] a;
    } 
};

CPPUNIT_TEST_SUITE_REGISTRATION(TestOnsetDetection);

int main(int arg, char **argv) {
    CppUnit::TextTestRunner runner;
    runner.addTest(CppUnit::TestFactoryRegistry::getRegistry().makeTest());
    return runner.run("", false);
}
