# v2rayA-windows-helper  
让v2rayA看起来比较像正常的Windows GUI应用  

## 功能  
显示一个托盘图标，并且用单独的webview窗口显示V2rayA Web UI，退出时处理设置。  

## 编译与打包
由于`nuitka`目前的发行版本不能成功打包`clr`，所以需要安装开发版的`nuitka`。  
```
cd packer
pack.py
```
将在`packer`下产生`dist.zip`。  