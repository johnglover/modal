cmake_minimum_required(VERSION 2.6)
project(modal)

set(source_files modal/detectionfunctions/mq.cpp
                 modal/detectionfunctions/detectionfunctions.cpp
                 src/onsetdetection.cpp
                 src/exceptions.cpp)

set(include_files modal/detectionfunctions/mq.h
                  modal/detectionfunctions/detectionfunctions.h
                  src/onsetdetection.h
                  src/exceptions.h)

include_directories(modal/detectionfunctions src)
add_library(modal SHARED ${source_files})
target_link_libraries(modal m fftw3)

install(TARGETS modal LIBRARY DESTINATION lib)
install(FILES ${include_files} DESTINATION include/modal)


# ----------------------------------------------------------------------------
# Tests
# ----------------------------------------------------------------------------
if(BUILD_TESTS)
    set(test_src src/onsetdetection.cpp
                 src/exceptions.cpp
                 modal/detectionfunctions/mq.cpp
                 modal/detectionfunctions/detectionfunctions.cpp
                 tests/cpp/tests.cpp
                 tests/cpp/test_detectionfunctions.cpp
                 tests/cpp/test_onsetdetection.cpp)
    add_executable(tests ${test_src})
    target_link_libraries(tests cppunit sndfile m fftw3)
else()
    message("-- Not building tests. To change run CMake with -D BUILD_TESTS=yes")
endif()
