"""
ETS100 API 客户端
负责所有网络请求、签名、登录和资源下载
"""

import base64
import hashlib
import json
import time
import logging
from typing import Dict, Any, Optional, List
import requests

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ETS100ApiClient:
    API_BASE_URL = "https://api.ets100.com"
    CDN_BASE_URL = "https://cdn.subject.ets100.com"
    PID = "grlx"
    SECRET_KEY = "555ffbe95ccf4e9535a110170b445ab8"
    TIMEOUT = 30

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "libcurl-agent/1.0",
            "Accept": "*/*"
        })

    @staticmethod
    def _compact_json(data: Dict[str, Any]) -> str:
        """紧凑 JSON 序列化"""
        return json.dumps(data, ensure_ascii=False, separators=(",", ":"))

    @staticmethod
    def _md5_hex(text: str) -> str:
        """MD5 哈希"""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def _generate_sign(self, timestamp: int, body_base64: str) -> str:
        """生成签名"""
        sign_str = f"{self.PID}{timestamp}{body_base64}{self.SECRET_KEY}"
        return self._md5_hex(sign_str)

    def _post_request(self, endpoint: str, body_data: Dict[str, Any]) -> Dict[str, Any]:
        """发送 POST 请求"""
        timestamp = int(time.time())
        
        # 构建 body_data 数组
        body_array = [body_data]
        body_json = self._compact_json(body_array)
        body_base64 = base64.b64encode(body_json.encode("utf-8")).decode("ascii")
        
        # 生成签名
        sign = self._generate_sign(timestamp, body_base64)
        
        # 构建完整请求
        head = {
            "version": "1.0",
            "sign": sign,
            "pid": self.PID,
            "time": timestamp
        }
        
        request_json = self._compact_json({
            "body": body_base64,
            "head": head
        })
        
        logger.debug(f"请求 {endpoint}: {request_json}")
        
        url = f"{self.API_BASE_URL}{endpoint}"
        response = self.session.post(
            url,
            data=request_json.encode("utf-8"),
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=self.TIMEOUT
        )
        
        response.raise_for_status()
        
        # 解析响应
        resp_data = response.json()
        logger.debug(f"响应: {resp_data}")
        
        # 处理数组响应
        if isinstance(resp_data, list) and len(resp_data) > 0:
            return resp_data[0]
        return resp_data

    def login(self, phone: str, password: str, device_code: str) -> Dict[str, Any]:
        """登录"""
        body_data = {
            "r": "user/login",
            "params": {
                "sn": "test",
                "phone": phone,
                "password": password,
                "device_code": device_code,
                "device_name": "DESKTOP",
                "version": "3",
                "local_ip": "127.0.0.1",
                "system": "4",
                "global_client_version": "5.4.5",
                "sign_response": 1
            }
        }
        
        return self._post_request("/user/login", body_data)

    def bind_device(self, phone: str, password: str, device_code: str) -> Dict[str, Any]:
        """设备绑定"""
        body_data = {
            "r": "user/rebind-code",
            "params": {
                "sn": "test",
                "phone": phone,
                "email": "",
                "password": password,
                "code": "0",
                "version": "2",
                "device_name": "1337",
                "device_code": device_code,
                "local_ip": "127.0.0.1",
                "system": "4",
                "global_client_version": "5.4.5",
                "sign_response": 1
            }
        }
        
        return self._post_request("/user/rebind-code", body_data)

    def login_with_verification(
        self, uid: str, captcha_result: str, device_code: str
    ) -> Dict[str, Any]:
        """使用验证凭证登录（畅言网页验证后的登录）"""
        body_data = {
            "r": "user/login-zt",
            "params": {
                "sn": "test",
                "login": uid,
                "user_id": uid,
                "suc_user_token": captcha_result,
                "device_code": device_code,
                "device_name": "Android",
                "suc_device_name": "Other",
                "os_type": "android",
                "system": "4",
                "global_client_version": "5.4.5",
                "sign_response": 1,
                "version": "3"
            }
        }
        
        return self._post_request("/user/login-zt", body_data)

    def get_ecard_list(self, token: str) -> Dict[str, Any]:
        """获取父账户列表"""
        body_data = {
            "r": "m/ecard/list",
            "params": {
                "sn": "test",
                "token": token,
                "version": "3",
                "system": "4",
                "global_client_version": "5.4.5",
                "sign_response": 1
            }
        }
        
        return self._post_request("/m/ecard/list", body_data)

    def get_homework_list(self, token: str, parent_account_id: str, status: str = "1") -> Dict[str, Any]:
        """获取作业列表"""
        body_data = {
            "r": "g/homework/list",
            "params": {
                "sn": "test",
                "token": token,
                "parent_account_id": parent_account_id,
                "limit": "0",
                "status": status,
                "offset": "0",
                "max_end_time": "",
                "max_homework_id": "",
                "min_end_time": "",
                "min_homework_id": "",
                "get_to_do_count": 1,
                "show_old_homework": 1,
                "parent_homework_id": "",
                "get_all_count": 1,
                "check_pass": 1,
                "get_to_overtime_count": 1,
                "version": "3",
                "system": "4",
                "global_client_version": "5.4.5",
                "sign_response": 1
            }
        }
        
        return self._post_request("/g/homework/list", body_data)

    def download_file(self, url: str, dest_path: str, progress_callback=None) -> bool:
        """下载文件"""
        try:
            logger.info(f"开始下载: {url}")
            
            # 处理 SSL 证书问题
            if url.startswith("https://cdn.subject.ets100.com"):
                import urllib3
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            
            response = self.session.get(
                url,
                stream=True,
                verify=False,  # 跳过证书验证
                timeout=self.TIMEOUT
            )
            response.raise_for_status()
            
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0
            
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded, total_size)
            
            logger.info(f"下载完成: {dest_path}")
            return True
            
        except Exception as e:
            logger.error(f"下载失败: {e}")
            return False


# 数据模型
class LoginResponse:
    def __init__(self, data: Dict[str, Any]):
        self.token = data.get("body", {}).get("token", "")
        self.code = data.get("code", -1)
        self.msg = data.get("msg", "")


class HomeworkContent:
    def __init__(self, data: Dict[str, Any]):
        self.group_name = data.get("group_name", "")
        self.url = data.get("url", "")


class HomeworkInfo:
    def __init__(self, data: Dict[str, Any]):
        self.id = data.get("id", "")
        self.name = data.get("name", "未知作业")
        self.contents = []
        
        struct = data.get("struct", {})
        contents_array = struct.get("contents", [])
        for content_data in contents_array:
            self.contents.append(HomeworkContent(content_data))


class HomeworkListResponse:
    def __init__(self, data: Dict[str, Any]):
        self.base_url = data.get("body", {}).get("base_url", ETS100ApiClient.CDN_BASE_URL)
        self.homeworks = []
        
        data_array = data.get("body", {}).get("data", [])
        for hw_data in data_array:
            self.homeworks.append(HomeworkInfo(hw_data))


class EcardAccount:
    def __init__(self, key: str, data: Dict[str, Any]):
        self.key = key
        self.id = data.get("id", "")
        self.parent_id = data.get("parent_id", "")
        self.user_account_id = data.get("user_account_id", "")
        self.name = data.get("name", "")
        self.grade = data.get("grade", "")
        self.status = data.get("status", "")
        self.mobile_status = data.get("mobile_status", "")
        self.out_of_date = data.get("out_of_date", "")
        self.class_id = data.get("class_id", "")
        self.class_name = data.get("class_name", "")
        self.machine_code_status = data.get("machine_code_status", "")

    @property
    def is_valid(self) -> bool:
        return (self.status == "0" and 
                self.out_of_date == "0" and 
                self.class_id and 
                self.mobile_status == "1")
