# -*- coding: utf-8 -*-
"""本地诊断：把未捕获异常写到用户目录，避免窗口程序闪退后无任何线索。

日志只写在本机，不联网、不上传。
"""

import functools
import os
import sys
import traceback
from datetime import datetime

_MAX_BYTES = 512 * 1024


def _log_path():
    base = os.environ.get('APPDATA')
    if not base:
        base = os.path.join(os.path.expanduser('~'), '.config')
    return os.path.join(base, 'PomodoroTaskbar', 'crash.log')


def log_exception(context, exc=None, tb=None):
    try:
        if tb is not None:
            text = ''.join(traceback.format_exception(type(exc), exc, tb))
        elif exc is not None:
            text = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__))
        else:
            text = traceback.format_exc()
        path = _log_path()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if os.path.exists(path) and os.path.getsize(path) > _MAX_BYTES:
            os.replace(path, path + '.old')
        with open(path, 'a', encoding='utf-8') as f:
            f.write(f"\n===== {datetime.now().isoformat(timespec='seconds')} [{context}] =====\n")
            f.write(text)
            if not text.endswith('\n'):
                f.write('\n')
    except Exception:
        pass


def safe_slot(func):
    """装饰槽函数：单个回调出错只记日志，不让整个进程退出。"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            log_exception(func.__qualname__, exc)
            return None
    return wrapper


def install_exception_hook():
    """捕获主线程未处理异常，写日志后仍交给默认钩子打印。"""
    def hook(exc_type, exc, tb):
        log_exception('unhandled', exc, tb)
        try:
            sys.__excepthook__(exc_type, exc, tb)
        except Exception:
            pass
    sys.excepthook = hook
