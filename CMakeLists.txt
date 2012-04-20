cmake_minimum_required(VERSION 2.6)
project(modal)

set(source_files modal/detectionfunctions/mq.cpp 
                 modal/detectionfunctions/detectionfunctions.cpp)
set(include_files modal/detectionfunctions/mq.h 
                  modal/detectionfunctions/detectionfunctions.h)

include_directories(modal/detectionfunctions)
add_library(modal SHARED ${source_files})
target_link_libraries(modal m fftw3)

install(TARGETS modal LIBRARY DESTINATION lib)
install(FILES ${include_files} DESTINATION include/modal)
