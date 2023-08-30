#include <windef.h>
#include <winuser.h>
#include <thread>
#include <cstdio>
#include "option_map.hpp"
#include "wargv.h"
#include "webview.hpp"


#define IDI_APPLICATION_W MAKEINTRESOURCEW(32512)
#define IDC_ARROW_W MAKEINTRESOURCEW(32512)


OptionMapW option_map;

auto naive_u16le_to_acsii(const std::wstring_view& wstr) {
    std::string ret;
    bool is_acsii = true;
    for (auto wchr : wstr) {
        if (wchr > 127) return std::tuple(ret, false);
        ret.push_back(wchr & 0xFF);
    }

    return std::tuple(ret, true);
}

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
            }
            return 0;
        } break;

        default: return CallWindowProc((WNDPROC)OrigWindowProc, hwnd, uMsg, wParam, lParam);
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
    if (!url_w.empty()) {
        auto url_converted = naive_u16le_to_acsii(url_w);
        if (std::get<1>(url_converted)) w.navigate(std::get<0>(url_converted));
    }
    MoveWindow(hwnd, pos.x, pos.y, pos.width, pos.height, true);

    if (tray_control) {
        HMENU hmenu = GetSystemMenu(hwnd, false);
        RemoveMenu(hmenu, SC_CLOSE, MF_BYCOMMAND);
        OrigWindowProc = (WNDPROC)SetWindowLongPtrW(hwnd, GWLP_WNDPROC, (LONG_PTR)HideWhenMinimizeProc);
        wprintf(L"%d", hwnd);
    }

    w.run();

    return 0;
}

