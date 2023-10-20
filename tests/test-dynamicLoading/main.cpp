
#include <KHR/khrplatform.h>
#include <oglhpp/GL.h>
#include <GLFW/glfw3.h>
#include <iostream>
#include <cassert>


// GLFW error callback
void errorCallback(int error, const char* description) {
    std::cerr << "GLFW Error: " << description << std::endl;
}


int main() {
    // Initialize GLFW
    if (!glfwInit()) {
        std::cerr << "Failed to initialize GLFW" << std::endl;
        return -1;
    }

    // Set GLFW to use OpenGL 3.3 core profile
    glfwWindowHint(GLFW_CLIENT_API, GLFW_OPENGL_API);
    
    glfwWindowHint(GLFW_CONTEXT_CREATION_API, GLFW_NATIVE_CONTEXT_API);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 3);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_FORWARD_COMPAT, GL_TRUE);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    
    glfwWindowHint(GLFW_DOUBLEBUFFER, GL_TRUE);
    glfwWindowHint(GLFW_RED_BITS, 8);
    glfwWindowHint(GLFW_GREEN_BITS, 8);
    glfwWindowHint(GLFW_BLUE_BITS, 8);
    glfwWindowHint(GLFW_ALPHA_BITS, 8);
    
    // Create a GLFW window
    GLFWwindow* window = glfwCreateWindow(800, 600, "OpenGL App", nullptr, nullptr);
    if (!window) {
        std::cerr << "Failed to create GLFW window" << std::endl;
        glfwTerminate();
        return -1;
    }

    // Make the OpenGL context current
    glfwMakeContextCurrent(window);

    //initialize extensions here
    __glClear = (PFNGLCLEARPROC)glfwGetProcAddress("glClear");
    assert(__glClear);
    __glClearColor = (PFNGLCLEARCOLORPROC)glfwGetProcAddress("glClearColor");
    assert(__glClearColor);
    __glFlush = (PFNGLFLUSHPROC)glfwGetProcAddress("glFlush");
    assert(__glFlush);

    // Set GLFW error callback
    glfwSetErrorCallback(errorCallback);

    // Main loop
    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();

        __glClearColor(0.2f, 0.4f, 0.8f, 1.0f);
        __glClear(GL_COLOR_BUFFER_BIT);

        __glFlush();
        glfwSwapBuffers(window);
    }


    // Clean up
    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}
