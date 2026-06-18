"""
登录对话框
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QGroupBox,
    QFormLayout, QCheckBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
import logging

from core import ETS100ApiClient, AuthManager, EcardAccount
from ui.verification_dialog_v2 import VerificationDialog

logger = logging.getLogger(__name__)


class LoginWorker(QThread):
    """登录工作线程"""
    login_success = pyqtSignal(dict)
    login_failed = pyqtSignal(str)
    login_progress = pyqtSignal(str, int)
    verification_required = pyqtSignal()  # 需要验证时发出此信号

    def __init__(self, phone: str, password: str, device_code: str):
        super().__init__()
        self.phone = phone
        self.password = password
        self.device_code = device_code
        self.client = ETS100ApiClient()
        self.verification_data = None  # 来自验证对话框的数据

    def set_verification_data(self, verification_data):
        """设置验证数据（从验证对话框获取）"""
        self.verification_data = verification_data

    def run(self):
        try:
            # 如果有验证数据，使用验证登录流程
            if self.verification_data:
                return self._login_with_verification()
            
            # 标准密码登录流程
            self.login_progress.emit("正在登录...", 20)
            
            resp = self.client.login(self.phone, self.password, self.device_code)
            code = resp.get("code", -1)
            
            if code == 30014:
                self.login_progress.emit("设备需要绑定，正在绑定...", 40)
                resp = self.client.bind_device(self.phone, self.password, self.device_code)
                code = resp.get("code", -1)
            
            # 检测是否需要验证（根据错误消息）
            if code != 0 and code != -1:
                msg = resp.get("msg", "登录失败")
                # 检查是否是验证错误
                if "验证" in msg or "尝试" in msg or "太多" in msg:
                    self.login_progress.emit("需要完成身份验证，请在弹出窗口完成验证", 30)
                    self.verification_required.emit()
                    return
                self.login_failed.emit(msg)
                return

            token = resp.get("body", {}).get("token", "")
            if not token:
                self.login_failed.emit("未获取到 Token")
                return

            self._complete_login(token)

        except Exception as e:
            logger.error(f"登录异常: {e}")
            self.login_failed.emit(f"登录异常: {str(e)}")

    def _login_with_verification(self):
        """使用验证凭证登录"""
        try:
            self.login_progress.emit("正在使用验证凭证登录...", 20)
            
            uid = self.verification_data.get("uid")
            captcha_result = self.verification_data.get("captchaResult")
            
            if not uid or not captcha_result:
                self.login_failed.emit("验证凭证不完整")
                return
            
            resp = self.client.login_with_verification(uid, captcha_result, self.device_code)
            code = resp.get("code", -1)
            
            if code != 0 and code != -1:
                msg = resp.get("msg", "验证登录失败")
                self.login_failed.emit(msg)
                return
            
            token = resp.get("body", {}).get("token", "")
            if not token:
                self.login_failed.emit("未获取到 Token")
                return
            
            self._complete_login(token)
        
        except Exception as e:
            logger.error(f"验证登录异常: {e}")
            self.login_failed.emit(f"验证登录异常: {str(e)}")

    def _complete_login(self, token: str):
        """完成登录流程：获取账户信息"""
        try:
            self.login_progress.emit("获取账户信息...", 60)
            
            ecard_resp = self.client.get_ecard_list(token)
            body = ecard_resp.get("body", {})
            
            selected_account = None
            for key, account_data in body.items():
                if not account_data:
                    continue
                account = EcardAccount(key, account_data)
                if account.is_valid:
                    selected_account = account
                    break
            
            if not selected_account and body:
                first_key = next(iter(body.keys()))
                selected_account = EcardAccount(first_key, body[first_key])

            if not selected_account or not selected_account.parent_id:
                self.login_failed.emit("未找到有效的账户信息")
                return

            self.login_progress.emit("登录成功！", 100)
            
            result = {
                "phone": self.phone,
                "password": self.password,
                "token": token,
                "parent_account_id": selected_account.parent_id,
                "account_name": selected_account.name
            }
            
            self.login_success.emit(result)
        
        except Exception as e:
            logger.error(f"获取账户信息异常: {e}")
            self.login_failed.emit(f"获取账户信息失败: {str(e)}")


class LoginDialog(QDialog):
    """登录对话框"""

    def __init__(self, auth_manager: AuthManager, parent=None):
        super().__init__(parent)
        self.auth_manager = auth_manager
        self.setWindowTitle("登录 - Fuck ETS100")
        self.setMinimumSize(400, 350)
        self._init_ui()
        self._load_saved_info()

    def _init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # 标题
        title_label = QLabel("Fuck ETS100")
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        subtitle = QLabel("Windows 版本")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(subtitle)

        # 登录表单
        form_group = QGroupBox("登录信息")
        form_layout = QFormLayout()

        self.phone_input = QLineEdit()
        self.phone_input.setPlaceholderText("请输入手机号")
        form_layout.addRow("手机号:", self.phone_input)

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("请输入密码")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        form_layout.addRow("密  码:", self.password_input)

        self.save_password_cb = QCheckBox("记住密码")
        form_layout.addRow("", self.save_password_cb)

        form_group.setLayout(form_layout)
        layout.addWidget(form_group)

        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 状态标签
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # 按钮
        btn_layout = QHBoxLayout()
        
        self.login_btn = QPushButton("登录")
        self.login_btn.setMinimumHeight(40)
        self.login_btn.clicked.connect(self._on_login_clicked)
        btn_layout.addWidget(self.login_btn)

        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setMinimumHeight(40)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def _load_saved_info(self):
        """加载保存的登录信息"""
        info = self.auth_manager.get_login_info()
        if info:
            self.phone_input.setText(info.get("phone", ""))
            if info.get("password"):
                self.password_input.setText(info.get("password"))
                self.save_password_cb.setChecked(True)

    def _on_login_clicked(self):
        """登录按钮点击"""
        phone = self.phone_input.text().strip()
        password = self.password_input.text().strip()

        if not phone or not password:
            QMessageBox.warning(self, "提示", "请输入手机号和密码")
            return

        device_code = self.auth_manager.get_device_code()

        self.login_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("")

        self.worker = LoginWorker(phone, password, device_code)
        self.worker.login_success.connect(self._on_login_success)
        self.worker.login_failed.connect(self._on_login_failed)
        self.worker.login_progress.connect(self._on_login_progress)
        self.worker.verification_required.connect(self._on_verification_required)
        self.worker.start()

    def _on_verification_required(self):
        """需要身份验证"""
        self.login_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # 显示验证对话框
        verification_dialog = VerificationDialog(self)
        if verification_dialog.exec() == QDialog.DialogCode.Accepted:
            verification_data = verification_dialog.get_verification_data()
            if verification_data:
                # 用验证凭证重新登录
                self._login_with_verification(verification_data)
            else:
                QMessageBox.warning(self, "错误", "未获取到验证凭证")
        else:
            # 用户取消验证
            self.status_label.setText("已取消验证")

    def _login_with_verification(self, verification_data: dict):
        """使用验证凭证重新登录"""
        device_code = self.auth_manager.get_device_code()
        
        self.login_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.status_label.setText("")
        
        # 创建新的 worker，设置验证数据
        self.worker = LoginWorker(self.phone_input.text().strip(), self.password_input.text().strip(), device_code)
        self.worker.set_verification_data(verification_data)
        self.worker.login_success.connect(self._on_login_success)
        self.worker.login_failed.connect(self._on_login_failed)
        self.worker.login_progress.connect(self._on_login_progress)
        self.worker.start()

    def _on_login_success(self, result: dict):
        """登录成功"""
        phone = result["phone"]
        password = result["password"] if self.save_password_cb.isChecked() else None
        token = result["token"]
        parent_id = result["parent_account_id"]

        self.auth_manager.save_login_info(phone, token, parent_id, password)
        
        QMessageBox.information(self, "成功", f"登录成功！\n账户: {result.get('account_name', phone)}")
        self.accept()

    def _on_login_failed(self, error_msg: str):
        """登录失败"""
        self.login_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "错误", error_msg)

    def _on_login_progress(self, message: str, value: int):
        """登录进度"""
        self.status_label.setText(message)
        self.progress_bar.setValue(value)
