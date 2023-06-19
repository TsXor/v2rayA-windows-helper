# hook-minimize-button  
命令行程序，作用是禁用一个窗口的关闭键，并且使这个窗口在最小化时隐藏。  
很明显，只适用于Windows。

## 用法  
```
hook-minimize-button.bat <窗口句柄>
```
这样将会同时启动32位和64位版本，以保证成功hook窗口。  
你也可以用同样的方法单独启动32位或者64位的版本。  

## 编译
```
cmake_build.bat Release
```
编译结果将放在`dist`下。  