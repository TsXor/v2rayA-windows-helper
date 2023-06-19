#include "hook_minimize_button.h"

#define ASSERT_(expr, errmsg) if (!(expr)) {printf(errmsg); abort();}

static HMODULE _hLib;

int IsOriginalWindow(HWND hwnd, DWORD processID) {
    return (IsWindow(hwnd) && (GetWindowThreadProcessId(hwnd, NULL) == processID));
}

int main(int argc, char *argv[]) {
    ASSERT_(argc == 2, "Wrong number of arguments.");
    
    char *endptr; unsigned long long input_hwnd = strtoull(argv[1], &endptr, 10);
    HWND target_hwnd = (HWND)input_hwnd;
    ASSERT_(IsWindow(target_hwnd), "Invalid window handle.");
    
	HMENU hmenu = GetSystemMenu(target_hwnd, false);
	RemoveMenu(hmenu, SC_CLOSE, MF_BYCOMMAND);

    DWORD processID = GetWindowThreadProcessId(target_hwnd, NULL);
    ASSERT_(_hLib = LoadLibrary((LPCSTR_T)_T("hook_minimize_button_dll.dll")), "Error loading hook_minimize_button_dll.dll.");
    ASSERT_(RegisterHook(processID, _hLib), "Error setting hook procedure.");
    while (IsOriginalWindow(target_hwnd, processID)) {
        Sleep(1000);
    }
    
    return 0;
}

