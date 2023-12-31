import sys, os, subprocess, time
from pathlib import Path
from socket import socket
import pystray, win32gui, win32con
from fake_image_class import FakeImage
from proxy_setter import close_proxy


SELF_PATH = Path(sys.argv[0])

TIME_TEMPLATE = '%Y-%m-%d_%H-%M-%S'
MAX_WAIT_TIME = 5
SP_NOCONSOLE = subprocess.STARTUPINFO()
SP_NOCONSOLE.dwFlags = subprocess.CREATE_NEW_CONSOLE | subprocess.STARTF_USESHOWWINDOW
SP_NOCONSOLE.wShowWindow = subprocess.SW_HIDE
WINDOW_TITLE = 'V2rayA Web UI'
V2RAYA_DEFAULT_PORT = 2017
LOOPBACK_ADDR = '127.0.0.1'


def get_available_port(addr: str, start_from: int):
    s = socket()
    port = start_from
    while True:
        try:
            s.bind((addr, port))
            break
        except OSError:
            port += 1
    s.close()
    return port

def ensure_directory(dirp: Path):
    dirp.mkdir(parents=True, exist_ok=True)
    return dirp

def ensure_file(dirp: Path, globs: list[str]):
    ensure_directory(dirp)
    available_paths: list[Path] = []
    for glob in globs:
        try:
            available_paths.append(list(dirp.glob(glob))[0])
        except IndexError:
            pass
    if available_paths:
        return available_paths[0]
    else:
        raise FileNotFoundError('target file not found', dirp, globs)

def all_to_string(*args):
    return [arg if isinstance(arg, str) else str(arg) for arg in args]


class v2rayaApplication:
    def __init__(self, app_root: Path, ui_port=V2RAYA_DEFAULT_PORT, n_max_logs=10):
        self._alive = True
        self.app_root = app_root
        self.ui_port = get_available_port(LOOPBACK_ADDR, ui_port)
        if self.ui_port != ui_port: print(f'Port {ui_port} unavailable, changed to {self.ui_port}.')
        self.n_max_logs = n_max_logs

        # find paths
        v2raya_executable_path = ensure_file(self.app_root / 'v2raya', ['v2raya*.exe'])
        v2raya_config_dir      = ensure_directory(self.app_root / 'v2raya' / 'config')
        v2raya_log_dir         = ensure_directory(self.app_root / 'v2raya' / 'logs')
        vcore_executable_path  = ensure_file(self.app_root / 'vcore', ['v2ray.exe', 'xray.exe'])
        vcore_asset_dir        = ensure_directory(self.app_root / 'vcore')
        vcore_config_dir       = ensure_directory(self.app_root / 'vcore' / 'config')
        helper_config_dir      = ensure_directory(self.app_root / 'chore-worker' / 'config')
        open_webview_path      = ensure_file(self.app_root / 'chore-worker' / 'OpenWebview2Window', ['OpenWebview2Window.exe'])

        # save some paths for future use
        self.vcore_executable_path = vcore_executable_path
        self.helper_config_dir     = helper_config_dir
        self.v2raya_log_dir        = v2raya_log_dir
        self.open_webview_path     = open_webview_path

        self.logfile_fp = self.open_new_log_fp()
        self.clean_logs()

        self.process = subprocess.Popen(
            all_to_string(
                v2raya_executable_path, '--lite',
                '--address',         f'0.0.0.0:{self.ui_port}',
                '--v2ray-bin',       vcore_executable_path,
                '--config',          v2raya_config_dir,
                '--v2ray-confdir',   vcore_config_dir,
                '--v2ray-assetsdir', vcore_asset_dir,
            ),
            stdout=self.logfile_fp,
            startupinfo=SP_NOCONSOLE,
        )
        self.start_webview_process()

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

    def start_webview_process(self):
        os.chdir(self.helper_config_dir)
        self.webview_process = subprocess.Popen(
            all_to_string(
                self.open_webview_path,
                '--userdata-path', self.helper_config_dir,
                '--navigate-url',  f'http://{LOOPBACK_ADDR}:{self.ui_port}',
                '--window-title', WINDOW_TITLE,
                '--tray-control',
            ),
            stdout=subprocess.PIPE
        )
        hwnd_bytestr: bytes = b''
        while True:
            hwnd_bytechr: bytes = self.webview_process.stdout.read(1)
            if hwnd_bytechr == b' ': break
            hwnd_bytestr += hwnd_bytechr
        hwnd_str = hwnd_bytestr.decode()
        self.webview_hwnd = int(hwnd_str)
        print(f'webview window hwnd: {self.webview_hwnd}')
    
    def open_webview_window(self):
        if self.webview_process.poll() is None:
            win32gui.ShowWindow(self.webview_hwnd, win32con.SW_SHOWNORMAL)
            win32gui.SetForegroundWindow(self.webview_hwnd)
        else:
            self.start_webview_process()
    
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
        icon_path = app_root / 'chore-worker' / 'v2raya_icon.ico'
        menu = (
            pystray.MenuItem(text='打开V2rayA Web UI', action=self.app.open_webview_window, default=True),
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
    console_log_dir = SELF_PATH.parent / 'console_log'
    console_log_dir.mkdir(parents=True, exist_ok=True)
    sys.stdout = open(console_log_dir / 'stdout', 'wt')
    sys.stderr = open(console_log_dir / 'stderr', 'wt')
    ROOT_DIR = SELF_PATH.parents[1]
    v2rayaTray(ROOT_DIR)