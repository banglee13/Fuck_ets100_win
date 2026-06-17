"""
UI 样式表 (Material Design 风格)
借鉴了 Android 版的 Monet Sky (天空蓝) 配色
Primary: #0B65D8
"""

MATERIAL_STYLE = """
/* 全局基础设置 */
QWidget {
    background-color: #F8F9FA;
    color: #1F2937;
    font-family: "Microsoft YaHei", "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif;
    font-size: 14px;
}

/* 顶部工具栏 */
QToolBar {
    background-color: #FFFFFF;
    border-bottom: 1px solid #E5E7EB;
    padding: 8px 12px;
    spacing: 12px;
}

/* 按钮 - 基础 (实心主题色按钮) */
QPushButton {
    background-color: #0B65D8;
    color: #FFFFFF;
    border: none;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: bold;
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

/* 工具栏中的按钮 (扁平/轮廓风格) */
QToolBar QPushButton {
    background-color: #FFFFFF;
    color: #0B65D8;
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    padding: 6px 12px;
}
QToolBar QPushButton:hover {
    background-color: #EFF6FF;
    border-color: #0B65D8;
}
QToolBar QPushButton:pressed {
    background-color: #DBEAFE;
}

/* 标签 */
QLabel {
    color: #374151;
    background: transparent;
}

/* 树形列表 (左侧作业列表) */
QTreeWidget {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 4px;
    outline: none; /* 隐藏选中时的虚线框 */
}
QTreeWidget::item {
    padding: 10px 8px;
    border-radius: 6px;
    margin: 2px 4px;
}
QTreeWidget::item:hover {
    background-color: #F3F4F6;
}
QTreeWidget::item:selected {
    background-color: #EFF6FF;
    color: #0B65D8;
    font-weight: bold;
}
QHeaderView::section {
    background-color: #F9FAFB;
    color: #4B5563;
    padding: 8px;
    border: none;
    border-bottom: 1px solid #E5E7EB;
    font-weight: bold;
}

/* 文本编辑框 (右侧答案区域) */
QTextEdit {
    background-color: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 16px;
    selection-background-color: #BFDBFE;
    selection-color: #1E3A8A;
}

/* 分割线 */
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

/* 进度条 */
QProgressBar {
    background-color: #E5E7EB;
    border: none;
    border-radius: 4px;
    text-align: center;
    color: transparent; /* 隐藏文字 */
    min-height: 8px;
    max-height: 8px;
    margin: 8px 0;
}
QProgressBar::chunk {
    background-color: #0B65D8;
    border-radius: 4px;
}

/* 下拉框 */
QComboBox {
    background-color: #FFFFFF;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 6px 12px;
    color: #374151;
    min-width: 100px;
}
QComboBox:hover {
    border-color: #0B65D8;
}
QComboBox::drop-down {
    border: none;
    padding-right: 8px;
}
QComboBox QAbstractItemView {
    border: 1px solid #E5E7EB;
    border-radius: 6px;
    background-color: #FFFFFF;
    selection-background-color: #EFF6FF;
    selection-color: #0B65D8;
    outline: none;
}
QComboBox QAbstractItemView::item {
    padding: 8px;
    border-radius: 4px;
}

/* 状态栏 */
QStatusBar {
    background-color: #FFFFFF;
    color: #6B7280;
    border-top: 1px solid #E5E7EB;
}
QStatusBar::item {
    border: none;
}

/* 对话框通用 (如登录框) */
QDialog {
    background-color: #FFFFFF;
}
QLineEdit {
    background-color: #F9FAFB;
    border: 1px solid #D1D5DB;
    border-radius: 6px;
    padding: 8px 12px;
    color: #1F2937;
}
QLineEdit:focus {
    border: 2px solid #0B65D8;
    background-color: #FFFFFF;
}
QGroupBox {
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    margin-top: 16px;
    font-weight: bold;
    color: #374151;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 8px;
    left: 16px;
}
QCheckBox {
    spacing: 8px;
    color: #4B5563;
}
QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 1px solid #D1D5DB;
    border-radius: 4px;
    background-color: #FFFFFF;
}
QCheckBox::indicator:checked {
    background-color: #0B65D8;
    border: 1px solid #0B65D8;
    image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='14' height='14' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'><polyline points='20 6 9 17 4 12'></polyline></svg>");
}
QCheckBox::indicator:hover {
    border-color: #0B65D8;
}
/* 卡片样式：用于分组或特殊容器 */
QWidget[card="true"] {
    background-color: #FFFFFF;
    border: 1px solid rgba(14,30,37,0.06);
    border-radius: 12px;
    padding: 12px;
}

/* 更圆润的工具栏视觉 */
QToolBar {
    border-radius: 10px;
    padding: 10px;
}

/* 滚动条样式 */
QScrollBar:vertical {
    background: transparent;
    width: 10px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #D1D5DB;
    min-height: 20px;
    border-radius: 6px;
}
QScrollBar::handle:vertical:hover {
    background: #9CA3AF;
}
QScrollBar::add-line, QScrollBar::sub-line { height: 0px; }

/* 对话框标题更醒目 */
QDialog QLabel {
    font-size: 16px;
}
"""