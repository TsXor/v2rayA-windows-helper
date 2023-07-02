cmake_minimum_required(VERSION 3.15)

project(hook_minimize_button)

add_library(hook_minimize_button_dll SHARED hook_minimize_button_dll.cpp)
add_executable(hook_minimize_button hook_minimize_button.cpp)
target_link_libraries(hook_minimize_button hook_minimize_button_dll)

install(TARGETS hook_minimize_button
        DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist/${ARCH})
install(TARGETS hook_minimize_button_dll
        DESTINATION ${CMAKE_CURRENT_SOURCE_DIR}/dist/${ARCH})