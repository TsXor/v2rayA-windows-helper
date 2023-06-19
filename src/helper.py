import sys

if len(sys.argv) > 1:
    if sys.argv[1] == 'webview':
        from open_webview import open_webview_window
        open_webview_window(); exit()


import subprocess, time
from pathlib import Path
import pystray, win32gui, win32con
from PIL import Image
from proxy_setter import close_proxy


ROOT_DIR = Path(sys.argv[0]).parent.parent
TIME_TEMPLATE = '%Y-%m-%d_%H-%M-%S'
N_MAX_LOGS = 10


class v2rayaApplication:
    def __init__(self, ui_port=2017):
        self.closed = False
        self.webview_process = None
        self.ui_port = ui_port

        try: v2raya_executable_path = list((ROOT_DIR / 'v2raya').glob('v2raya*.exe'))[0]
        except: raise EnvironmentError('v2rayA executable cannot be found!')
        try: vcore_executable_path = (list((ROOT_DIR / 'vcore').glob('xray.exe')) + list((ROOT_DIR / 'vcore').glob('v2ray.exe')))[0]
        except: raise EnvironmentError('v2ray core executable cannot be found!')
        #sysproxy_hook_executable_path = ROOT_DIR / 'chore-worker' / 'v2raya_sysproxy_hook.exe'
        vcore_asset_dir = ROOT_DIR / 'vcore'
        v2raya_config_dir = ROOT_DIR / 'config' / 'v2raya'
        vcore_config_dir = ROOT_DIR / 'config' / 'vcore'

        self.vcore_executable_path = vcore_executable_path

        self.logfile_path = ROOT_DIR / 'logs' / f'log_{time.strftime(TIME_TEMPLATE, time.localtime())}.log'
        self.logfile_path.touch()
        self.logfile_fp = open(self.logfile_path, 'w+')

        self.process = subprocess.Popen(
            [
                str(v2raya_executable_path), '--lite',
                '--address', f'0.0.0.0:{ui_port}',
                '--v2ray-bin', str(vcore_executable_path),
                '--config', str(v2raya_config_dir),
                '--v2ray-confdir', str(vcore_config_dir),
                '--v2ray-assetsdir', str(vcore_asset_dir),
                #'--core-hook', str(sysproxy_hook_executable_path),
            ],
            stdout=self.logfile_fp,
        )
        self.start_webview()
    
    def start_webview(self):
        self.webview_process = subprocess.Popen([sys.argv[0], 'webview', str(self.ui_port)], shell=True)
        while not (webview_hwnd := win32gui.FindWindow(None, 'V2rayA Web UI')): time.sleep(0.5)
        self.webview_hwnd = webview_hwnd
        subprocess.Popen([str(ROOT_DIR / 'chore-worker' / 'hook_minimize_button' / 'hook_minimize_button.bat'), str(webview_hwnd)], shell=True)
    
    def webview_ui(self):
        if self.webview_process.poll() is None:
            win32gui.ShowWindow(self.webview_hwnd, win32con.SW_SHOWNORMAL)
            win32gui.SetForegroundWindow(self.webview_hwnd)
        else:
            self.start_webview()
    
    def close(self):
        self.process.kill()
        self.logfile_fp.close()
        subprocess.run(['taskkill', '/f', '/im', str(self.vcore_executable_path.name)], shell=True)
        close_proxy()
        if self.webview_process.poll() is None:
            win32gui.PostMessage(self.webview_hwnd, win32con.WM_CLOSE, 0, 0)
        self.closed = True
    
    def __del__(self):
        if not self.closed:
            self.close()

class v2rayaTray:
    name = "V2rayA"
    icon_path = ROOT_DIR / 'chore-worker' / 'v2raya.png'
    desc = "V2rayA tray"

    def __init__(self):
        self.app = v2rayaApplication()
        menu = (
            pystray.MenuItem(text='打开V2rayA Web UI', action=self.app.webview_ui, default=True),
            pystray.MenuItem(text='退出', action=self.exit),
        )
        self.tray = pystray.Icon(self.name, Image.open(self.icon_path), self.desc, pystray.Menu(*menu))
        self.tray.run()
    
    def exit(self):
        self.app.close()
        self.tray.stop()


log_paths = list((ROOT_DIR / 'logs').iterdir())
log_paths.sort(key=lambda p: time.strptime(p.name[4:-4], TIME_TEMPLATE), reverse=True)
for i, p in enumerate(log_paths):
    if i >= N_MAX_LOGS: p.unlink()

v2rayaTray()
