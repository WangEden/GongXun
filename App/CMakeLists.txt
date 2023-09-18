project(app)

message(STATUS "This is BINARY dir " ${HELLO_BINARY_DIR})
message(STATUS "This is SOURCE dir " ${HELLO_SOURCE_DIR})
add_executable(${PROJECT_NAME} main.cpp)

# add_subdirectory(utils)

# set(CMAKE_AUTOUIC ON)
# set(CMAKE_AUTOMOC ON)
# set(CMAKE_AUTORCC ON)

# set(CMAKE_CXX_STANDARD 17)
# set(CMAKE_CXX_STANDARD_REQUIRED ON)

# set(OpenCV_DIR D:/JumBoKits/OpenCV454/build)

# set(PROJECT_SOURCES
#     main.cpp
#     utils/utils.hpp utils/utils.cpp
# )

# include_directories(${OpenCV_DIR}/include)
# link_directories(${OpenCV_DIR}/lib)
# find_package(OpenCV 4.5.4 REQUIRED)

# target_link_libraries(App
#   PRIVATE ${OpenCV_LIBS}
# )

# install(TARGETS DustbinWithQT5
#     BUNDLE DESTINATION .
#     LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}
# )