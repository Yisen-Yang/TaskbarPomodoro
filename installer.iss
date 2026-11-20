; 番茄钟安装脚本 —— 安装到当前用户目录，无需管理员权限
; 用 Inno Setup 6 编译

#define AppName "任务栏番茄钟"
#define AppVersion "1.1.0"
#define AppPublisher "Yisen-Yang"
#define AppExeName "PomodoroTaskbar.exe"

[Setup]
AppId={{8F3C2D1A-6E94-4B7A-9C21-123456789ABC}
AppName={#AppName}
AppVersion={#AppVersion}
AppVerName={#AppName} {#AppVersion}
AppPublisher={#AppPublisher}
DefaultDirName={userappdata}\PomodoroTaskbar
DefaultGroupName={#AppName}
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma2/max
SolidCompression=yes
OutputDir=..\Release交付
OutputBaseFilename=PomodoroTaskbar_安装版_v1.1.0
SetupIconFile=assets\app.ico
Uninstallable=yes
; 关键：不请求管理员权限
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
; 64 位
ArchitecturesInstallIn64BitMode=x64
; 不显示"选择组件"页
DisableProgramGroupPage=yes
WizardStyle=modern

[Languages]
Name: "chinese"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Tasks]
Name: "desktopicon"; Description: "创建桌面快捷方式"; GroupDescription: "快捷方式:"
Name: "startup"; Description: "开机自动启动"; GroupDescription: "快捷方式:"

[Files]
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"
Name: "{group}\卸载 {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Registry]
; 开机自启（HKCU，无需管理员）
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "PomodoroTaskbar"; ValueData: "{app}\{#AppExeName}"; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{app}\{#AppExeName}"; Description: "立即运行番茄钟"; Flags: postinstall nowait skipifsilent
