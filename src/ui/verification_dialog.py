"""
验证对话框 - 集成畅言网页验证页
当密码错误次数过多时，需要通过此对话框完成人工验证
"""

import json
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui import QFont
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings

logger = logging.getLogger(__name__)


class VerificationThread(QThread):
    """验证线程 - 监听 WebView 中的验证完成"""
    verification_success = pyqtSignal(dict)  # 返回 uid + captchaResult
    verification_failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.verification_data = None
        self.is_completed = False

    def set_verification_data(self, data):
        """从 WebView JS 回调接收验证数据"""
        self.verification_data = data
        self.is_completed = True


class VerificationDialog(QDialog):
    """验证对话框 - 使用 WebView 打开畅言验证页"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("身份验证 - ETS100")
        self.setMinimumSize(500, 700)
        self.verification_data = None
        self._init_ui()

    def _init_ui(self):
        """初始化 UI"""
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)

        # 标题
        title = QLabel("请完成身份验证")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        layout.addWidget(title)

        # 说明
        desc = QLabel(
            "由于登录尝试次数过多，系统要求您完成身份验证后才能继续。\n"
            "请在下方页面中完成验证。"
        )
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # WebView
        self.webview = QWebEngineView()
        
        # 配置 WebView 设置
        settings = self.webview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        
        # 注入 JS bridge
        self.webview.page().scripts.clear()
        script = """
        (function() {
            if (window.__feEtsVerificationInstalled) return;
            window.__feEtsVerificationInstalled = true;
            
            if (!window.$) {
                // 如果 jQuery 未加载，定期重试注入
                setTimeout(arguments.callee, 500);
                return;
            }
            
            $(document).ajaxComplete(function(event, xhr, settings) {
                if (!settings || !settings.url) return;
                
                // 监听 checkLogin 响应
                if (settings.url.indexOf('/login/checkLogin') !== -1) {
                    try {
                        var responseBody = xhr.responseText || '';
                        var data = JSON.parse(responseBody);
                        
                        if (data.Code === 0 && data.Data) {
                            var dataObj = data.Data;
                            if (typeof dataObj === 'string') {
                                dataObj = JSON.parse(dataObj);
                            }
                            
                            if (dataObj.uid && dataObj.captchaResult) {
                                // 验证成功，通知 Python
                                if (window.etsBridge && window.etsBridge.verificationComplete) {
                                    window.etsBridge.verificationComplete(JSON.stringify({
                                        uid: dataObj.uid,
                                        captchaResult: dataObj.captchaResult
                                    }));
                                }
                            }
                        }
                    } catch (e) {
                        console.error("验证解析失败", e);
                    }
                }
            });
        })();
        """
        
        from PyQt6.QtWebEngineCore import QWebEngineScript
        script_obj = QWebEngineScript()
        script_obj.setSourceCode(script)
        script_obj.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentStart)
        script_obj.setRunsOnSubFrames(False)
        self.webview.page().scripts.insert(script_obj)
        
        # 设置 JS bridge
        self.webview.page().javaScriptConsoleMessage.connect(self._on_js_log)
        
        # 加载验证页
        verification_url = (
            "https://pass.changyan.com/login?"
            "nextpage=aHR0cHM6Ly93d3cuZXRzMTAwLmNvbS9sb2dpbkNoZWNrLmh0bWw%3D&"
            "customConfig=e2hpZGRlbl9tb2R1bGU6ICJoZWFkZXIsdGFpbCxsb2dpbkJ5VmVyaWZ5Q29kZSxyZWdpc3Rlcixsb2dpbkJ5VGhpcmRMb2dpbiIscHJvZHVjdF9hcHBrZXk6InFpbmdkYW9fZXRzIiwibmVlZFRpY2tldCI6InRydWUiLCJsb2dpbl9ub3RBdXRvIjoidHJ1ZSJ9&"
            "from=ew&"
            "appId=pass6port18"
        )
        
        self.webview.load(QUrl(verification_url))
        layout.addWidget(self.webview)

        # 进度条（初始隐藏）
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        # 按钮
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.reject)
        layout.addWidget(self.close_btn)

        self.setLayout(layout)
        
        # 启动监听线程
        self.verification_thread = VerificationThread()
        self.verification_thread.start()
        
        # 添加自定义 JS bridge
        self._setup_js_bridge()

    def _setup_js_bridge(self):
        """设置 JavaScript bridge"""
        from PyQt6.QtCore import QObject
        
        class EtsBridge(QObject):
            verification_complete_signal = pyqtSignal(str)
            
            def verificationComplete(self, data):
                """从 JS 接收验证完成信号"""
                self.verification_complete_signal.emit(data)
        
        self.bridge = EtsBridge()
        self.bridge.verification_complete_signal.connect(self._on_verification_complete)
        
        # 注册 bridge 到 WebView
        self.webview.page().addScriptMessageHandler(self.bridge, "etsBridge")

    def _on_verification_complete(self, data_str):
        """当 JS 传回验证数据时触发"""
        try:
            self.verification_data = json.loads(data_str)
            self.accept()
        except Exception as e:
            logger.error(f"解析验证数据失败: {e}")
            QMessageBox.critical(self, "错误", f"解析验证数据失败: {e}")

    def _on_js_log(self, level, message, line_number, source_id):
        """处理 JS 控制台消息"""
        logger.debug(f"JS Log: {message}")

    def get_verification_data(self):
        """获取验证数据"""
        return self.verification_data
