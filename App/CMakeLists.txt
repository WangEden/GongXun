cmake_minimum_required(VERSION 3.0.0)
project(app VERSION 0.1.0 LANGUAGES C CXX)

set(OpenCV_DIR "D:/JumBoKits/OpenCV454/build")
find_package(OpenCV REQUIRED)
include_directories(${OpenCV_INCLUDE_DIRS})
link_directories(${OpenCV_DIR}/lib)

set(CPACK_PROJECT_NAME ${PROJECT_NAME})
set(CPACK_PROJECT_VERSION ${PROJECT_VERSION})

add_executable(app main.cpp)

target_link_libraries(${PROJECT_NAME}
  ${OpenCV_LIBS}
)