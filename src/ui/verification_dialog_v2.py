"""
验证对话框 - 集成畅言网页验证页
当密码错误次数过多时，需要通过此对话框完成人工验证
桌面端版本：使用桌面 UA、大尺寸窗口
"""

import json
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton, QMessageBox, QHBoxLayout
)
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings, QWebEngineScript

# 桌面端 User-Agent（非手机版）
DESKTOP_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/148.0.0.0 Safari/537.36"
)

logger = logging.getLogger(__name__)


class VerificationDialog(QDialog):
    """验证对话框 - 使用 WebView 打开畅言验证页（桌面端适配）"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("身份验证 - ETS100")
        self.setMinimumSize(850, 680)
        self.resize(900, 720)
        self.verification_data = None
        self._setup_ui()

    def _setup_ui(self):
        """初始化 UI"""
        self.setStyleSheet("""
            QDialog { background-color: #1E1E1E; }
            QLabel { color: #E5E1E7; background: transparent; }
            QLabel#title { font-size: 16px; font-weight: bold; color: #FFFFFF; }
            QLabel#desc { color: #CBC4D2; font-size: 13px; }
            QPushButton {
                background-color: #1E2530; color: #E5E1E7;
                border: 1px solid #494551; border-radius: 20px;
                padding: 8px 20px; font-size: 13px;
            }
            QPushButton:hover { background-color: #253650; border-color: #0B65D8; }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(12)

        # 标题栏
        header = QHBoxLayout()
        title = QLabel("请完成身份验证")
        title.setObjectName("title")
        header.addWidget(title)
        header.addStretch()
        layout.addLayout(header)

        # 说明
        desc = QLabel(
            "由于登录尝试次数过多，系统要求您完成身份验证后才能继续。"
            "请在下方页面中完成验证，验证完成后窗口会自动关闭。"
        )
        desc.setObjectName("desc")
        desc.setWordWrap(True)
        layout.addWidget(desc)

        # WebView - 桌面端渲染
        self.webview = QWebEngineView()

        # 配置 WebView - 使用桌面 UA
        self.webview.page().profile().setHttpUserAgent(DESKTOP_USER_AGENT)
        settings = self.webview.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.WebGLEnabled, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.AutoLoadImages, True)

        # 注入脚本监听验证完成
        self._inject_verification_script()

        # 监听页面加载
        self.webview.page().loadFinished.connect(self._on_page_load_finished)

        # 加载验证页（与 Android 版相同 URL，桌面 UA 会自动适配布局）
        verification_url = (
            "https://pass.changyan.com/login?"
            "nextpage=aHR0cHM6Ly93d3cuZXRzMTAwLmNvbS9sb2dpbkNoZWNrLmh0bWw%3D&"
            "customConfig=e2hpZGRlbl9tb2R1bGU6ICJoZWFkZXIsdGFpbCxsb2dpbkJ5VmVyaWZ5Q29kZSxyZWdpc3Rlcixsb2dpbkJ5VGhpcmRMb2dpbiIscHJvZHVjdF9hcHBrZXk6InFpbmdkYW9fZXRzIiwibmVlZFRpY2tldCI6InRydWUiLCJsb2dpbl9ub3RBdXRvIjoidHJ1ZSJ9&"
            "from=ew&"
            "appId=pass6port18"
        )

        self.webview.load(QUrl(verification_url))
        layout.addWidget(self.webview, 1)

        # 底部按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.reject)
        self.close_btn.setMinimumWidth(100)
        btn_layout.addWidget(self.close_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

        # 定时器：轮询检查验证数据
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self._check_verification)
        self.check_timer.start(500)

    def _inject_verification_script(self):
        """注入验证脚本 - 拦截 checkLogin 响应"""
        script_code = """
        (function() {
            if (window.__feEtsVerificationInstalled) return;
            window.__feEtsVerificationInstalled = true;
            window.__feEtsVerificationData = null;

            function tryInstallCapture() {
                if (window.__feEtsVerificationCaptureInstalled) return;
                if (window.$) {
                    window.__feEtsVerificationCaptureInstalled = true;
                    $(document).ajaxComplete(function(event, xhr, settings) {
                        if (!settings || !settings.url) return;
                        if (settings.url.indexOf('/login/checkLogin') === -1) return;
                        captureCheckLoginResponse(xhr.responseText);
                    });
                }
                if (window.fetch && !window.__feEtsVerificationFetchInstalled) {
                    window.__feEtsVerificationFetchInstalled = true;
                    var originalFetch = window.fetch;
                    window.fetch = function(...args) {
                        return originalFetch.apply(this, args).then(function(response) {
                            var url = args[0];
                            if (typeof url === 'string' && url.indexOf('/login/checkLogin') !== -1) {
                                var cloned = response.clone();
                                cloned.text().then(function(text) {
                                    captureCheckLoginResponse(text);
                                });
                            }
                            return response;
                        });
                    };
                }
            }

            function captureCheckLoginResponse(text) {
                try {
                    var data = JSON.parse(text || '{}');
                    if (data.Code !== 0 || !data.Data) return;
                    var dataObj = data.Data;
                    if (typeof dataObj === 'string') {
                        dataObj = JSON.parse(dataObj);
                    }
                    if (dataObj.uid && dataObj.captchaResult) {
                        window.__feEtsVerificationData = {
                            uid: dataObj.uid,
                            captchaResult: dataObj.captchaResult
                        };
                        console.log('验证成功，已保存凭证');
                    }
                } catch (e) {
                    console.error('checkLogin 解析失败:', e);
                }
            }

            tryInstallCapture();
            var installTimer = window.setInterval(function() {
                tryInstallCapture();
                if (window.__feEtsVerificationCaptureInstalled) {
                    window.clearInterval(installTimer);
                }
            }, 500);
        })();
        """

        script = QWebEngineScript()
        script.setSourceCode(script_code)
        script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentReady)
        script.setRunsOnSubFrames(True)
        self.webview.page().scripts().insert(script)

    def _on_page_load_finished(self, success):
        """页面加载完成"""
        if success:
            logger.debug("验证页面加载成功")

    def _check_verification(self):
        """定时检查验证数据"""
        self.webview.page().runJavaScript(
            "JSON.stringify(window.__feEtsVerificationData)",
            lambda result: self._process_verification_result(result)
        )

    def _process_verification_result(self, result):
        """处理验证结果"""
        if result and result != "null":
            try:
                self.verification_data = json.loads(result)
                if self.verification_data and self.verification_data.get("uid"):
                    logger.info(f"验证成功！uid={self.verification_data.get('uid', '')[:8]}...")
                    self.check_timer.stop()
                    self.accept()
            except Exception as e:
                logger.error(f"解析验证数据失败: {e}")

    def get_verification_data(self):
        """获取验证数据"""
        return self.verification_data