"""
Fuck ETS100 - Windows 版本
主程序入口
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 添加 src 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from ui import MainWindow
from ui.theme_manager import ThemeManager


def main():
    app = QApplication(sys.argv)
    
    # 设置应用程序信息
    app.setApplicationName("Fuck ETS100")
    app.setOrganizationName("FuckETS100")
    app.setApplicationVersion("1.0.0")
    
    # 设置默认字体
    font = QFont("Microsoft YaHei", 10)
    app.setFont(font)
    
    # 初始化主题管理器（默认跟随系统）
    theme_mgr = ThemeManager()
    theme_mgr.apply_to_app()
    
    # 创建并显示主窗口
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
