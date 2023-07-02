# OpenWebview2Window  
一个简易程序，用途是在独立的Edge Webview窗口中打开一个网址。  
简易修改自[EdgeBrowserByAyush](https://www.codeproject.com/Tips/5287858/WebView2-Edge-Browser-in-MFC-Cplusplus-application)。  
每次启动会自动使用上次保存的窗口位置或默认居中。  


## 启动参数  
```
EdgeBrowserApp.exe
    --userdata-path /path/to/userdata
    --navigate-url https://www.example.com
    --window-title TITLE
```
参数都必须给出。  
使用例：  
```
EdgeBrowserApp.exe --userdata-path E:\Users\23Xor\Downloads\EdgeBrowserByAyush\x64\Release\webdata --navigate-url https://www.baidu.com --window-title 百度一下
```
如果文件夹名带空格，需要加双引号，如：  
```
EdgeBrowserApp.exe --userdata-path "E:\Users\AUSER\Downloads\path with space\webdata" --navigate-url https://www.baidu.com --window-title 百度一下
```


## 注意  
原版[EdgeBrowserByAyush](https://www.codeproject.com/Tips/5287858/WebView2-Edge-Browser-in-MFC-Cplusplus-application)并没有启用窗口的最大化和最小化按钮，本来这个“问题”在VS的Dialog Editor中编辑一下就可以解决，但是由于VS占空间太大，我只装了生成工具，于是我最终通过编程的方式在窗口初始化时启用了最大化和最小化按钮。  
如果您需要定制窗口右上角的三个按钮，请在`EdgeBrowserApp\EdgeBrowserAppDlg.cpp`中搜索以下注释：  
```c++
// enable maximize and minimize button (so sorry I don't have a VS installation)
```
然后删去这条注释和它的下两行。  