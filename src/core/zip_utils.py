"""
ZIP 密码生成和解压工具
"""

import hashlib
import logging
import os
from typing import Optional
import zipfile
import pyzipper

logger = logging.getLogger(__name__)


class ZipPasswordGenerator:
    FOOTER_SIZE = 336
    SEED_START = 16
    SEED_END = 143  # 128 bytes

    @staticmethod
    def generate_password(zip_path: str) -> Optional[str]:
        """从 ZIP 文件生成解压密码"""
        try:
            if not os.path.exists(zip_path):
                logger.error(f"ZIP 文件不存在: {zip_path}")
                return None

            file_size = os.path.getsize(zip_path)
            if file_size < ZipPasswordGenerator.FOOTER_SIZE:
                logger.error(f"ZIP 文件太小: {file_size} bytes")
                return None

            with open(zip_path, "rb") as f:
                f.seek(file_size - ZipPasswordGenerator.FOOTER_SIZE)
                footer = f.read(ZipPasswordGenerator.FOOTER_SIZE)

            return ZipPasswordGenerator.generate_password_from_footer(footer)

        except Exception as e:
            logger.error(f"生成密码失败: {e}")
            return None

    @staticmethod
    def generate_password_from_footer(footer: bytes) -> Optional[str]:
        """从尾部数据生成密码"""
        try:
            # 验证签名
            signature1_valid = footer[0:8] == b"MSTCHINA"
            signature2_valid = footer[144:149] == b"EPLAT"

            if not signature1_valid and not signature2_valid:
                logger.error("无效的 ZIP 文件签名")
                return None

            logger.debug("ZIP 文件签名验证通过")

            # 提取种子数据
            seed = footer[ZipPasswordGenerator.SEED_START : ZipPasswordGenerator.SEED_END + 1]

            # 第一次 MD5
            first_md5 = hashlib.md5(seed).hexdigest().upper()

            # 第二次 MD5 (ASCII 编码)
            second_md5 = hashlib.md5(first_md5.encode("ascii")).hexdigest().upper()

            # 拼接密码
            return first_md5 + second_md5

        except Exception as e:
            logger.error(f"从尾部生成密码失败: {e}")
            return None

    @staticmethod
    def extract_zip(zip_path: str, extract_dir: str, password: Optional[str] = None) -> bool:
        """解压 ZIP 文件"""
        try:
            if not os.path.exists(extract_dir):
                os.makedirs(extract_dir, exist_ok=True)

            if password:
                # 使用 pyzipper 解压加密 ZIP
                with pyzipper.ZipFile(zip_path) as zf:
                    zf.setpassword(password.encode("ascii"))
                    zf.extractall(extract_dir)
            else:
                # 普通解压
                with zipfile.ZipFile(zip_path) as zf:
                    zf.extractall(extract_dir)

            logger.info(f"解压成功: {zip_path} -> {extract_dir}")
            return True

        except Exception as e:
            logger.error(f"解压失败: {e}")
            return False
