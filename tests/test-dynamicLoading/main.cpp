
#include <oglhpp/gl.h>
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
    oglhpp_load_functions(glfwGetProcAddress);

    // Set GLFW error callback
    glfwSetErrorCallback(errorCallback);


    float vertices[] = {
        -0.5f, -0.5f, 0.0f,
         0.5f, -0.5f, 0.0f,
         0.0f,  0.5f, 0.0f
    };  

    // Main loop
    while (!glfwWindowShouldClose(window)) {
        glfwPollEvents();

        glClearColor(0.2f, 0.4f, 0.8f, 1.0f);
        assert(glGetError() == GL_NO_ERROR);

        glClear(GL_COLOR_BUFFER_BIT);
        assert(glGetError() == GL_NO_ERROR);
        
        /*
        glBegin(GL_TRIANGLE_STRIP);
        glVertex3f(0.0f, 0.5f, 0.0f);        
        glVertex3f(-0.5f, 0.0f, 0.0f);
        glVertex3f(0.5f, 0.0f, 0.0f);
        glEnd();
        */
        assert(glGetError() == GL_NO_ERROR);

        glFlush();
        glfwSwapBuffers(window);
    }


    // Clean up
    glfwDestroyWindow(window);
    glfwTerminate();

    return 0;
}
