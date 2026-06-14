"""
认证管理器
负责机器码生成、登录状态持久化
"""

import hashlib
import json
import os
import random
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class AuthManager:
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            # 使用项目目录下的 config 文件夹
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            config_dir = os.path.join(project_root, "config")
        
        self.config_dir = config_dir
        self.config_file = os.path.join(config_dir, "config.json")
        self._ensure_config_dir()

    def _ensure_config_dir(self):
        """确保配置目录存在"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"加载配置失败: {e}")
        return {}

    def _save_config(self, config: Dict[str, Any]):
        """保存配置"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存配置失败: {e}")

    def get_device_code(self) -> str:
        """获取机器码，不存在则生成"""
        config = self._load_config()
        
        if "device_code" in config:
            return config["device_code"]

        # 首次生成
        device_info = self._generate_random_hex(16)
        mac_address = self._generate_random_hex(16)
        
        data_md5 = self._md5_substring(device_info, 8, 24)
        mac_md5 = self._md5_substring(mac_address, 8, 24)
        device_code = f"{data_md5}|{mac_md5}"
        
        config["device_code"] = device_code
        self._save_config(config)
        
        logger.info(f"生成机器码: {device_code[:8]}...")
        return device_code

    @staticmethod
    def _generate_random_hex(length: int) -> str:
        """生成随机十六进制字符串"""
        chars = "0123456789ABCDEF"
        return "".join(random.choice(chars) for _ in range(length))

    @staticmethod
    def _md5_substring(input_str: str, start: int, end: int) -> str:
        """MD5 哈希并截取子串"""
        md5_hash = hashlib.md5(input_str.encode("utf-8")).hexdigest()
        return md5_hash[start:end]

    def save_login_info(self, phone: str, token: str, parent_account_id: str, password: Optional[str] = None):
        """保存登录信息"""
        config = self._load_config()
        config.update({
            "phone": phone,
            "token": token,
            "parent_account_id": parent_account_id,
            "is_logged_in": True
        })
        if password:
            config["password"] = password
        
        self._save_config(config)
        logger.info(f"保存登录信息: {phone}")

    def get_login_info(self) -> Optional[Dict[str, Any]]:
        """获取登录信息"""
        config = self._load_config()
        if not config.get("is_logged_in"):
            return None
        
        return {
            "phone": config.get("phone"),
            "token": config.get("token"),
            "parent_account_id": config.get("parent_account_id"),
            "password": config.get("password")
        }

    def is_logged_in(self) -> bool:
        """检查是否已登录"""
        config = self._load_config()
        return bool(config.get("is_logged_in") and config.get("token"))

    def logout(self):
        """登出（保留机器码）"""
        config = self._load_config()
        device_code = config.get("device_code")
        
        new_config = {"device_code": device_code} if device_code else {}
        self._save_config(new_config)
        logger.info("已登出")

    def clear_all(self):
        """清除所有数据"""
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        logger.info("已清除所有数据")
