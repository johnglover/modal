#include <cppunit/ui/text/TextTestRunner.h>
#include <cppunit/extensions/HelperMacros.h>
#include <cppunit/extensions/TestFactoryRegistry.h>

#include "test_detectionfunctions.h"
#include "test_onsetdetection.h"
 
CPPUNIT_TEST_SUITE_REGISTRATION(modal::TestOnsetDetection);
CPPUNIT_TEST_SUITE_REGISTRATION(modal::TestPeakODF);

int main(int arg, char **argv) {
    CppUnit::TextTestRunner runner;
    runner.addTest(CppUnit::TestFactoryRegistry::getRegistry().makeTest());
    return runner.run("", false);
}
