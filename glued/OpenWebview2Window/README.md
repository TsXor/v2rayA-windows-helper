# OpenWebview2Window  
一个简易程序，用途是在独立的Edge Webview窗口中打开一个网址。  
目前使用[webview](https://github.com/webview/webview)的个人修改版本实现。  
每次启动默认居中。  


## 启动参数  
```
EdgeBrowserApp.exe
    --userdata-path /path/to/userdata
    --navigate-url https://www.example.com
    --window-title TITLE
    --tray-control
```
参数均为可选。
- 若不填`--navigate-url`，此窗口不会打开任何页面，表现为白屏。  
- 若不填`--userdata-path`，用户数据会被存到`webview`自动选择的位置，目前为`%APPDATA%\[程序名]`。  
- 若不填`--window-title`，标题为空。  
- 若打开`--tray-control`开关，窗口将禁用关闭键，在最小化时自动隐藏，并在启动时输出主窗口句柄，此功能是为了方便Python胶水。  
  
使用例：  
```
EdgeBrowserApp.exe --userdata-path E:\Users\23Xor\Desktop\OpenWebview2Window-ng\dist\bin\x64\webdata --navigate-url https://www.baidu.com --window-title 百度一下
```
如果文件夹名带空格，需要加双引号，如：  
```
EdgeBrowserApp.exe --userdata-path "E:\Users\AUSER\Downloads\path with space\webdata" --navigate-url https://www.baidu.com --window-title 百度一下
```


## Python胶水
由于浏览器内部的多进程和启动器机制，用win32api获取的hwnd一般不准确。  
本程序在打开`--tray-control`开关时会输出hwnd，在Python中可以利用`Popen::stdout`读取。  
输出的hwnd会以空格结尾。  

使用例：  
```python
p = subprocess.Popen(
    [
        r'E:\Users\23Xor\Desktop\OpenWebview2Window.exe',
        '--userdata-path', r'E:\Users\23Xor\Desktop\ebdata',
        '--navigate-url', 'https://www.baidu.com',
        '--window-title', 'baidu',
        '--tray-control'
    ],
    stdout=subprocess.PIPE
)
hwnd_bytestr: bytes = b''
while True:
    hwnd_bytechr: bytes = p.stdout.read(1)
    if hwnd_bytechr == b' ': break
    hwnd_bytestr += hwnd_bytechr
hwnd_str = hwnd_bytestr.decode()
hwnd = int(hwnd_str)
```


## 注意  
目前`webview`暂不支持指定用户数据存放位置，本项目自行修改添加了这个功能。  
