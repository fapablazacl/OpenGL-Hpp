
project (test-gl10)

set(CMAKE_CXX_STANDARD 11)
add_executable(test-gl10 gl.hpp test-gl10.cpp "glad-gl/src/glad.c")
target_include_directories(test-gl10 PUBLIC "glad-gl/include/")
