# Fuck ETS100 - Windows 版本

<img src="https://github.com/banglee13/Fuck_ets100_win/blob/main/logo.png?raw=true" width="300">

感谢 https://github.com/laststudio/Fuck_ets100 提供的原始代码，AI 根据原始代码改的。

专门为 ETS100 (e听说) 用户打造的答案提取工具 - Windows 桌面版本

![License: GPL-3.0](https://img.shields.io/badge/License-GPL%203.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.5+-green.svg)

## 功能特性

- ✅ **云端模式**：直接从 ETS100 云端获取作业列表和答案
- ✅ **自动解压**：自动生成 ZIP 解压密码并解密
- ✅ **多种题型**：支持选择题、问答题、信息转述、填空题等所有题型
- ✅ **答案导出**：支持将答案导出为文本文件
- ✅ **跨平台**：基于 Python + PyQt6 开发，理论支持 Windows / macOS / Linux
- ✅ **美观界面**：现代化的桌面应用界面

## 快速开始

### 环境要求

- Python 3.8 或更高版本
- Windows 7 或更高版本

### 多种启动方式（任选一种）

#### 方式 1：最简单，推荐（使用 run.py）
```bash
python run.py
```

#### 方式 2：使用批处理脚本
双击 `run.bat`

## 开发与构建

### 开发环境搭建

```bash
# 克隆项目
git clone https://github.com/banglee13/Fuck_ets100_win.git
cd Fuck_ets100_win

# 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 开发模式运行

```bash
# 方式 1：使用 main.py
python main.py

# 方式 2：使用 run.py（自动检查依赖）
python run.py
```

### 打包构建

```bash
# 安装打包工具
pip install pyinstaller pillow

# 方式 1：运行打包脚本（推荐）
build.bat

# 方式 2：手动打包
pyinstaller --onefile --windowed --name "FuckETS100" --icon="logo.ico" --add-data "src;src" --hidden-import=requests --hidden-import=pyzipper --hidden-import=dotenv.main --hidden-import=PyQt6.QtWebEngineWidgets --hidden-import=PyQt6.QtWebEngineCore main.py
```

打包完成后，exe 文件位于 `dist/FuckETS100.exe`

## 使用说明

1. **启动程序**：启动应用
2. **登录账号**：输入 ETS100 手机号和密码进行登录
3. **获取作业**：点击"刷新作业"按钮获取作业列表
4. **查看答案**：点击作业名称自动下载并解析答案
5. **导出答案**：点击"导出答案"将答案保存为文本文件

## 项目结构

```
Fuck_ets100_win/
├── src/
│   ├── core/              # 核心模块
│   │   ├── __init__.py
│   │   ├── api_client.py  # API 客户端
│   │   ├── auth_manager.py # 认证管理
│   │   ├── answer_parser.py # 答案解析
│   │   └── zip_utils.py   # ZIP 工具
│   ├── ui/                # UI 模块
│   │   ├── __init__.py
│   │   ├── login_dialog.py # 登录对话框
│   │   ├── main_window.py  # 主窗口
│   │   ├── styles.py       # 样式定义
│   │   ├── theme_manager.py # 主题管理
│   │   ├── verification_dialog.py # 验证码对话框
│   │   └── verification_dialog_v2.py # 验证码对话框 v2
│   └── __init__.py
├── docs/                  # 文档
│   └── 使用说明.md
├── main.py                # 主程序入口
├── run.py                 # 推荐启动器（自动安装依赖）
├── run.bat                # Windows 批处理启动
├── build.bat              # 打包脚本
├── requirements.txt       # 依赖列表
├── logo.png               # 应用图标（PNG）
├── logo.ico               # 应用图标（ICO）
├── README.md              # 项目说明
├── 快速入门.md            # 快速入门指南
├── FuckETS100.spec        # PyInstaller 打包配置
└── LICENSE                # 许可证
```

## 注意事项

⚠️ **重要提示**：

1. 本工具仅供学习交流使用，请勿用于考试作弊等违规行为
2. 使用前请确保您已购买了 e听说 的正版服务
3. 云端模式可能会导致官方客户端被顶号，建议先使用本工具查看答案后再去官方客户端做题
4. 请妥善保管您的账号密码

## 技术栈

- **GUI 框架**：PyQt6
- **HTTP 请求**：requests
- **ZIP 处理**：pyzipper
- **JSON 解析**：Python 标准库 json

## 免责声明

本项目仅供学习和技术研究使用。使用本项目产生的一切后果由使用者自行承担。作者不对使用本项目造成的任何问题负责。

## 许可证

本项目采用 GPL-3.0 许可证 - 详见 [LICENSE](LICENSE) 文件

## 致谢

- 原 Android 版本开发者
- PyQt6 社区
- 所有贡献者
