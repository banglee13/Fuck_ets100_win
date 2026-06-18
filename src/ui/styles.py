"""
UI 样式表 (Material Design 3 亮色/暗色主题)
主色: #0B65D8 (天空蓝)
"""

DARK_STYLE = """
/* ===== 全局基础 ===== */
QWidget {
    background-color: #1E1E1E;
    color: #E5E1E7;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 14px;
}

/* ===== 主窗口 ===== */
QMainWindow {
    background-color: #1E1E1E;
}

/* ===== 顶部工具栏 ===== */
QToolBar {
    background-color: #1E2530;
    border-bottom: 1px solid #494551;
    padding: 8px 12px;
    spacing: 10px;
}

/* ===== 按钮 - 实心主题色 ===== */
QPushButton {
    background-color: #0B65D8;
    color: #FFFFFF;
    border: none;
    border-radius: 20px;
    padding: 8px 20px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #1D4ED8;
}
QPushButton:pressed {
    background-color: #1E3A8A;
}
QPushButton:disabled {
    color: #494551;
    background-color: #2D2D2D;
}

/* ===== 工具栏按钮 - 轮廓风格 ===== */
QToolBar QPushButton {
    background-color: transparent;
    color: #E5E1E7;
    border: 1px solid #494551;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 13px;
}
QToolBar QPushButton:hover {
    background-color: #253650;
    border-color: #0B65D8;
    color: #FFFFFF;
}
QToolBar QPushButton:pressed {
    background-color: #3D5A80;
}

/* ===== 标签 ===== */
QLabel {
    color: #E5E1E7;
    background: transparent;
}

/* ===== 输入框 ===== */
QLineEdit {
    background-color: #1E2530;
    border: 1px solid #494551;
    border-radius: 12px;
    padding: 10px 14px;
    color: #E5E1E7;
    font-size: 14px;
}
QLineEdit:focus {
    border: 2px solid #0B65D8;
    background-color: #1E2A3F;
}
QLineEdit::placeholder {
    color: #6B7280;
}

/* ===== 树形列表 (作业列表) ===== */
QTreeWidget {
    background-color: #1E2530;
    border: 1px solid #494551;
    border-radius: 12px;
    padding: 6px;
    outline: none;
    color: #E5E1E7;
}
QTreeWidget::item {
    padding: 10px 10px;
    border-radius: 8px;
    margin: 2px 4px;
    color: #E5E1E7;
}
QTreeWidget::item:hover {
    background-color: #253650;
}
QTreeWidget::item:selected {
    background-color: #3D5A80;
    color: #FFFFFF;
    font-weight: bold;
}
QTreeWidget::item:alternate {
    background-color: transparent;
}
QHeaderView::section {
    background-color: #1E2A3F;
    color: #CBC4D2;
    padding: 10px 8px;
    border: none;
    border-bottom: 1px solid #494551;
    font-weight: bold;
    font-size: 13px;
}

/* ===== 文本编辑框 (答案区域) ===== */
QTextEdit {
    background-color: #1E2530;
    border: 1px solid #494551;
    border-radius: 12px;
    padding: 16px;
    color: #E5E1E7;
    selection-background-color: #3D5A80;
    selection-color: #FFFFFF;
}

/* ===== 分割线 ===== */
QSplitter::handle {
    background-color: transparent;
}
QSplitter::handle:horizontal {
    width: 8px;
}
QSplitter::handle:hover {
    background-color: #494551;
    border-radius: 4px;
}

/* ===== 进度条 ===== */
QProgressBar {
    background-color: #2D2D2D;
    border: none;
    border-radius: 6px;
    text-align: center;
    color: transparent;
    min-height: 8px;
    max-height: 8px;
    margin: 8px 0;
}
QProgressBar::chunk {
    background-color: #0B65D8;
    border-radius: 6px;
}

/* ===== 下拉框 ===== */
QComboBox {
    background-color: #1E2530;
    border: 1px solid #494551;
    border-radius: 10px;
    padding: 8px 14px;
    color: #E5E1E7;
    min-width: 110px;
    font-size: 13px;
}
QComboBox:hover {
    border-color: #0B65D8;
}
QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}
QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}
QComboBox QAbstractItemView {
    border: 1px solid #494551;
    border-radius: 10px;
    background-color: #1E2530;
    color: #E5E1E7;
    selection-background-color: #3D5A80;
    selection-color: #FFFFFF;
    outline: none;
    padding: 4px;
}
QComboBox QAbstractItemView::item {
    padding: 8px 12px;
    border-radius: 6px;
}

/* ===== 状态栏 ===== */
QStatusBar {
    background-color: #1E2530;
    color: #CBC4D2;
    border-top: 1px solid #494551;
    font-size: 12px;
}
QStatusBar::item {
    border: none;
}

/* ===== 对话框 ===== */
QDialog {
    background-color: #1E1E1E;
}

/* ===== 分组框 ===== */
QGroupBox {
    border: 1px solid #494551;
    border-radius: 12px;
    margin-top: 20px;
    padding-top: 24px;
    font-weight: bold;
    color: #E5E1E7;
    font-size: 14px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    left: 16px;
    color: #CBC4D2;
}

/* ===== 复选框 ===== */
QCheckBox {
    color: #CBC4D2;
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #494551;
    border-radius: 4px;
    background-color: #1E2530;
}
QCheckBox::indicator:checked {
    background-color: #0B65D8;
    border-color: #0B65D8;
}

/* ===== 滚动条 ===== */
QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background-color: #494551;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #6B7280;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background-color: #494551;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #6B7280;
}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ===== 消息框 ===== */
QMessageBox {
    background-color: #1E1E1E;
}
QMessageBox QLabel {
    color: #E5E1E7;
}
QMessageBox QPushButton {
    min-width: 80px;
    min-height: 32px;
}

/* ===== 卡片面板 ===== */
QWidget[card="true"] {
    background-color: #1E2530;
    border: 1px solid #494551;
    border-radius: 16px;
    padding: 16px;
}
"""


LIGHT_STYLE = """
/* ===== 全局基础 ===== */
QWidget {
    background-color: #F8F9FA;
    color: #1E1E1E;
    font-family: "Microsoft YaHei", "Segoe UI", sans-serif;
    font-size: 14px;
}

/* ===== 主窗口 ===== */
QMainWindow {
    background-color: #F8F9FA;
}

/* ===== 顶部工具栏 ===== */
QToolBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E0E0E0;
    padding: 8px 12px;
    spacing: 10px;
}

/* ===== 按钮 - 实心主题色 ===== */
QPushButton {
    background-color: #0B65D8;
    color: #FFFFFF;
    border: none;
    border-radius: 20px;
    padding: 8px 20px;
    font-weight: bold;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #1D4ED8;
}
QPushButton:pressed {
    background-color: #1E3A8A;
}
QPushButton:disabled {
    color: #9CA3AF;
    background-color: #E5E7EB;
}

/* ===== 工具栏按钮 - 轮廓风格 ===== */
QToolBar QPushButton {
    background-color: transparent;
    color: #374151;
    border: 1px solid #D1D5DB;
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 13px;
}
QToolBar QPushButton:hover {
    background-color: #EFF6FF;
    border-color: #0B65D8;
    color: #0B65D8;
}
QToolBar QPushButton:pressed {
    background-color: #DBEAFE;
}

/* ===== 标签 ===== */
QLabel {
    color: #1E1E1E;
    background: transparent;
}

/* ===== 输入框 ===== */
QLineEdit {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 12px;
    padding: 10px 14px;
    color: #1E1E1E;
    font-size: 14px;
}
QLineEdit:focus {
    border: 2px solid #0B65D8;
    background-color: #FFFFFF;
}
QLineEdit::placeholder {
    color: #9CA3AF;
}

/* ===== 树形列表 (作业列表) ===== */
QTreeWidget {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 12px;
    padding: 6px;
    outline: none;
    color: #1E1E1E;
}
QTreeWidget::item {
    padding: 10px 10px;
    border-radius: 8px;
    margin: 2px 4px;
    color: #1E1E1E;
}
QTreeWidget::item:hover {
    background-color: #F3F4F6;
}
QTreeWidget::item:selected {
    background-color: #DBEAFE;
    color: #0B65D8;
    font-weight: bold;
}
QTreeWidget::item:alternate {
    background-color: transparent;
}
QHeaderView::section {
    background-color: #F8F9FA;
    color: #6B7280;
    padding: 10px 8px;
    border: none;
    border-bottom: 1px solid #E0E0E0;
    font-weight: bold;
    font-size: 13px;
}

/* ===== 文本编辑框 (答案区域) ===== */
QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 12px;
    padding: 16px;
    color: #1E1E1E;
    selection-background-color: #DBEAFE;
    selection-color: #1E1E1E;
}

/* ===== 分割线 ===== */
QSplitter::handle {
    background-color: transparent;
}
QSplitter::handle:horizontal {
    width: 8px;
}
QSplitter::handle:hover {
    background-color: #D1D5DB;
    border-radius: 4px;
}

/* ===== 进度条 ===== */
QProgressBar {
    background-color: #E5E7EB;
    border: none;
    border-radius: 6px;
    text-align: center;
    color: transparent;
    min-height: 8px;
    max-height: 8px;
    margin: 8px 0;
}
QProgressBar::chunk {
    background-color: #0B65D8;
    border-radius: 6px;
}

/* ===== 下拉框 ===== */
QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 10px;
    padding: 8px 14px;
    color: #1E1E1E;
    min-width: 110px;
    font-size: 13px;
}
QComboBox:hover {
    border-color: #0B65D8;
}
QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}
QComboBox::down-arrow {
    width: 10px;
    height: 10px;
}
QComboBox QAbstractItemView {
    border: 1px solid #E0E0E0;
    border-radius: 10px;
    background-color: #FFFFFF;
    color: #1E1E1E;
    selection-background-color: #DBEAFE;
    selection-color: #0B65D8;
    outline: none;
    padding: 4px;
}
QComboBox QAbstractItemView::item {
    padding: 8px 12px;
    border-radius: 6px;
}

/* ===== 状态栏 ===== */
QStatusBar {
    background-color: #FFFFFF;
    color: #6B7280;
    border-top: 1px solid #E0E0E0;
    font-size: 12px;
}
QStatusBar::item {
    border: none;
}

/* ===== 对话框 ===== */
QDialog {
    background-color: #F8F9FA;
}

/* ===== 分组框 ===== */
QGroupBox {
    border: 1px solid #E0E0E0;
    border-radius: 12px;
    margin-top: 20px;
    padding-top: 24px;
    font-weight: bold;
    color: #1E1E1E;
    font-size: 14px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 10px;
    left: 16px;
    color: #6B7280;
}

/* ===== 复选框 ===== */
QCheckBox {
    color: #6B7280;
    spacing: 8px;
    font-size: 13px;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #D1D5DB;
    border-radius: 4px;
    background-color: #FFFFFF;
}
QCheckBox::indicator:checked {
    background-color: #0B65D8;
    border-color: #0B65D8;
}

/* ===== 滚动条 ===== */
QScrollBar:vertical {
    background-color: transparent;
    width: 8px;
    border-radius: 4px;
}
QScrollBar::handle:vertical {
    background-color: #D1D5DB;
    border-radius: 4px;
    min-height: 30px;
}
QScrollBar::handle:vertical:hover {
    background-color: #9CA3AF;
}
QScrollBar::add-line:vertical,
QScrollBar::sub-line:vertical {
    height: 0;
}
QScrollBar:horizontal {
    background-color: transparent;
    height: 8px;
    border-radius: 4px;
}
QScrollBar::handle:horizontal {
    background-color: #D1D5DB;
    border-radius: 4px;
    min-width: 30px;
}
QScrollBar::handle:horizontal:hover {
    background-color: #9CA3AF;
}
QScrollBar::add-line:horizontal,
QScrollBar::sub-line:horizontal {
    width: 0;
}

/* ===== 消息框 ===== */
QMessageBox {
    background-color: #FFFFFF;
}
QMessageBox QLabel {
    color: #1E1E1E;
}
QMessageBox QPushButton {
    min-width: 80px;
    min-height: 32px;
}

/* ===== 卡片面板 ===== */
QWidget[card="true"] {
    background-color: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 16px;
    padding: 16px;
}
"""

# 向后兼容别名
MATERIAL_STYLE = DARK_STYLE