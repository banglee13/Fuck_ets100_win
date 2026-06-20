@echo off
chcp 65001 >nul
echo 开始打包 FuckETS100...

pyinstaller --onefile --windowed --name "FuckETS100" --icon="logo.ico" --add-data "src;src" --hidden-import=requests --hidden-import=pyzipper --hidden-import=dotenv.main --hidden-import=PyQt6 --hidden-import=PyQt6.QtCore --hidden-import=PyQt6.QtWidgets --hidden-import=PyQt6.QtGui --hidden-import=PyQt6.QtWebEngineWidgets --hidden-import=PyQt6.QtWebEngineCore main.py

echo.
echo 打包完成！exe 文件在 dist\FuckETS100.exe
pause
