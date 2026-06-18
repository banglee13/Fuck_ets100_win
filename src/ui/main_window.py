"""
主窗口
"""

import os
import shutil
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTreeWidget, QTreeWidgetItem,
    QSplitter, QTextEdit, QMessageBox, QProgressBar,
    QFileDialog, QToolBar, QStatusBar, QMenu, QDialog,
    QApplication, QComboBox, QLineEdit
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl, QTimer
from PyQt6.QtGui import QIcon, QFont, QDesktopServices
import logging

from core import (
    ETS100ApiClient, AuthManager, ZipPasswordGenerator,
    AnswerParser, HomeworkListResponse, HomeworkInfo
)
from ui.login_dialog import LoginDialog

logger = logging.getLogger(__name__)


class LoadHomeworkWorker(QThread):
    """加载作业工作线程"""
    load_success = pyqtSignal(HomeworkListResponse)
    load_failed = pyqtSignal(str)
    load_progress = pyqtSignal(str)

    def __init__(self, auth_manager: AuthManager, status: str = "1"):
        super().__init__()
        self.auth_manager = auth_manager
        self.status = status
        self.client = ETS100ApiClient()

    def run(self):
        try:
            info = self.auth_manager.get_login_info()
            if not info:
                self.load_failed.emit("未找到登录信息，请重新登录")
                return

            token = info.get("token")
            parent_id = info.get("parent_account_id")
            
            if not token or not parent_id:
                self.load_failed.emit("登录信息不完整，请重新登录")
                return

            self.load_progress.emit("获取作业列表...")
            hw_resp = self.client.get_homework_list(token, parent_id, self.status)
            
            # 如果请求失败（例如 token 过期）
            code = hw_resp.get("code", -1)
            if code != 0:
                phone = info.get("phone")
                password = info.get("password")
                device_code = self.auth_manager.get_device_code()

                if not password:
                    self.load_failed.emit("登录已过期且未保存密码，请重新登录")
                    return

                self.load_progress.emit("正在重新登录...")
                resp = self.client.login(phone, password, device_code)
                login_code = resp.get("code", -1)

                if login_code == 30014:
                    resp = self.client.bind_device(phone, password, device_code)

                token = resp.get("body", {}).get("token", "")
                if not token:
                    self.load_failed.emit("重新登录失败，请手动登录")
                    return
                
                # 更新 token
                self.auth_manager.save_login_info(phone, token, parent_id, password)
                
                self.load_progress.emit("获取作业列表...")
                hw_resp = self.client.get_homework_list(token, parent_id, self.status)
                if hw_resp.get("code", -1) != 0:
                    self.load_failed.emit(hw_resp.get("msg", "获取作业列表失败"))
                    return

            result = HomeworkListResponse(hw_resp)
            self.load_success.emit(result)

        except Exception as e:
            logger.error(f"加载作业异常: {e}")
            self.load_failed.emit(f"加载失败: {str(e)}")


class DownloadHomeworkWorker(QThread):
    """下载作业工作线程"""
    download_success = pyqtSignal(str, list)
    download_failed = pyqtSignal(str)
    download_progress = pyqtSignal(str, int)

    def __init__(
        self, 
        homework: HomeworkInfo, 
        base_url: str, 
        cache_dir: str
    ):
        super().__init__()
        self.homework = homework
        self.base_url = base_url
        self.cache_dir = cache_dir
        self.client = ETS100ApiClient()

    def run(self):
        try:
            parsed_sections = []
            total = len(self.homework.contents)
            
            for idx, content in enumerate(self.homework.contents):
                self.download_progress.emit(f"正在下载: {content.group_name}", int((idx / total) * 80))

                url = content.url
                if not url.startswith("http"):
                    base = self.base_url.rstrip("/")
                    url = f"{base}{url if url.startswith('/') else '/' + url}"
                url = url.replace("http://", "https://")

                filename = os.path.basename(url.split("?")[0])
                zip_path = os.path.join(self.cache_dir, filename)

                if not os.path.exists(zip_path):
                    success = self.client.download_file(
                        url, 
                        zip_path,
                        lambda d, t: self.download_progress.emit(
                            f"下载中: {content.group_name}",
                            int((idx / total) * 80 + (d / t) * (80 / total))
                        )
                    )
                    if not success:
                        logger.warning(f"下载失败: {url}")
                        continue

                self.download_progress.emit(f"正在解压: {content.group_name}", int((idx + 0.5) / total * 80))
                
                password = ZipPasswordGenerator.generate_password(zip_path)
                if not password:
                    logger.warning(f"无法生成密码: {zip_path}")
                    continue

                extract_dir = os.path.join(self.cache_dir, filename.replace(".zip", ""))
                if not os.path.exists(extract_dir):
                    success = ZipPasswordGenerator.extract_zip(zip_path, extract_dir, password)
                    if not success:
                        logger.warning(f"解压失败: {zip_path}")
                        continue

                content_json = os.path.join(extract_dir, "content.json")
                if os.path.exists(content_json):
                    self.download_progress.emit(f"正在解析: {content.group_name}", int((idx + 0.8) / total * 80))
                    
                    parsed = AnswerParser.parse_content_json(content_json)
                    if parsed:
                        parsed["group_name"] = content.group_name
                        parsed_sections.append(parsed)

            self.download_progress.emit("完成！", 100)
            self.download_success.emit(self.homework.name, parsed_sections)

        except Exception as e:
            logger.error(f"下载作业异常: {e}")
            self.download_failed.emit(f"下载失败: {str(e)}")


class MainWindow(QMainWindow):
    """主窗口"""

    def __init__(self):
        super().__init__()
        self.auth_manager = AuthManager()
        self.cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        self.homework_list = []
        self.base_url = ""
        self.current_homework_data = {}

        self.setWindowTitle("Fuck ETS100 - Windows 版本")
        self.setMinimumSize(1000, 700)
        self._init_ui()
        QTimer.singleShot(0, self._check_login)

    def _init_ui(self):
        """初始化 UI"""
        # 工具栏
        toolbar = QToolBar()
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        self.refresh_btn = QPushButton("刷新作业")
        # 使用简洁的 emoji 图标以增强视觉识别
        self.refresh_btn.setText("🔄 刷新")
        self.refresh_btn.clicked.connect(self._load_homework)
        toolbar.addWidget(self.refresh_btn)

        toolbar.addSeparator()

        self.logout_btn = QPushButton("退出登录")
        self.logout_btn.setText("🔒 退出")
        self.logout_btn.clicked.connect(self._logout)
        toolbar.addWidget(self.logout_btn)

        toolbar.addSeparator()

        self.open_cache_btn = QPushButton("打开缓存目录")
        self.open_cache_btn.setText("📁 缓存")
        self.open_cache_btn.clicked.connect(self._open_cache_dir)
        toolbar.addWidget(self.open_cache_btn)

        # 清理缓存按钮（位于缓存按钮右侧）
        self.clear_cache_btn = QPushButton("🧹 清理缓存")
        self.clear_cache_btn.clicked.connect(self._clear_cache_dir)
        toolbar.addWidget(self.clear_cache_btn)

        toolbar.addSeparator()

        self.export_btn = QPushButton("导出答案")
        self.export_btn.setText("📤 导出")
        self.export_btn.clicked.connect(self._export_answers)
        toolbar.addWidget(self.export_btn)

        # 中央部件
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧 - 作业列表
        left_panel = QWidget()
        left_panel.setProperty("card", "true")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)

        left_label = QLabel("作业列表")
        left_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))

        self.status_combo = QComboBox()
        self.status_combo.addItem("当前作业", "1")
        self.status_combo.addItem("历史作业", "2")
        self.status_combo.currentIndexChanged.connect(self._load_homework)

        header_layout = QHBoxLayout()
        header_layout.addWidget(left_label)
        header_layout.addStretch()
        header_layout.addWidget(self.status_combo)

        left_layout.addLayout(header_layout)

        # 搜索框：用于快速筛选作业列表（类似 Android 列表的即时过滤）
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("搜索作业...")
        try:
            self.search_input.setClearButtonEnabled(True)
        except Exception:
            pass
        self.search_input.textChanged.connect(self._filter_homework)
        left_layout.addWidget(self.search_input)

        self.homework_tree = QTreeWidget()
        self.homework_tree.setHeaderLabels(["作业名称"])
        self.homework_tree.itemClicked.connect(self._on_homework_clicked)
        # 更友好的交互体验
        self.homework_tree.setAlternatingRowColors(True)
        self.homework_tree.setIndentation(12)
        left_layout.addWidget(self.homework_tree)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        left_layout.addWidget(self.progress_bar)

        self.status_label_left = QLabel("")
        left_layout.addWidget(self.status_label_left)

        splitter.addWidget(left_panel)

        # 右侧 - 答案显示
        right_panel = QWidget()
        right_panel.setProperty("card", "true")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)

        self.right_label = QLabel("请选择作业")
        self.right_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        right_layout.addWidget(self.right_label)

        self.answer_text = QTextEdit()
        self.answer_text.setReadOnly(True)
        self.answer_text.setFont(QFont("Microsoft YaHei", 10))
        right_layout.addWidget(self.answer_text)

        splitter.addWidget(right_panel)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 2)

        main_layout.addWidget(splitter)

        # 状态栏
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def _check_login(self):
        """检查登录状态"""
        if not self.auth_manager.is_logged_in():
            self._show_login_dialog()
        else:
            self._load_homework()

    def _show_login_dialog(self):
        """显示登录对话框"""
        self.hide()
        dialog = LoginDialog(self.auth_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.show()
            self._load_homework()
        else:
            QApplication.instance().quit()

    def _load_homework(self):
        """加载作业列表"""
        if not self.auth_manager.is_logged_in():
            self._show_login_dialog()
            return

        self.refresh_btn.setEnabled(False)
        self.status_combo.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.status_label_left.setText("正在加载...")
        self.homework_tree.clear()

        status = self.status_combo.currentData()
        self.worker = LoadHomeworkWorker(self.auth_manager, status)
        self.worker.load_success.connect(self._on_homework_loaded)
        self.worker.load_failed.connect(self._on_homework_load_failed)
        self.worker.load_progress.connect(self._on_load_progress)
        self.worker.start()

    def _on_homework_loaded(self, result: HomeworkListResponse):
        """作业加载成功"""
        self.homework_list = result.homeworks
        self.base_url = result.base_url

        for hw in self.homework_list:
            item = QTreeWidgetItem([hw.name])
            item.setData(0, Qt.ItemDataRole.UserRole, hw)
            self.homework_tree.addTopLevelItem(item)

        self.refresh_btn.setEnabled(True)
        self.status_combo.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label_left.setText(f"共 {len(self.homework_list)} 份作业")
        self.statusBar.showMessage("加载成功")

    def _filter_homework(self, text: str):
        """根据搜索文本过滤左侧作业列表"""
        if text is None:
            text = ""
        needle = text.strip().lower()
        count = self.homework_tree.topLevelItemCount()
        for i in range(count):
            item = self.homework_tree.topLevelItem(i)
            name = (item.text(0) or "").lower()
            # 隐藏不匹配的项
            item.setHidden(bool(needle) and (needle not in name))

    def _on_homework_load_failed(self, error: str):
        """作业加载失败"""
        self.refresh_btn.setEnabled(True)
        self.status_combo.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label_left.setText("加载失败")
        QMessageBox.critical(self, "错误", error)
        
        if "重新登录" in error:
            self._show_login_dialog()

    def _on_load_progress(self, message: str):
        """加载进度"""
        self.status_label_left.setText(message)

    def _on_homework_clicked(self, item: QTreeWidgetItem, column: int):
        """作业点击"""
        homework = item.data(0, Qt.ItemDataRole.UserRole)
        if not homework:
            return

        if homework.name in self.current_homework_data:
            self._display_answers(homework.name, self.current_homework_data[homework.name])
        else:
            self._download_and_parse_homework(homework)

    def _download_and_parse_homework(self, homework: HomeworkInfo):
        """下载并解析作业"""
        self.right_label.setText(f"正在下载: {homework.name}")
        self.answer_text.clear()
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)

        self.download_worker = DownloadHomeworkWorker(homework, self.base_url, self.cache_dir)
        self.download_worker.download_success.connect(self._on_download_success)
        self.download_worker.download_failed.connect(self._on_download_failed)
        self.download_worker.download_progress.connect(self._on_download_progress)
        self.download_worker.start()

    def _on_download_success(self, name: str, sections: list):
        """下载成功"""
        self.current_homework_data[name] = sections
        self.progress_bar.setVisible(False)
        self._display_answers(name, sections)
        self.statusBar.showMessage("下载成功")

    def _on_download_failed(self, error: str):
        """下载失败"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "错误", error)

    def _on_download_progress(self, message: str, value: int):
        """下载进度"""
        self.progress_bar.setValue(value)
        self.right_label.setText(message)

    def _display_answers(self, name: str, sections: list):
        """显示答案"""
        self.right_label.setText(name)
        
        # 注入美化用的 CSS
        html = f"""
        <style>
            body {{ font-family: "Microsoft YaHei", sans-serif; color: #1F2937; line-height: 1.6; }}
            h2 {{ color: #0B65D8; border-bottom: 2px solid #E5E7EB; padding-bottom: 8px; }}
            h3 {{ color: #374151; margin-top: 24px; background-color: #F3F4F6; padding: 8px 12px; border-radius: 6px; }}
            .question-card {{ background-color: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 8px; padding: 16px; margin-bottom: 16px; }}
            .question-title {{ font-weight: bold; font-size: 15px; margin-bottom: 8px; color: #111827; }}
            ul {{ list-style-type: none; padding-left: 0; margin-top: 8px; }}
            li {{ padding: 6px 8px; margin-bottom: 4px; border-radius: 4px; background-color: #F9FAFB; }}
            .correct-option {{ color: #059669; font-weight: bold; background-color: #D1FAE5; }}
            .answer-box {{ margin-top: 12px; padding: 10px; background-color: #EFF6FF; border-left: 4px solid #0B65D8; border-radius: 4px; }}
            .answer-label {{ font-weight: bold; color: #1E3A8A; }}
            hr {{ border: none; }}
        </style>
        """
        html += f"<h2>{name}</h2>"
        
        for section in sections:
            group_name = section.get("group_name", section.get("type_name", "未知"))
            html += f"<h3>{group_name}</h3>"
            
            questions = section.get("questions", [])
            for q in questions:
                html += "<div class='question-card'>"
                if "options" in q:
                    # 选择题
                    q_num = q.get('number', q.get('index', 0) + 1)
                    html += f"<div class='question-title'>{q_num}. {q['question']}</div>"
                    html += "<ul>"
                    for opt in q["options"]:
                        is_correct = opt["label"] == q["answer"]
                        li_class = "correct-option" if is_correct else ""
                        html += f"<li class='{li_class}'>{opt['label']}. {opt['text']}</li>"
                    html += f"</ul><div class='answer-box'><span class='answer-label'>答案:</span> {q['answer']}</div>"
                elif "answer" in q:
                    # 填空题
                    q_num = q.get('number', q.get('index', 0) + 1)
                    html += f"<div class='question-title'>{q_num}. 填空题</div>"
                    html += f"<div class='answer-box'><span class='answer-label'>答案:</span> {q['answer']}</div>"
                elif "topic" in q:
                    # 信息转述
                    html += f"<div class='question-title'>主题: {q['topic']}</div>"
                    if q.get("original_text"):
                        html += f"<div><b>原文:</b><br/>{q['original_text'].replace(chr(10), '<br>')}</div>"
                    if q.get("answers"):
                        html += "<div class='answer-box'><span class='answer-label'>参考答案:</span><br/>"
                        for ans in q["answers"]:
                            html += f"<div>{ans.replace(chr(10), '<br>')}</div>"
                        html += "</div>"
                elif "type" in q and q["type"] == "read":
                    # 模仿朗读
                    html += f"<div class='question-title'>模仿朗读</div>"
                    html += f"<div class='answer-box'><span class='answer-label'>原文:</span><br/>{q.get('original_text', '').replace(chr(10), '<br>')}</div>"
                else:
                    # 问答题
                    q_num = q.get('index', 0) + 1
                    html += f"<div class='question-title'>{q_num}. {q['question']}</div>"
                    if q.get("answers"):
                        html += "<div class='answer-box'><span class='answer-label'>参考答案:</span><br/>"
                        for ans in q["answers"]:
                            html += f"<div>{ans.replace(chr(10), '<br>')}</div>"
                        html += "</div>"
                html += "</div>"
        
        self.answer_text.setHtml(html)

    def _logout(self):
        """退出登录"""
        reply = QMessageBox.question(
            self, "确认", "确定要退出登录吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.auth_manager.logout()
            self.current_homework_data.clear()
            self.homework_tree.clear()
            self.answer_text.clear()
            self.right_label.setText("请选择作业")
            self._show_login_dialog()

    def _open_cache_dir(self):
        """打开缓存目录"""
        QDesktopServices.openUrl(QUrl.fromLocalFile(self.cache_dir))

    def _clear_cache_dir(self):
        """清理缓存目录内的所有内容（保留缓存根目录）"""
        reply = QMessageBox.question(
            self, "确认", "确定要清空缓存目录吗？此操作不可恢复。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # 删除缓存目录下的所有文件和子目录
            for name in os.listdir(self.cache_dir):
                path = os.path.join(self.cache_dir, name)
                if os.path.isfile(path) or os.path.islink(path):
                    os.remove(path)
                elif os.path.isdir(path):
                    shutil.rmtree(path)

            # 确保目录存在
            os.makedirs(self.cache_dir, exist_ok=True)

            self.statusBar.showMessage("缓存已清理")
            QMessageBox.information(self, "完成", "缓存已成功清理")
        except Exception as e:
            logger.error(f"清理缓存失败: {e}")
            QMessageBox.critical(self, "错误", f"清理缓存失败: {e}")

    def _export_answers(self):
        """导出答案"""
        selected_items = self.homework_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "提示", "请先选择一个作业")
            return

        hw = selected_items[0].data(0, Qt.ItemDataRole.UserRole)
        if not hw or hw.name not in self.current_homework_data:
            QMessageBox.warning(self, "提示", "请先下载并解析该作业")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self, "导出答案", f"{hw.name}.txt", "Text Files (*.txt);;All Files (*)"
        )
        if not file_path:
            return

        try:
            sections = self.current_homework_data[hw.name]
            text = f"{'='*50}\n{hw.name}\n{'='*50}\n\n"

            for section in sections:
                group_name = section.get("group_name", section.get("type_name", "未知"))
                text += f"\n【{group_name}】\n{'-'*30}\n"

                questions = section.get("questions", [])
                for q in questions:
                    if "options" in q:
                        q_num = q.get('number', q.get('index', 0) + 1)
                        text += f"\n{q_num}. {q['question']}\n"
                        for opt in q["options"]:
                            mark = "★" if opt["label"] == q["answer"] else " "
                            text += f"  {mark} {opt['label']}. {opt['text']}\n"
                        text += f"  答案: {q['answer']}\n"
                    elif "answer" in q:
                        q_num = q.get('number', q.get('index', 0) + 1)
                        text += f"\n{q_num}. 答案: {q['answer']}\n"
                    elif "topic" in q:
                        text += f"\n主题: {q['topic']}\n"
                        if q.get("original_text"):
                            text += f"\n原文:\n{q['original_text']}\n"
                        if q.get("answers"):
                            text += "\n参考答案:\n"
                            for ans in q["answers"]:
                                text += f"{ans}\n"
                    elif "type" in q and q["type"] == "read":
                        text += f"\n模仿朗读原文:\n{q.get('original_text', '')}\n"
                    else:
                        q_num = q.get('index', 0) + 1
                        text += f"\n{q_num}. {q['question']}\n"
                        if q.get("answers"):
                            text += "参考答案:\n"
                            for ans in q["answers"]:
                                text += f"{ans}\n"

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(text)

            QMessageBox.information(self, "成功", "导出成功！")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"导出失败: {e}")
