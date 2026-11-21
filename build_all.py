# -*- coding: utf-8 -*-
"""跨平台打包脚本：Windows / macOS / Linux 通用，供 GitHub Actions 调用。

用法：python build_all.py
产物：dist/PomodoroTaskbar.exe (Win) / dist/PomodoroTaskbar.app (Mac) / dist/PomodoroTaskbar (Linux)
"""
import platform
import subprocess
import sys
import os

# CI 控制台默认编码可能是 cp1252，强制 UTF-8 避免打印中文时崩溃
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

SYSTEM = platform.system()
IS_WIN = SYSTEM == 'Windows'
IS_MAC = SYSTEM == 'Darwin'

# Windows 用 .ico；macOS 必须用 .icns；Linux 不设图标
if IS_WIN:
    icon_args = ['--icon', 'assets/app.ico']
elif IS_MAC:
    icon_args = ['--icon', 'assets/app.icns']
else:
    icon_args = []

# macOS 的 .app bundle 本身就是目录，不能用 onefile（会冲突）
mode_args = ['--onedir'] if IS_MAC else ['--onefile']

EXCLUDES = [
    'pygame', 'numpy', 'scipy', 'matplotlib', 'PIL', 'Pillow', 'pandas',
    'tkinter', 'unittest', 'IPython', 'jupyter',
    'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.QtWebChannel',
    'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtQuickWidgets', 'PySide6.QtQuickControls2',
    'PySide6.QtNetwork', 'PySide6.QtSql', 'PySide6.QtTest', 'PySide6.QtXml',
    'PySide6.QtOpenGL', 'PySide6.QtOpenGLWidgets', 'PySide6.QtPrintSupport',
    'PySide6.QtSvg', 'PySide6.QtSvgWidgets', 'PySide6.QtPdf', 'PySide6.QtPdfWidgets',
    'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets',
    'PySide6.Qt3DCore', 'PySide6.Qt3DRender', 'PySide6.QtCharts',
    'PySide6.QtDataVisualization', 'PySide6.QtDesigner', 'PySide6.QtHelp',
    'PySide6.QtBluetooth', 'PySide6.QtConcurrent', 'PySide6.QtNfc',
    'PySide6.QtPositioning', 'PySide6.QtSensors', 'PySide6.QtSerialPort',
    'PySide6.QtTextToSpeech', 'PySide6.QtWebSockets',
]

cmd = [
    sys.executable, '-m', 'PyInstaller',
    '--noconfirm', '--clean',
] + mode_args + [
    '--windowed',
    '--name', 'PomodoroTaskbar',
    '--add-data', 'sound' + os.pathsep + 'sound',
    '--add-data', 'assets' + os.pathsep + 'assets',
]
cmd += icon_args
for m in EXCLUDES:
    cmd.append('--exclude-module=' + m)
cmd.append('main.py')

print('系统:', SYSTEM)
print('打包命令:', ' '.join(cmd))
result = subprocess.run(cmd)
if result.returncode != 0:
    print('打包失败，退出码:', result.returncode)
    sys.exit(result.returncode)
print('打包成功，产物在 dist/')
