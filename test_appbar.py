import sys
import ctypes
from ctypes import wintypes

user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32

ABM_NEW = 0x00000000
ABM_REMOVE = 0x00000001
ABM_QUERYPOS = 0x00000002
ABM_SETPOS = 0x00000003
ABM_GETSTATE = 0x00000004
ABM_GETTASKBARPOS = 0x00000005
ABM_ACTIVATE = 0x00000006
ABM_GETAUTOHIDEBAR = 0x00000007
ABM_SETAUTOHIDEBAR = 0x00000008
ABM_WINDOWPOSCHANGED = 0x00000009
ABM_SETSTATE = 0x0000000A

ABN_STATECHANGE = 0x00000000
ABN_POSCHANGED = 0x00000002
ABN_FULLSCREENAPP = 0x00000003
ABN_WINDOWARRANGE = 0x00000004

AB_LEFT = 0x00000000
AB_TOP = 0x00000001
AB_RIGHT = 0x00000002
AB_BOTTOM = 0x00000003

SM_CYSCREEN = 1
SM_CXSCREEN = 0
SM_CYSMICON = 49

class RECT(ctypes.Structure):
    _fields_ = [
        ("left", wintypes.LONG),
        ("top", wintypes.LONG),
        ("right", wintypes.LONG),
        ("bottom", wintypes.LONG),
    ]

class APPBARDATA(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("hWnd", wintypes.HWND),
        ("uCallbackMessage", wintypes.UINT),
        ("uEdge", wintypes.UINT),
        ("rc", RECT),
        ("lParam", wintypes.LPARAM),
    ]

def get_taskbar_rect():
    hwnd_tray = user32.FindWindowW("Shell_TrayWnd", None)
    if not hwnd_tray:
        print("ERROR: 无法找到任务栏窗口")
        return None
    
    rect = RECT()
    result = user32.GetWindowRect(hwnd_tray, ctypes.byref(rect))
    if not result:
        print("ERROR: 无法获取任务栏矩形")
        return None
    
    print(f"任务栏句柄: {hwnd_tray}")
    print(f"任务栏位置: left={rect.left}, top={rect.top}, right={rect.right}, bottom={rect.bottom}")
    print(f"任务栏尺寸: 宽度={rect.right - rect.left}, 高度={rect.bottom - rect.top}")
    return rect

def test_appbar_registration():
    hwnd = user32.CreateWindowExW(
        0,
        "STATIC",
        "Test AppBar",
        0,
        0, 0, 100, 48,
        None,
        None,
        None,
        None
    )
    
    if not hwnd:
        print(f"ERROR: 创建窗口失败, 错误码: {ctypes.get_last_error()}")
        return False
    
    print(f"测试窗口句柄: {hwnd}")
    
    abd = APPBARDATA()
    abd.cbSize = ctypes.sizeof(APPBARDATA)
    abd.hWnd = hwnd
    abd.uCallbackMessage = 0x0312
    abd.uEdge = AB_RIGHT
    
    result = shell32.SHAppBarMessage(ABM_NEW, ctypes.byref(abd))
    print(f"ABM_NEW 结果: {result}")
    
    if result:
        screen_width = user32.GetSystemMetrics(SM_CXSCREEN)
        screen_height = user32.GetSystemMetrics(SM_CYSCREEN)
        taskbar_height = user32.GetSystemMetrics(SM_CYSMICON) + 8
        
        abd.rc.left = screen_width - 100
        abd.rc.top = screen_height - taskbar_height
        abd.rc.right = screen_width
        abd.rc.bottom = screen_height
        
        result = shell32.SHAppBarMessage(ABM_QUERYPOS, ctypes.byref(abd))
        print(f"ABM_QUERYPOS 结果: {result}")
        print(f"查询后矩形: left={abd.rc.left}, top={abd.rc.top}, right={abd.rc.right}, bottom={abd.rc.bottom}")
        
        result = shell32.SHAppBarMessage(ABM_SETPOS, ctypes.byref(abd))
        print(f"ABM_SETPOS 结果: {result}")
        
        user32.ShowWindow(hwnd, 1)
        print("AppBar 注册成功! 窗口已显示")
        
        import time
        time.sleep(5)
        
        abd = APPBARDATA()
        abd.cbSize = ctypes.sizeof(APPBARDATA)
        abd.hWnd = hwnd
        shell32.SHAppBarMessage(ABM_REMOVE, ctypes.byref(abd))
        user32.DestroyWindow(hwnd)
        return True
    else:
        print("AppBar 注册失败!")
        user32.DestroyWindow(hwnd)
        return False

if __name__ == "__main__":
    print("=== Windows 任务栏信息 ===")
    get_taskbar_rect()
    
    print("\n=== 测试 AppBar 注册 ===")
    success = test_appbar_registration()
    
    if not success:
        print("\n=== AppBar 注册失败，将尝试覆盖窗口方案 ===")
        print("覆盖窗口方案将使用 SetParent + SetWindowPos 在任务栏上方显示窗口")
