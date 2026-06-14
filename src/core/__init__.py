"""
核心模块
"""

from core.api_client import (
    ETS100ApiClient,
    LoginResponse,
    HomeworkInfo,
    HomeworkContent,
    HomeworkListResponse,
    EcardAccount
)
from core.zip_utils import ZipPasswordGenerator
from core.answer_parser import AnswerParser
from core.auth_manager import AuthManager

__all__ = [
    "ETS100ApiClient",
    "LoginResponse",
    "HomeworkInfo",
    "HomeworkContent",
    "HomeworkListResponse",
    "EcardAccount",
    "ZipPasswordGenerator",
    "AnswerParser",
    "AuthManager"
]
