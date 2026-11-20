@echo off
chcp 65001 >nul
echo 正在构建番茄钟应用...

python -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name "PomodoroTaskbar" ^
    --icon "assets/app.ico" ^
    --add-data "sound;sound" ^
    --add-data "assets;assets" ^
    --exclude-module=pygame ^
    --exclude-module=numpy ^
    --exclude-module=scipy ^
    --exclude-module=matplotlib ^
    --exclude-module=PIL ^
    --exclude-module=Pillow ^
    --exclude-module=pandas ^
    --exclude-module=tkinter ^
    --exclude-module=unittest ^
    --exclude-module=IPython ^
    --exclude-module=jupyter ^
    --exclude-module=PySide6.QtWebEngineCore ^
    --exclude-module=PySide6.QtWebEngineWidgets ^
    --exclude-module=PySide6.QtWebChannel ^
    --exclude-module=PySide6.QtQml ^
    --exclude-module=PySide6.QtQuick ^
    --exclude-module=PySide6.QtQuickWidgets ^
    --exclude-module=PySide6.QtQuickControls2 ^
    --exclude-module=PySide6.QtNetwork ^
    --exclude-module=PySide6.QtSql ^
    --exclude-module=PySide6.QtTest ^
    --exclude-module=PySide6.QtXml ^
    --exclude-module=PySide6.QtOpenGL ^
    --exclude-module=PySide6.QtOpenGLWidgets ^
    --exclude-module=PySide6.QtPrintSupport ^
    --exclude-module=PySide6.QtSvg ^
    --exclude-module=PySide6.QtSvgWidgets ^
    --exclude-module=PySide6.QtPdf ^
    --exclude-module=PySide6.QtPdfWidgets ^
    --exclude-module=PySide6.QtMultimedia ^
    --exclude-module=PySide6.QtMultimediaWidgets ^
    --exclude-module=PySide6.Qt3DCore ^
    --exclude-module=PySide6.Qt3DRender ^
    --exclude-module=PySide6.QtCharts ^
    --exclude-module=PySide6.QtDataVisualization ^
    --exclude-module=PySide6.QtDesigner ^
    --exclude-module=PySide6.QtHelp ^
    --exclude-module=PySide6.QtBluetooth ^
    --exclude-module=PySide6.QtConcurrent ^
    --exclude-module=PySide6.QtNfc ^
    --exclude-module=PySide6.QtPositioning ^
    --exclude-module=PySide6.QtSensors ^
    --exclude-module=PySide6.QtSerialPort ^
    --exclude-module=PySide6.QtTextToSpeech ^
    --exclude-module=PySide6.QtWebSockets ^
    main.py

if %ERRORLEVEL% NEQ 0 (
    echo 构建失败。
    pause
    exit /b 1
)

echo.
echo 构建完成！
echo EXE 文件位于 dist\PomodoroTaskbar.exe
pause
