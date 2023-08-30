cmake_minimum_required(VERSION 3.15)


set(AVAILABLE_ARCH "x32" "x64")
# default to x64
if (NOT DEFINED ARCH)
    message(STATUS "default ARCH to x64")
    set(ARCH "x64")
endif()
string(SUBSTRING ${ARCH} 1 -1 ARCH_N)
# architecture check
list(FIND AVAILABLE_ARCH ${ARCH} avail_state)
if (${avail_state} EQUAL -1)
    message(FATAL_ERROR "unsupported architecture")
endif()

function(import_extern_dll target_name dll_name path)
    if(MSVC)
        set(lib_type SHARED)
    else()
        set(lib_type MODULE)
    endif()
    if(${path} STREQUAL MS_BUILTIN)
        if(MSVC)
            set(dll_path ${dll_name}.dll)
            set(lib_path ${dll_name}.lib)
        else()
            if(${ARCH} STREQUAL "x32" AND ${CMAKE_HOST_SYSTEM_PROCESSOR} STREQUAL "AMD64")
                set(dll_path C:/Windows/SysWoW64/${dll_name}.dll)
                set(lib_path C:/Windows/SysWoW64/${dll_name}.lib)
            else()
                set(dll_path C:/Windows/System32/${dll_name}.dll)
                set(lib_path C:/Windows/System32/${dll_name}.lib)
            endif()
        endif()
    else()
        set(dll_path ${path}/${dll_name}.dll)
        set(lib_path ${path}/${dll_name}.lib)
    endif()
    add_library(${target_name} ${lib_type} IMPORTED)
    set_property(TARGET ${target_name} PROPERTY
                IMPORTED_LOCATION ${dll_path})
    set_property(TARGET ${target_name} PROPERTY
                IMPORTED_IMPLIB ${lib_path})
endfunction()


project(OpenWebview2Window)

import_extern_dll(winlib_shlwapi shlwapi MS_BUILTIN)
import_extern_dll(Webview2 WebView2Loader ${CMAKE_CURRENT_LIST_DIR}/extlibs/Microsoft.Web.Webview/lib/${ARCH})

add_executable(${PROJECT_NAME} WIN32
    ${CMAKE_CURRENT_LIST_DIR}/src/main.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/wargv.cpp)
target_link_libraries(${PROJECT_NAME} version)
target_link_libraries(${PROJECT_NAME} winlib_shlwapi)
target_include_directories(${PROJECT_NAME} PRIVATE
        ${CMAKE_CURRENT_LIST_DIR}/extlibs/Microsoft.Web.Webview/include)
target_link_libraries(${PROJECT_NAME} Webview2)
target_include_directories(${PROJECT_NAME} PRIVATE
        ${CMAKE_CURRENT_LIST_DIR}/extlibs/webview/include)
install(TARGETS ${PROJECT_NAME}
        DESTINATION ${CMAKE_CURRENT_LIST_DIR}/dist/bin/${ARCH})
