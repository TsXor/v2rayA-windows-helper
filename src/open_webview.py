import webview, sys, win32print, win32gui, json
from pathlib import Path


ROOT_DIR = Path(sys.argv[0]).parent.parent


def get_screen_size():
    shdc = win32gui.GetDC(0)
    screen_x = win32print.GetDeviceCaps(shdc, 118)
    screen_y = win32print.GetDeviceCaps(shdc, 117)
    return screen_x, screen_y

def get_default_pos():
    screen_x, screen_y = get_screen_size()
    w_x = round(screen_x / 4)
    w_y = round(screen_y / 4)
    w_width  = round(screen_x / 2)
    w_height = round(screen_y / 2)
    return w_x, w_y, w_width, w_height

def get_pos_range():
    screen_x, screen_y = get_screen_size()
    w_width  = round(screen_x / 16)
    w_height = round(screen_y / 16)
    return (0, screen_x-w_width), (0, screen_y-w_height), (w_width, screen_x+1), (w_height, screen_y+1)

def inrange(x, r):
    rl, rr = r
    return x >= rl and x < rr

def on_closing():
    window = webview.windows[0]
    with open(ROOT_DIR / 'config' / 'chore-worker' / 'last_pos.json', 'w') as last_pos_fp:
        json.dump([window.x, window.y, window.width, window.height], last_pos_fp)

def open_webview_window():
    try:
        with open(ROOT_DIR / 'config' / 'chore-worker' / 'last_pos.json') as last_pos_fp:
            w_size = json.load(last_pos_fp)
        if not all(inrange(s, r) for s, r in zip(w_size, get_pos_range)): raise ValueError
    except:
         w_size = get_default_pos()
    w_x, w_y, w_width, w_height = w_size

    window = webview.create_window('V2rayA Web UI', f'http://127.0.0.1:{sys.argv[2]}',
                                    width=w_width, height=w_height, x=w_x, y=w_y)
    window.events.closing += on_closing
    webview.start(private_mode=False, storage_path=str(ROOT_DIR / 'config' / 'chore-worker' / 'webview'))