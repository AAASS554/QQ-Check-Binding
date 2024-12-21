@echo off
chcp 65001
echo 正在清理缓存...
for %%i in (build,dist,__pycache__,src\__pycache__,src\utils\__pycache__) do (
    if exist %%i rmdir /s /q %%i 2>nul
)
if exist *.spec del /f /q *.spec 2>nul

echo 正在清理旧文件...
rmdir /s /q build dist

echo 正在打包程序...
rem 打包主程序
pyinstaller ^
    --clean ^
    --onefile ^
    --noconsole ^
    --icon=icon.ico ^
    --add-data "src/utils/*;utils" ^
    --hidden-import PyQt5.QtCore ^
    --hidden-import PyQt5.QtWidgets ^
    --hidden-import requests ^
    --hidden-import pymysql ^
    --hidden-import Crypto ^
    --hidden-import psutil ^
    --hidden-import win32gui ^
    --hidden-import win32process ^
    --hidden-import winreg ^
    --name "QQ查询工具" ^
    src/main.py

rem 打包管理工具
pyinstaller ^
    --clean ^
    --onefile ^
    --noconsole ^
    --icon=icon.ico ^
    --add-data "src/utils/*;utils" ^
    --hidden-import PyQt5.QtCore ^
    --hidden-import PyQt5.QtWidgets ^
    --hidden-import pymysql ^
    --name "卡密管理工具" ^
    src/admin.py

echo 打包完成！
pause 