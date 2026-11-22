# -*- coding: utf-8 -*-
"""平台差异统一层。

把 Windows 专属的 Win32 调用（置顶 / MCI 音效 / 注册表自启）与
Linux 的对应实现收口到这里，业务代码只调用本模块的通用接口。

- Windows: 保持原有 Win32 行为（user32 / winmm / winreg）
- Linux:   Qt 原生置顶 + paplay/aplay + XDG autostart
"""
import os
import sys
import platform
import subprocess

from i18n import tr

IS_WIN = platform.system() == 'Windows'
IS_LINUX = platform.system() == 'Linux'

APP_NAME = 'PomodoroTaskbar'


# ── 音效播放 ────────────────────────────────────────────────────────
# MCI 延迟加载：即使系统策略拦截 winmm，也不影响软件启动与主流程。
_mci = None
_mci_failed = False


def _get_mci():
    global _mci, _mci_failed
    if _mci is not None or _mci_failed or not IS_WIN:
        return _mci
    try:
        import ctypes
        _mci = ctypes.windll.winmm
        _mci.mciSendStringW.argtypes = [ctypes.c_wchar_p, ctypes.c_wchar_p,
                                        ctypes.c_uint, ctypes.c_void_p]
        _mci.mciSendStringW.restype = ctypes.c_long
    except Exception:
        from diagnostics import log_exception
        log_exception('mci.init')
        _mci_failed = True
        _mci = None
    return _mci


def play_sound_file(path, mci_type='waveaudio'):
    """双平台播放提示音。path 为本地音频文件（wav/mp3）。"""
    try:
        if IS_WIN:
            mci = _get_mci()
            if mci is None:
                return False
            mci.mciSendStringW('close bgm', None, 0, None)
            mci.mciSendStringW(f'open "{path}" type {mci_type} alias bgm', None, 0, None)
            mci.mciSendStringW('play bgm', None, 0, None)
        else:
            # Linux：优先 PulseAudio 的 paplay，回退 ALSA 的 aplay
            player = None
            for candidate in ('paplay', 'aplay'):
                if _which(candidate):
                    player = candidate
                    break
            if player:
                subprocess.Popen([player, path],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                # 兜底：让系统默认程序打开
                subprocess.Popen(['xdg-open', path],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception:
        return False


def _which(name):
    for p in os.environ.get('PATH', '').split(os.pathsep):
        candidate = os.path.join(p, name)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return candidate
    return None


# ── 开机自启 ────────────────────────────────────────────────────────
def set_auto_start(enable):
    """双平台设置开机自启。失败静默忽略。"""
    try:
        if IS_WIN:
            _set_auto_start_windows(enable)
        elif IS_LINUX:
            _set_auto_start_linux(enable)
    except Exception:
        pass


def is_auto_start_enabled():
    try:
        if IS_WIN:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r'Software\Microsoft\Windows\CurrentVersion\Run')
            try:
                winreg.QueryValueEx(key, APP_NAME)
                return True
            finally:
                winreg.CloseKey(key)
        elif IS_LINUX:
            return os.path.exists(_linux_desktop_path())
    except Exception:
        pass
    return False


def _exe_path():
    return sys.executable if getattr(sys, 'frozen', False) else sys.argv[0]


def _set_auto_start_windows(enable):
    import winreg
    key_path = r'Software\Microsoft\Windows\CurrentVersion\Run'
    if enable:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, _exe_path())
    else:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, APP_NAME)
        except FileNotFoundError:
            pass


def _linux_desktop_path():
    return os.path.expanduser(f'~/.config/autostart/{APP_NAME}.desktop')


def _set_auto_start_linux(enable):
    desktop = _linux_desktop_path()
    if enable:
        exe = os.path.abspath(_exe_path())
        content = f'''[Desktop Entry]
Type=Application
Name={tr("Taskbar Pomodoro")}
Exec={exe}
Hidden=false
NoDisplay=false
X-GNOME-Autostart-enabled=true
'''
        os.makedirs(os.path.dirname(desktop), exist_ok=True)
        with open(desktop, 'w', encoding='utf-8') as f:
            f.write(content)
    else:
        if os.path.exists(desktop):
            os.remove(desktop)
