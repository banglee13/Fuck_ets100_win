"""
ETS100 content.json 答案解析引擎
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)


class AnswerParser:
    """通用答案解析器"""

    @staticmethod
    def clean_text(text: str, remove_ets_th: bool = True) -> str:
        """清洗文本"""
        if not text:
            return ""

        cleaned = text
        if remove_ets_th:
            cleaned = re.sub(r"ets_th\d+\s*", "", cleaned)

        # 处理 HTML 标签
        cleaned = re.sub(r"</p>\s*<p[^>]*>", "\n", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<br\s*/?>|</br>|</p>|<p[^>]*>", "\n", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"<[^>]+>", "", cleaned)

        # 移除零宽字符
        cleaned = cleaned.replace("\u200b", "")

        # 整理换行
        lines = [line.strip() for line in cleaned.splitlines()]
        lines = [line for line in lines if line]
        return "\n".join(lines)

    @staticmethod
    def parse_collector_role(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析 collector.role 题型 (听选信息/回答问题/提问)"""
        questions = []
        info = data.get("info", {})
        question_list = info.get("question", [])

        for q_idx, q_data in enumerate(question_list):
            ask = AnswerParser.clean_text(q_data.get("ask", ""))
            std_list = q_data.get("std", [])
            answers = [AnswerParser.clean_text(a.get("value", "")) for a in std_list if a.get("value")]

            questions.append({
                "index": q_idx,
                "question": ask,
                "answers": answers
            })

        return questions

    @staticmethod
    def parse_collector_3q5a(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析 collector.3q5a 题型 (广东高中 3问5答)"""
        questions = []
        info = data.get("info", {})
        question_list = info.get("question", [])

        for q_idx, q_data in enumerate(question_list):
            ask = AnswerParser.clean_text(q_data.get("ask", ""))
            std_list = q_data.get("std", [])
            answers = [AnswerParser.clean_text(a.get("value", "")) for a in std_list if a.get("value")]

            questions.append({
                "index": q_idx,
                "question": ask,
                "answers": answers
            })

        return questions

    @staticmethod
    def parse_collector_choose(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析 collector.choose 题型 (听后选择)"""
        questions = []
        info = data.get("info", {})
        xt_list = info.get("xtlist", [])

        for q_idx, xt in enumerate(xt_list):
            xt_xh = xt.get("xt_xh", str(q_idx + 1))
            xt_nr = AnswerParser.clean_text(xt.get("xt_nr", ""))
            answer = xt.get("answer", "")

            options = []
            xx_list = xt.get("xxlist", [])
            for xx in xx_list:
                xx_mc = xx.get("xx_mc", "")
                xx_nr = AnswerParser.clean_text(xx.get("xx_nr", ""))
                options.append({
                    "label": xx_mc,
                    "text": xx_nr
                })

            questions.append({
                "index": q_idx,
                "number": xt_xh,
                "question": xt_nr,
                "options": options,
                "answer": answer
            })

        return questions

    @staticmethod
    def parse_collector_picture(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析 collector.picture 题型 (信息转述/听后转述)"""
        info = data.get("info", {})
        std_list = info.get("std", [])
        answers = [AnswerParser.clean_text(a.get("value", "")) for a in std_list if a.get("value")]

        topic = AnswerParser.clean_text(info.get("topic", ""))
        original_text = AnswerParser.clean_text(info.get("value", ""))

        return [{
            "index": 0,
            "topic": topic,
            "original_text": original_text,
            "answers": answers
        }]

    @staticmethod
    def parse_collector_fill(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析 collector.fill 题型 (听后记录/填空)"""
        questions = []
        info = data.get("info", {})
        std_list = info.get("std", [])

        for q_idx, std in enumerate(std_list):
            xth = std.get("xth", str(q_idx + 1))
            value = AnswerParser.clean_text(std.get("value", ""))

            questions.append({
                "index": q_idx,
                "number": xth,
                "answer": value
            })

        return questions

    @staticmethod
    def parse_collector_dialogue(data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """解析 collector.dialogue 题型 (回答问题)"""
        questions = []
        info = data.get("info", {})
        question_list = info.get("question", [])

        for q_idx, q_data in enumerate(question_list):
            ask = AnswerParser.clean_text(q_data.get("ask", ""))
            std_list = q_data.get("std", [])
            answers = [AnswerParser.clean_text(a.get("value", "")) for a in std_list if a.get("value")]

            questions.append({
                "index": q_idx,
                "question": ask,
                "answers": answers
            })

        return questions

    @staticmethod
    def parse_content_json(content_json_path: str) -> Optional[Dict[str, Any]]:
        """解析 content.json 文件"""
        try:
            with open(content_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            structure_type = data.get("structure_type", "")
            logger.info(f"解析 content.json, structure_type: {structure_type}")

            result = {
                "structure_type": structure_type,
                "questions": [],
                "type_name": AnswerParser._get_type_name(structure_type)
            }

            if structure_type == "collector.role":
                result["questions"] = AnswerParser.parse_collector_role(data)
            elif structure_type == "collector.3q5a":
                result["questions"] = AnswerParser.parse_collector_3q5a(data)
            elif structure_type == "collector.choose":
                result["questions"] = AnswerParser.parse_collector_choose(data)
            elif structure_type == "collector.picture":
                result["questions"] = AnswerParser.parse_collector_picture(data)
            elif structure_type == "collector.fill":
                result["questions"] = AnswerParser.parse_collector_fill(data)
            elif structure_type == "collector.dialogue":
                result["questions"] = AnswerParser.parse_collector_dialogue(data)
            elif structure_type == "collector.read":
                info = data.get("info", {})
                original_text = AnswerParser.clean_text(info.get("value", ""))
                result["questions"] = [{
                    "index": 0,
                    "type": "read",
                    "original_text": original_text
                }]

            return result

        except Exception as e:
            logger.error(f"解析 content.json 失败: {e}")
            return None

    @staticmethod
    def _get_type_name(structure_type: str) -> str:
        """获取题型名称"""
        type_map = {
            "collector.role": "问答题",
            "collector.3q5a": "3问5答",
            "collector.choose": "选择题",
            "collector.picture": "信息转述",
            "collector.fill": "填空题",
            "collector.dialogue": "对话问答",
            "collector.read": "模仿朗读"
        }
        return type_map.get(structure_type, "未知题型")
