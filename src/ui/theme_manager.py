"""
主题管理器 - 支持亮色/暗色/跟随系统
"""
import json
import os
from enum import Enum
from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QStyleHints

from .styles import DARK_STYLE, LIGHT_STYLE


class Theme(Enum):
    SYSTEM = "system"
    LIGHT = "light"
    DARK = "dark"


class ThemeManager(QObject):
    """主题管理器，单例模式"""
    
    theme_changed = pyqtSignal(str)  # 'light' or 'dark'
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        super().__init__()
        self._initialized = True
        self._config_dir = self._get_config_dir()
        self._config_file = os.path.join(self._config_dir, "theme.json")
        self._preference = Theme.SYSTEM
        self._current_effective = "dark"  # actual applied theme
        self._load_preference()
    
    def _get_config_dir(self):
        """获取配置目录"""
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        config_dir = os.path.join(appdata, "FuckETS100")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    
    def _load_preference(self):
        """加载主题偏好"""
        try:
            if os.path.exists(self._config_file):
                with open(self._config_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    pref = data.get("theme", "system")
                    self._preference = Theme(pref) if pref in [t.value for t in Theme] else Theme.SYSTEM
        except Exception:
            self._preference = Theme.SYSTEM
    
    def _save_preference(self):
        """保存主题偏好"""
        try:
            with open(self._config_file, "w", encoding="utf-8") as f:
                json.dump({"theme": self._preference.value}, f)
        except Exception:
            pass
    
    def _detect_system_theme(self) -> str:
        """检测系统主题"""
        app = QApplication.instance()
        if app:
            hint = app.styleHints()
            if hasattr(hint, 'colorScheme'):
                scheme = hint.colorScheme()
                if scheme == Qt.ColorScheme.Dark:
                    return "dark"
                elif scheme == Qt.ColorScheme.Light:
                    return "light"
        # 默认暗色
        return "dark"
    
    def get_effective_theme(self) -> str:
        """获取当前生效的主题 ('light' or 'dark')"""
        if self._preference == Theme.SYSTEM:
            return self._detect_system_theme()
        return self._preference.value
    
    def get_preference(self) -> Theme:
        """获取用户偏好设置"""
        return self._preference
    
    def set_theme(self, theme: Theme):
        """设置主题偏好"""
        if self._preference != theme:
            self._preference = theme
            self._save_preference()
            new_effective = self.get_effective_theme()
            if new_effective != self._current_effective:
                self._current_effective = new_effective
                self._apply_theme()
                self.theme_changed.emit(new_effective)
    
    def toggle(self):
        """切换亮色/暗色"""
        current = self.get_effective_theme()
        new = Theme.LIGHT if current == "dark" else Theme.DARK
        self.set_theme(new)
    
    def get_stylesheet(self) -> str:
        """获取当前主题的样式表"""
        theme = self.get_effective_theme()
        self._current_effective = theme
        return DARK_STYLE if theme == "dark" else LIGHT_STYLE
    
    def apply_to_app(self):
        """应用主题到应用程序"""
        self._current_effective = self.get_effective_theme()
        self._apply_theme()
    
    def _apply_theme(self):
        """应用主题样式"""
        app = QApplication.instance()
        if app:
            theme = self._current_effective
            app.setStyleSheet(DARK_STYLE if theme == "dark" else LIGHT_STYLE)
    
    def on_system_theme_changed(self):
        """系统主题变化时调用（仅当设置为跟随系统时）"""
        if self._preference == Theme.SYSTEM:
            new_theme = self._detect_system_theme()
            if new_theme != self._current_effective:
                self._current_effective = new_theme
                self._apply_theme()
                self.theme_changed.emit(new_theme)
    
    @property
    def is_dark(self) -> bool:
        return self.get_effective_theme() == "dark"