import sys, subprocess, time
from pathlib import Path
import pystray, win32gui, win32con
from fake_image_class import FakeImage
from proxy_setter import close_proxy


SELF_PATH = Path(sys.argv[0])
PY_EXEC_SUFFIX = SELF_PATH.suffix

TIME_TEMPLATE = '%Y-%m-%d_%H-%M-%S'
MAX_WAIT_TIME = 5
SP_NOCONSOLE = subprocess.STARTUPINFO()
SP_NOCONSOLE.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
SP_NOCONSOLE.wShowWindow = subprocess.SW_HIDE


class v2rayaApplication:
    def __init__(self, app_root: Path, ui_port=2017, n_max_logs=10):
        self._alive = True
        self.app_root = app_root
        self.ui_port = ui_port
        self.n_max_logs = n_max_logs

        v2raya_executable_path, \
        v2raya_config_dir, \
        v2raya_log_dir, \
        vcore_executable_path, \
        vcore_asset_dir, \
        vcore_config_dir, \
        helper_config_dir, \
        open_webview_path, \
        hook_minimize_button_path  = self.find_paths()

        self.vcore_executable_path = vcore_executable_path
        self.helper_config_dir = helper_config_dir
        self.v2raya_log_dir = v2raya_log_dir
        self.open_webview_path = open_webview_path
        self.hook_minimize_button_path = hook_minimize_button_path

        self.logfile_fp = self.open_new_log_fp()
        self.clean_logs()

        self.process = subprocess.Popen(
            [
                str(v2raya_executable_path), '--lite',
                '--address', f'0.0.0.0:{ui_port}',
                '--v2ray-bin', str(vcore_executable_path),
                '--config', str(v2raya_config_dir),
                '--v2ray-confdir', str(vcore_config_dir),
                '--v2ray-assetsdir', str(vcore_asset_dir),
            ],
            stdout=self.logfile_fp,
            startupinfo=SP_NOCONSOLE,
        )
        self.start_webview()
    
    def find_paths(self):
        try: v2raya_executable_path = list((self.app_root / 'v2raya').glob('v2raya*.exe'))[0]
        except: raise EnvironmentError('Executable cannot be found!', 'v2rayA')
        try: 
            vcore_executable_path_X = list((self.app_root / 'vcore').glob('v2ray.exe'))
            vcore_executable_path_V = list((self.app_root / 'vcore').glob('xray.exe'))
            vcore_executable_path = (vcore_executable_path_X + vcore_executable_path_V)[0]
        except: raise EnvironmentError('Executable cannot be found!', 'v2ray core')
        vcore_asset_dir = self.app_root / 'vcore'
        vcore_config_dir = self.app_root / 'vcore' / 'config'
        v2raya_config_dir = self.app_root / 'v2raya' / 'config'
        v2raya_log_dir = self.app_root / 'v2raya' / 'logs'
        helper_config_dir = self.app_root / 'chore-worker' / 'config'
        open_webview_path = self.app_root / 'chore-worker' / f'open_webview{PY_EXEC_SUFFIX}'
        hook_minimize_button_path = self.app_root / 'chore-worker' / 'hook_minimize_button' / 'run.bat'
        return v2raya_executable_path \
             , v2raya_config_dir \
             , v2raya_log_dir \
             , vcore_executable_path \
             , vcore_asset_dir \
             , vcore_config_dir \
             , helper_config_dir \
             , open_webview_path \
             , hook_minimize_button_path

    def open_new_log_fp(self):
        self.cur_logfile_path = self.v2raya_log_dir / f'log_{time.strftime(TIME_TEMPLATE, time.localtime())}.log'
        self.cur_logfile_path.touch()
        return open(self.cur_logfile_path, 'w+')
    
    def clean_logs(self):
        log_paths = list(self.v2raya_log_dir.iterdir())
        log_paths.sort(key=lambda p: time.strptime(p.name[4:-4], TIME_TEMPLATE), reverse=True)
        for i, p in enumerate(log_paths):
            if i >= self.n_max_logs: p.unlink()
    
    def open_cur_log(self):
        subprocess.run(['notepad.exe', str(self.cur_logfile_path)])

    def start_webview(self):
        self.webview_process = subprocess.Popen([str(self.open_webview_path), str(self.helper_config_dir), str(self.ui_port)],
                                               shell=True, startupinfo=SP_NOCONSOLE)
        sleep_time = 0
        while not (webview_hwnd := win32gui.FindWindow(None, 'V2rayA Web UI')):
            time.sleep(0.5); sleep_time += 0.5
            if sleep_time >= MAX_WAIT_TIME: raise EnvironmentError('Webview no response!')
        self.webview_hwnd = webview_hwnd
        subprocess.Popen([str(self.hook_minimize_button_path), str(webview_hwnd)],
                         shell=True, startupinfo=SP_NOCONSOLE)
    
    def webview_ui(self):
        if self.webview_process.poll() is None:
            win32gui.ShowWindow(self.webview_hwnd, win32con.SW_SHOWNORMAL)
            win32gui.SetForegroundWindow(self.webview_hwnd)
        else:
            self.start_webview()
    
    def close(self):
        self.process.kill()
        self.logfile_fp.close()
        subprocess.run(['taskkill', '/f', '/im', str(self.vcore_executable_path.name)],
                       shell=True, startupinfo=SP_NOCONSOLE)
        close_proxy()
        if self.webview_process.poll() is None:
            win32gui.PostMessage(self.webview_hwnd, win32con.WM_CLOSE, 0, 0)
        self._alive = False
    
    def __del__(self):
        if self._alive: self.close()

class v2rayaTray:
    name = "V2rayA"
    desc = "V2rayA tray"

    def __init__(self, app_root: Path, app_config={}):
        self._alive = True
        self.app = v2rayaApplication(app_root, **app_config)
        icon_path = app_root / 'chore-worker' / 'v2raya.ico'
        menu = (
            pystray.MenuItem(text='打开V2rayA Web UI', action=self.app.webview_ui, default=True),
            pystray.MenuItem(text='打开当前日志文件', action=self.app.open_cur_log),
            pystray.MenuItem(text='退出', action=self.exit),
        )
        self.tray = pystray.Icon(self.name, FakeImage.open(icon_path), self.desc, pystray.Menu(*menu))
        self.tray.run()
    
    def exit(self):
        self.app.close()
        self.tray.stop()
        self._alive = False
    
    def __del__(self):
        if self._alive: self.exit()


if __name__ == '__main__':
    ROOT_DIR = SELF_PATH.parents[1]
    v2rayaTray(ROOT_DIR)