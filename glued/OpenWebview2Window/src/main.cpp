#include <windef.h>
#include <winuser.h>
#include <thread>
#include <cstdio>
#include "option_map.hpp"
#include "wargv.h"
#include "webview.hpp"


OptionMapW option_map;

typedef struct window_pos_t_tag {
    int x;
    int y;
    int width;
    int height;
} window_pos_t;

window_pos_t get_middle_pos(void) {
    HDC shdc = GetDC(0);
    int screen_x = GetDeviceCaps(shdc, 118);
    int screen_y = GetDeviceCaps(shdc, 117);
    window_pos_t ret;
    ret.x = screen_x / 4;
    ret.y = screen_y / 4;
    ret.width  = screen_x / 2;
    ret.height = screen_y / 2;
    ReleaseDC(0, shdc);
    return ret;
}

static WNDPROC OrigWindowProc = NULL;

LRESULT CALLBACK HideWhenMinimizeProc(HWND hwnd, UINT uMsg, WPARAM wParam, LPARAM lParam) {
	switch (uMsg) {
        case WM_SYSCOMMAND:{
            if (wParam == SC_MINIMIZE) {
                ShowWindow(hwnd, SW_HIDE);
                return 0;
            } else {
                return CallWindowProcW((WNDPROC)OrigWindowProc, hwnd, uMsg, wParam, lParam);
            }
        } break;

        default: return CallWindowProcW((WNDPROC)OrigWindowProc, hwnd, uMsg, wParam, lParam);
	}
}

int APIENTRY WinMain(
    HINSTANCE hInstance,
    HINSTANCE hPreInstance,
    LPSTR lpCmdLine,
    int nCmdShow
) {
    option_map = OptionMapW(get_argc(), get_wargv());
    
    auto window_title = option_map.get_option(std::wstring_view(L"--window-title"));
    auto pos = get_middle_pos();
    auto url_w = option_map.get_option(std::wstring_view(L"--navigate-url"));
    auto userdata_path = option_map.get_option(std::wstring_view(L"--userdata-path"));
    bool tray_control = option_map.get_flag(std::wstring_view(L"--tray-control"));

    webview::webview w = {false, nullptr, userdata_path};
    auto hwnd = (HWND)w.window();
    SetWindowTextW(hwnd, std::wstring(window_title).c_str());
    auto style = GetWindowLongW(hwnd, GWL_STYLE);
    style |= (WS_THICKFRAME | WS_MAXIMIZEBOX);
    SetWindowLongW(hwnd, GWL_STYLE, style);
    MoveWindow(hwnd, pos.x, pos.y, pos.width, pos.height, true);
    if (!url_w.empty()) {
        auto url_u = webview::detail::narrow_string(std::wstring(url_w));
        if (!url_u.empty()) w.navigate(url_u);
    }

    if (tray_control) {
        HMENU hmenu = GetSystemMenu(hwnd, false);
        RemoveMenu(hmenu, SC_CLOSE, MF_BYCOMMAND);
        OrigWindowProc = (WNDPROC)SetWindowLongPtrW(hwnd, GWLP_WNDPROC, (LONG_PTR)HideWhenMinimizeProc);
        printf("%d ", hwnd);
        fflush(stdout);
    }

    w.run();

    return 0;
}

