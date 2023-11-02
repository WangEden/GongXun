cmake_minimum_required(VERSION 3.0.0)
project(GongXun VERSION 0.1.0 LANGUAGES C CXX)

set(CMAKE_CXX_FLAGS "-std=c++11")

include(CTest)
option(BUILD_TEST "Whether or not to build the tests" ON)
if (${BUILD_TEST})
    message(STATUS "Building tests")
    enable_testing()  # Enable testing only works in root scope
endif ()

add_executable(${PROJECT_NAME} 
    src/Inc/main_program.h src/main.cpp
)

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})
include(CPack)

# Set OpenCV dirctory
set(OpenCV_DIR D:/JumBoKits/OpenCV454/build)

# import OpenCV lib
find_package(OpenCV 4.5.4 REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})
# link_directories(${OpenCV_LIBS})

target_link_libraries(${PROJECT_NAME}
  ${OpenCV_LIBS}
)
