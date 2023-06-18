import winreg, ctypes


WINREG_PROXY_SETTINGS_ROOT = winreg.HKEY_CURRENT_USER
WINREG_PROXY_SETTINGS_PATH = r'Software\Microsoft\Windows\CurrentVersion\Internet Settings'
PROXY_OVERRIDE_DEFAULT = 'localhost;127.*;10.*;172.16.*;172.17.*;172.18.*;172.19.*;172.20.*;172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;172.27.*;172.28.*;172.29.*;172.30.*;172.31.*;192.168.*;<local>'


class WinRegDir:
    def __init__(self, root, path: str, access: int):
        #self.handle = winreg.OpenKeyEx(root, path, 0, access)
        self.handle = winreg.CreateKeyEx(root, path, 0, access) # key may not exist
    
    def close(self):
        self.handle.Close()

    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.handle.Close()

    def read(self, name: str):
        reg_val, _ = winreg.QueryValueEx(self.handle, name)
        return reg_val
    
    def write(self, name: str, value):
        _, reg_type = winreg.QueryValueEx(self.handle, name)
        winreg.SetValueEx(self.handle, name, 0, reg_type, value)


def get_proxy_settings_reg():
    return WinRegDir(WINREG_PROXY_SETTINGS_ROOT, WINREG_PROXY_SETTINGS_PATH, winreg.KEY_ALL_ACCESS)

def flush_internet_settings():
    INTERNET_OPTION_REFRESH = 37
    INTERNET_OPTION_SETTINGS_CHANGED = 39
    InternetSetOptionW = ctypes.windll.Wininet.InternetSetOptionW
    InternetSetOptionW(0, INTERNET_OPTION_REFRESH, 0, 0)
    InternetSetOptionW(0, INTERNET_OPTION_SETTINGS_CHANGED, 0, 0)

def open_proxy(addr: str):
    with get_proxy_settings_reg() as proxy_settings_reg:
        proxy_settings_reg.write('ProxyEnable', 1)
        proxy_settings_reg.write('ProxyOverride', PROXY_OVERRIDE_DEFAULT)
        proxy_settings_reg.write('ProxyServer', addr)
    flush_internet_settings()

def close_proxy(clear_addr=False):
    with get_proxy_settings_reg() as proxy_settings_reg:
        proxy_settings_reg.write('ProxyEnable', 0)
        if clear_addr: proxy_settings_reg.write('ProxyServer', '')
    flush_internet_settings()