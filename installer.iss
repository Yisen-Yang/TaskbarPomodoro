; 番茄钟安装脚本 —— 安装到当前用户目录，无需管理员权限
; 用 Inno Setup 6（Unicode 版）编译
;
; 特性：
;   1. 安装向导支持中文 / English 两种语言
;   2. 自定义页选择「软件界面语言」（跟随系统/简中/English/日本語），写入 settings.ini
;   3. 相同 AppId + 递增版本号 => 自动识别为覆盖升级，保留用户设置与历史记录

#define AppName "任务栏番茄钟"
#define AppVersion "1.3.0"
#define AppPublisher "Yisen-Yang"
#define AppExeName "PomodoroTaskbar.exe"
#define AppIdValue "{{8F3C2D1A-6E94-4B7A-9C21-123456789ABC}"

[Setup]
AppId={#AppIdValue}
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
OutputBaseFilename=PomodoroTaskbar_安装版_v1.3.0
SetupIconFile=assets\app.ico
; 安装向导配图（深色番茄 · 发光进度环酷炫风格；由 tools/generate_installer_art.py 生成）
WizardImageFile=docs\images\wizard.png
WizardSmallImageFile=docs\images\wizard_small.png
; 左侧大图背景色与配图深色底一致，避免出现白边
WizardImageBackColor=$171426
Uninstallable=yes
; 关键：不请求管理员权限
PrivilegesRequired=lowest
PrivilegesRequiredOverridesAllowed=commandline
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
WizardStyle=modern
; 升级时若文件被占用，安排重启后替换，避免覆盖失败
CloseApplications=yes
RestartApplications=no

[Languages]
Name: "chinese"; MessagesFile: "tools\inno-languages\ChineseSimplified.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[CustomMessages]
DesktopShortcut=创建桌面快捷方式
AutoStartDesc=开机自动启动
AdditionalIcons=快捷方式:
RunApp=立即运行番茄钟
LangTitle=界面语言
LangSubTitle=选择番茄钟启动后使用的语言
LangDescNew=请选择界面语言，之后也可随时在「设置」中更改：
LangDescUpgrade=检测到已安装旧版本，本次将直接覆盖升级；您的设置与专注记录会完整保留。请选择界面语言：
Lang0=跟随系统（推荐）
Lang1=简体中文
Lang2=English
Lang3=日本語
english.DesktopShortcut=Create desktop shortcut
english.AutoStartDesc=Start with Windows
english.AdditionalIcons=Shortcuts:
english.RunApp=Run Taskbar Pomodoro now
english.LangTitle=Interface Language
english.LangSubTitle=Choose the language used by Taskbar Pomodoro
english.LangDescNew=Choose the interface language. You can change it later in Settings:
english.LangDescUpgrade=An older version was detected. It will be upgraded in place; your settings and focus history will be preserved. Choose the interface language:
english.Lang0=Follow system (recommended)
english.Lang1=简体中文 (Simplified Chinese)
english.Lang2=English
english.Lang3=日本語 (Japanese)

[Messages]
WelcomeLabel2=将在本机安装 [name/ver]。%n%n无需管理员权限；安装不会覆盖您的设置与专注记录。
FinishedHeadingLabel=[name] 安装完成
FinishedLabel=番茄钟已准备就绪，祝您专注愉快！
english.WelcomeLabel2=This will install [name/ver] on your computer.%n%nNo administrator rights are required; your settings and focus history will be preserved.
english.FinishedHeadingLabel=[name] Installation Complete
english.FinishedLabel=Taskbar Pomodoro is ready. Happy focusing!

[Tasks]
Name: "desktopicon"; Description: "{cm:DesktopShortcut}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "startup"; Description: "{cm:AutoStartDesc}"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; restartreplace：升级时若旧 EXE 正在运行，安排重启后替换，不会中断安装
Source: "dist\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion restartreplace
Source: "README.md"; DestDir: "{app}"; Flags: ignoreversion
Source: "README_EN.md"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"
Name: "{group}\卸载 {#AppName}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; IconFilename: "{app}\{#AppExeName}"; Tasks: desktopicon

[Registry]
; 开机自启（HKCU，无需管理员）
Root: HKCU; Subkey: "Software\Microsoft\Windows\CurrentVersion\Run"; ValueType: string; ValueName: "PomodoroTaskbar"; ValueData: "{app}\{#AppExeName}"; Flags: uninsdeletevalue; Tasks: startup

[Run]
Filename: "{app}\{#AppExeName}"; Description: "{cm:RunApp}"; Flags: postinstall nowait skipifsilent

[Code]
var
  LangPage: TInputOptionWizardPage;
  OldVersionFound: Boolean;

{ 软件配置固定写在 %APPDATA%\PomodoroTaskbar\settings.ini，与安装目录解耦 }
function ConfigPath: string;
begin
  Result := ExpandConstant('{userappdata}\PomodoroTaskbar\settings.ini');
end;

function DefaultExePath: string;
begin
  Result := ExpandConstant('{userappdata}\PomodoroTaskbar\{#AppExeName}');
end;

{ 检测是否已有旧版本（用于提示覆盖升级）
  注意：InitializeWizard 阶段 app 常量尚未初始化，绝不能在此展开 app 路径，
  否则会报 "expand the app constant before it was initialized"。
  安装目录固定为 %APPDATA%\PomodoroTaskbar，与 DefaultExePath 一致，直接检查它即可。 }
function HasOldVersion: Boolean;
begin
  Result := FileExists(DefaultExePath);
end;

{ 读取当前配置里的语言，升级时保持用户原有选择 }
function CurrentLangIndex: Integer;
var
  sl: TStringList;
  i: Integer;
  v: string;
  p: string;
begin
  Result := 0;
  p := ConfigPath;
  if not FileExists(p) then
    Exit;
  sl := TStringList.Create;
  try
    sl.LoadFromFile(p);
    for i := 0 to sl.Count - 1 do
    begin
      if Pos('language=', sl[i]) = 1 then
      begin
        v := Trim(Copy(sl[i], 10, MaxInt));
        if v = 'zh_CN' then Result := 1
        else if v = 'en_US' then Result := 2
        else if v = 'ja_JP' then Result := 3
        else Result := 0;
        Break;
      end;
    end;
  finally
    sl.Free;
  end;
end;

procedure InitializeWizard;
begin
  OldVersionFound := HasOldVersion;
  LangPage := CreateInputOptionPage(wpWelcome,
    CustomMessage('LangTitle'), CustomMessage('LangSubTitle'),
    '', True, False);
  LangPage.Add(CustomMessage('Lang0'));
  LangPage.Add(CustomMessage('Lang1'));
  LangPage.Add(CustomMessage('Lang2'));
  LangPage.Add(CustomMessage('Lang3'));
  if OldVersionFound then
    LangPage.Description := CustomMessage('LangDescUpgrade')
  else
    LangPage.Description := CustomMessage('LangDescNew');
  LangPage.SelectedValueIndex := CurrentLangIndex;
end;

{ 把选择写入 settings.ini 的 language 键（保留其他所有配置） }
procedure WriteLanguageSetting;
var
  code: string;
  sl: TStringList;
  i: Integer;
  p: string;
  found: Boolean;
begin
  case LangPage.SelectedValueIndex of
    0: code := 'system';
    1: code := 'zh_CN';
    2: code := 'en_US';
    3: code := 'ja_JP';
  else
    code := 'system';
  end;

  p := ConfigPath;
  sl := TStringList.Create;
  try
    if FileExists(p) then
      sl.LoadFromFile(p);
    found := False;
    for i := 0 to sl.Count - 1 do
    begin
      if Pos('language=', sl[i]) = 1 then
      begin
        sl[i] := 'language=' + code;
        found := True;
        Break;
      end;
    end;
    if not found then
      sl.Add('language=' + code);
    sl.SaveToFile(p);
  finally
    sl.Free;
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
    WriteLanguageSetting;
end;
