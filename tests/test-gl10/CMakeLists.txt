
project (test-gl10)

find_library(glfw3 REQUIRED)

add_executable(test-gl10 gl.hpp test-gl10.cpp)
