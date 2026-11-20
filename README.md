# 任务栏番茄钟

基于 **PySide6 + Win32 API** 的 Windows 任务栏番茄钟。窗口覆盖在任务栏上方，始终置顶，可拖动定位。

## 功能特性

- 任务栏高度自适应，半透明玻璃 UI + 进度圆环
- 开始 / 暂停 / 重置；窗口固定（禁止拖动）/ 解锁拖动
- 预设时长：`5/1`、`15/5`、`25/5`、`30/5`；设置中可自定义 1–180 / 1–90 分钟
- 连续专注模式（工作→休息→工作自动循环）
- 自定义 MP3 音效（`sound/1.mp3` 开始，`sound/2.mp3` 专注结束）
- 系统托盘、右键菜单、今日统计、历史记录
- 跨多显示器拖动；跨 DPI 屏幕自适应尺寸
- 开机自启（可选）
- 仅依赖系统 MCI 播放 MP3，无需 pygame

## 技术栈

- Python 3.10+
- PySide6
- Windows Win32 API（`ctypes` / `winmm` MCI）
- PyInstaller（打包）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 运行

```bash
python main.py
```

请确保 `sound/1.mp3`、`sound/2.mp3` 存在。

## 打包为 EXE

```bash
build.bat
```

或等价命令（Windows）：

```bash
pyinstaller --onefile --windowed --name PomodoroTaskbar --add-data "sound;sound" main.py
```

产物：`dist/PomodoroTaskbar.exe`（约 40–50MB，视 Python/Qt 环境而定）。

## 使用说明

1. 启动后窗口默认出现在任务栏区域（约屏幕右侧 1/4 处）
2. `▶` 开始，`⏸` 暂停，`↺` 重置；`📍`/`🔓` 锁定或解锁拖动
3. 下拉框切换预设时长；右键打开菜单（连续专注、今日统计、设置等）
4. 托盘图标：开始/暂停、设置、历史记录、显隐窗口、退出

### 音效规则

| 时机 | 音效 |
|------|------|
| 开始专注 | `1.mp3` |
| 专注结束 | `2.mp3` |
| 休息结束 + 连续专注 | `1.mp3`（并自动下一轮） |
| 休息结束 + 非连续 | 无 |

### 配置与数据位置

- 设置：`%APPDATA%\PomodoroTaskbar\settings.ini`
- 历史：`%APPDATA%\PomodoroTaskbar\history.json`

## 项目结构

```
├── main.py              # 入口与应用逻辑
├── appbar_window.py     # 任务栏窗口、进度环、拖动与置顶
├── timer_logic.py       # 计时状态机
├── settings.py          # 设置管理与设置对话框
├── tray_icon.py         # 系统托盘
├── history_manager.py   # 历史记录
├── history_dialog.py    # 历史对话框
├── sound/               # MP3 音效
├── requirements.txt
├── build.bat
└── README.md
```

## 注意事项

- 仅支持 **Windows 10 / 11**
- 置顶依赖 Win32 `SetWindowPos(HWND_TOPMOST)`；打开设置/统计/预设下拉时会短暂暂停高频刷新，避免遮挡弹出层
- 音效通过 `winmm.mciSendStringW` 播放本地 MP3

## License

MIT License
