# Fuck ETS100 - Windows 版本

![logo](https://github.com/banglee13/Fuck_ets100_win/blob/main/logo.png?raw=true)

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

## 使用说明

1. **启动程序**：启动应用
2. **登录账号**：输入 ETS100 手机号和密码进行登录
3. **获取作业**：点击"刷新作业"按钮获取作业列表
4. **查看答案**：点击作业名称自动下载并解析答案
5. **导出答案**：点击"导出答案"将答案保存为文本文件

## 项目结构

```
Fuck_ets_win/
├── src/
│   ├── core/              # 核心模块
│   │   ├── api_client.py  # API 客户端
│   │   ├── zip_utils.py   # ZIP 工具
│   │   ├── answer_parser.py # 答案解析
│   │   ├── auth_manager.py # 认证管理
│   │   └── __init__.py
│   ├── ui/                # UI 模块
│   │   ├── login_dialog.py # 登录对话框
│   │   ├── main_window.py  # 主窗口
│   │   └── __init__.py
│   └── __init__.py
├── cache/                 # 缓存目录
├── docs/                  # 文档
├── assets/                # 资源文件
├── run.py                 # 推荐启动器（自动安装依赖）
├── main.py                # 主程序入口
├── 启动.bat              # Windows 批处理启动
├── 启动.ps1              # PowerShell 启动脚本
├── requirements.txt       # 依赖列表
└── README.md
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
