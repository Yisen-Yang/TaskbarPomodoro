<div align="center">

# 🍅 任务栏番茄钟

**常驻任务栏的极简番茄工作法工具 —— 专注与休息，抬眼即见。**

基于 PySide6 + Win32 API，仅 Windows 可用。窗口覆盖在任务栏上方、始终置顶、可自由拖动定位。

[![Windows](https://img.shields.io/badge/Platform-Windows%2010%2F11-0078D4?logo=windows&logoColor=white)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

</div>

![任务栏番茄钟界面展示](docs/images/hero.png)

## 为什么用它？

大多数番茄钟是一个独立窗口——你需要把它切到前台，然后它会盖住正在做的工作。
**任务栏番茄钟** 换了一种思路：把自己嵌进任务栏，成为桌面的一部分。

| 痛点 | 本项目的做法 |
|------|------------|
| 番茄钟窗口挡住工作区 | 常驻任务栏，与系统任务栏**同高**，不占用桌面空间 |
| 一开全屏/其他窗口就看不见 | Win32 `HWND_TOPMOST` **始终置顶**，任何窗口都无法遮挡 |
| 多显示器拖动后界面变形 | 基于 Qt6 原生逻辑像素 + `screenChanged` 监听，**跨屏/跨 DPI 自动重排** |
| 计时器切走后走时不准 | 采用**单调时钟绝对时间戳**，系统卡顿或休眠唤醒后自动追平，不漂移 |
| 打包工具动辄上百 MB | 仅依赖 PySide6，**EXE 约 44MB**；提供安装版 + 绿色版 |
| 需要安装一堆音频库 | 直接调用 Windows MCI（`winmm`），**零第三方音频依赖** |
| 界面千篇一律 | **5 种主题**一键切换（深空/浅色/番茄红/森林绿/iOS） |
| 提示音不能换 | **14 种音效**自选，开始/结束分别设置 |

## 功能特性

![专注状态一览](docs/images/states.png)

- **任务栏融合**：半透明玻璃质感 UI + 实时进度圆环，窗口高度自适应任务栏
- **始终置顶**：主窗口常驻顶层；打开设置/统计/下拉菜单时智能暂停刷新，避免遮挡弹出层
- **拖拽与锁定**：可拖动到任意位置；`📍` 一键锁定，防止误触移动
- **完整番茄工作法**：专注 → 短休息 → …… → **每 4 个番茄自动进入长休息**（时长与轮数均可配置）
- **精准计时**：单调时钟驱动，杜绝累计误差；暂停后续接无偏差
- **连续专注模式**：工作与休息自动循环，直到手动暂停
- **5 种主题**：经典深空 / 清爽浅色 / 番茄红 / 森林绿 / iOS 现代风，设置里一键切换、即时生效
- **🍅 番茄图标**：窗口、托盘、安装包统一使用自绘番茄图标
- **14 种可选音效**：8 种代码合成（零版权）+ 6 种 mixkit 免费音效，**开始/结束音效分别可选**
- **系统托盘**：托盘菜单可开始/暂停、查看历史、今日统计、显隐窗口、开机自启
- **数据本地化**：设置与历史全部保存在本机 `%APPDATA%`，不联网、不上传

## 快速开始

### 方式一：直接运行（推荐开发者）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 运行
python main.py
```

### 方式二：下载现成版本（推荐）

从 [Releases](../../releases) 下载，有两个版本：

- **安装版** `PomodoroTaskbar_安装版_vX.X.X.exe`：双击安装到用户目录，自动建快捷方式，**无需管理员权限**，可卸载
- **绿色版** `PomodoroTaskbar_绿色版_vX.X.X.zip`：解压即用，删除文件夹即卸载

均无需 Python 环境。仅支持 Windows 10 / 11。

### 打包为 EXE

```bat
build.bat
```

产物位于 `dist/PomodoroTaskbar.exe`（约 44MB）。`build.bat` 内含精简参数，剔除 PySide6 中未使用的 WebEngine、QML、3D、Charts 等模块以控制体积。

## 使用说明

1. 启动后窗口出现在任务栏区域（默认屏幕右侧）
2. `▶` 开始 / `⏸` 暂停，`↺` 重置；`📍` 锁定窗口（禁止拖动）/ `🔓` 解锁
3. 下拉框切换预设时长；**右键窗口**打开菜单（连续专注、今日统计、设置、历史等）
4. 双击托盘图标可快速开始 / 暂停

### 预设与自定义

- 内置预设：`5/1`、`15/5`、`25/5`、`30/5`（专注/短休息，分钟）
- 设置中可自定义：专注时长、短休息、长休息时长、每几轮进入长休息、开机自启、提示音开关

### 音效规则

在 设置 → 声音设置 中，可分别为"开始 / 下一轮"和"专注结束"挑选音效，共 14 种：

- **8 种代码合成**（经典三音、清脆铃音、柔和双音、木鱼、电子音、晨光、完成和弦、禅意低音）——零版权
- **6 种 mixkit 免费音效**（界面启动、积极提示、马林巴琴、清亮铃声、欢快铃音、魔法铃环）

| 时机 | 使用设置项 |
|------|------|
| 开始专注 / 休息结束后进入下一轮 | 开始音效 |
| 专注结束 | 结束音效 |
| 休息结束且未开启连续专注 | 无 |

### 配置与数据位置

- 设置：`%APPDATA%\PomodoroTaskbar\settings.ini`
- 历史：`%APPDATA%\PomodoroTaskbar\history.json`

所有数据仅存于本机，不会上传到任何服务器。

## 技术栈

- **PySide6**：GUI 框架（仅用 QtWidgets / QtCore / QtGui）
- **Win32 API**（`ctypes`）：`SetWindowPos` 置顶、扩展窗口样式、任务栏高度计算
- **Windows MCI**（`winmm.mciSendStringW`）：零依赖播放 WAV / MP3
- **PyInstaller**：单文件 EXE 打包

## 项目结构

```
.
├── main.py              # 入口、应用逻辑、音效与通知
├── appbar_window.py     # 任务栏窗口、进度环、拖动/置顶/跨屏自适应
├── timer_logic.py       # 计时状态机（单调时钟 + 长休息）
├── settings.py          # 设置管理与设置对话框
├── tray_icon.py         # 系统托盘与右键菜单
├── history_manager.py   # 历史记录读写与统计
├── history_dialog.py    # 历史记录对话框
├── theme.py             # 5 套主题配色定义
├── sounds.py            # 14 种音效注册表
├── sound/               # 提示音文件（合成 WAV + mixkit MP3）
├── assets/              # 番茄图标（app.ico / tomato.png）
├── installer.iss        # Inno Setup 安装版脚本（免管理员）
├── docs/images/         # README 配图及其生成脚本
├── tests/               # 计时状态机单元测试
├── requirements.txt
├── build.bat
└── README.md
```

### 运行测试

```bash
python -m unittest tests.test_timer_logic
```

测试覆盖初始状态、时长切换、长休息间隔、计时防漂移、暂停续接等核心逻辑。

## 注意事项

- 仅支持 **Windows 10 / 11**
- 置顶依赖 Win32 `SetWindowPos(HWND_TOPMOST)`，因此任务栏窗口会浮于其他窗口之上（这是设计目的）
- 音效通过 Windows 系统 MCI 播放，无需安装 pygame 或其他音频库
- 6 种 mixkit 音效可用于个人/商业项目，但**不可将音频文件单独再分发/转售**
- 设置与历史存于 `%APPDATA%`，换电脑不会带走；绿色版卸载时可一并删除

## License

[MIT](LICENSE) © Yisen-Yang
