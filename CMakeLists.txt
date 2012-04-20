cmake_minimum_required(VERSION 2.6)
project(modal)

set(source_files modal/detectionfunctions/mq.cpp
                 modal/detectionfunctions/detectionfunctions.cpp
                 src/onsetdetection.cpp)

set(include_files modal/detectionfunctions/mq.h
                  modal/detectionfunctions/detectionfunctions.h
                  src/onsetdetection.h)

include_directories(modal/detectionfunctions src)
add_library(modal SHARED ${source_files})
target_link_libraries(modal m fftw3)

install(TARGETS modal LIBRARY DESTINATION lib)
install(FILES ${include_files} DESTINATION include/modal)

set(test_source_files src/onsetdetection.cpp
                      tests/cpp/test_onsetdetection.cpp)
add_executable(test_onsetdetection ${test_source_files})
target_link_libraries(test_onsetdetection cppunit)
