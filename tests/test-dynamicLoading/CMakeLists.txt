cmake_minimum_required(VERSION 3.5)
project(test-dynamicLoading)

set(CMAKE_CXX_STANDARD 11)

find_package(glfw3 REQUIRED)

add_executable(test-dynamicLoading "main.cpp" include/KHR/khrplatform.h include/oglhpp/GL.h)
target_include_directories(test-dynamicLoading PUBLIC "include/")
target_link_libraries(test-dynamicLoading PRIVATE glfw)
target_include_directories(test-dynamicLoading PRIVATE ${GLFW_INCLUDE_DIRS})
