#include "hook_minimize_button.h"

static HHOOK _hMinimizeHook = NULL;

LRESULT CALLBACK HookMinimizeProc(int nCode, WPARAM wParam, LPARAM lParam) {
    if (nCode < 0) {goto FN_END;}
    
    CWPRETSTRUCT *msg = (CWPRETSTRUCT *)lParam;
    HWND hwnd = msg->hwnd;
    if ((UINT)GetWindowLongPtr(hwnd, GWL_STYLE) & WS_CHILD) {
        hwnd = GetAncestor(hwnd, GA_ROOT);
    }
    
    switch (msg->message) {
        case WM_SYSCOMMAND:
            if (msg->wParam == SC_MINIMIZE) {
                ShowWindow(hwnd, SW_HIDE);
            }
            break;
        case WM_DESTROY:
            UnRegisterHook();
        default:
            break;
    }
    
    FN_END: return CallNextHookEx(_hMinimizeHook, nCode, wParam, lParam);
}

BOOL DLLIMPORT RegisterHook(DWORD processID, HMODULE hLib) {
    _hMinimizeHook = SetWindowsHookEx(WH_CALLWNDPROCRET, (HOOKPROC)HookMinimizeProc, hLib, processID);
    if (_hMinimizeHook == NULL) {
        UnRegisterHook();
        return FALSE;
    }
    return TRUE;
}

void DLLIMPORT UnRegisterHook() {
    if (_hMinimizeHook) {
        UnhookWindowsHookEx(_hMinimizeHook);
        _hMinimizeHook = NULL;
    }
}