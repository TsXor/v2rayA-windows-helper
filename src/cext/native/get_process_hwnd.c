#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include "get_process_hwnd.h"

#pragma comment (lib, "user32.lib")  

struct handle_data {
    unsigned long process_id;
    HWND best_handle;
};

static BOOL IsMainWindow(HWND handle) {
    return GetWindow(handle, GW_OWNER) == (HWND)0
        && IsWindowVisible(handle);
}

static BOOL CALLBACK EnumWindowsCallback(HWND handle, LPARAM lParam) {
    struct handle_data* data = (struct handle_data *)lParam;
    unsigned long process_id = 0;
    GetWindowThreadProcessId(handle, &process_id);
    if (data->process_id != process_id
     || !IsMainWindow(handle)) {
        return TRUE;
    }
    data->best_handle = handle;
    return FALSE;
}

void* FindMainWindow(unsigned long process_id) {
    struct handle_data data;
    data.process_id = process_id;
    data.best_handle = 0;
    EnumWindows(EnumWindowsCallback, (LPARAM)&data);
    return data.best_handle;
}
