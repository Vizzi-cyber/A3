"""
内容安全过滤与防幻觉机制
- 敏感词过滤
- Prompt 安全加固
- 输出自校验
- 引用溯源检查
"""
import json
import re
from typing import Any, Dict, List, Optional

# 基础敏感词库（示例，生产环境应接入专业内容审核 API）
SENSITIVE_KEYWORDS = [
    "法轮功", "台独", "藏独", "疆独", "赌博", "色情", "暴力", "毒品",
    "自杀", "自残", "恐怖主义", "极端主义", "纳粹", "种族灭绝",
]

# 编译正则
_SENSITIVE_PATTERN = re.compile(
    "|".join(map(re.escape, SENSITIVE_KEYWORDS)),
    re.IGNORECASE,
)


class SafetyGuard:
    """内容安全守卫"""

    @staticmethod
    def check_input(text: str | List[Dict[str, Any]]) -> Dict[str, Any]:
        """检查用户输入是否包含敏感内容（支持纯文本或图文数组）"""
        if isinstance(text, list):
            # 提取图文数组中的所有文本内容进行检查
            texts = [item.get("text", "") for item in text if isinstance(item, dict) and item.get("type") == "text"]
            combined = "\n".join(texts)
        else:
            combined = text or ""
        hits = _SENSITIVE_PATTERN.findall(combined)
        return {
            "safe": len(hits) == 0,
            "hits": hits,
            "message": "输入包含敏感内容，请修改后重试" if hits else "通过",
        }

    @staticmethod
    def check_output(text: str) -> Dict[str, Any]:
        """检查模型输出是否包含敏感内容"""
        hits = _SENSITIVE_PATTERN.findall(text)
        return {
            "safe": len(hits) == 0,
            "hits": hits,
            "message": "输出包含敏感内容，已拦截" if hits else "通过",
        }

    @staticmethod
    def sanitize_prompt(prompt: str, student_age: Optional[int] = None) -> str:
        """
        在 Prompt 末尾追加安全约束
        """
        constraints = [
            "【安全约束】",
            "1. 严禁输出任何违法违规、暴力恐怖、色情低俗、政治敏感内容。",
            "2. 严禁输出可能诱导自残、自杀或危害他人的内容。",
            '3. 对于不确定的事实，请明确说明"我不确定"或"根据现有信息无法确认"。',
            "4. 输出内容必须积极健康，适合学生群体阅读。",
        ]
        if student_age and student_age < 18:
            constraints.append("5. 考虑到受众为未成年人，请使用更温和、鼓励性的表达方式。")
        return prompt + "\n" + "\n".join(constraints)


class HallucinationGuard:
    """防幻觉机制"""

    @staticmethod
    def verify_json_schema(data: Dict[str, Any], required_fields: List[str]) -> Dict[str, Any]:
        """校验 JSON 输出是否包含必要字段"""
        missing = [f for f in required_fields if f not in data]
        return {
            "valid": len(missing) == 0,
            "missing_fields": missing,
            "message": f"缺少必要字段: {missing}" if missing else "结构校验通过",
        }

    @staticmethod
    def verify_code_output(code: str, language: str = "python") -> Dict[str, Any]:
        """对代码输出做基础语法检查（仅 Python 支持编译检查）"""
        if language.lower() == "python":
            try:
                compile(code, "<string>", "exec")
                return {"valid": True, "message": "Python 语法检查通过"}
            except SyntaxError as e:
                return {"valid": False, "message": f"Python 语法错误: {e.msg} (第{e.lineno}行)"}
        return {"valid": True, "message": f"{language} 语法检查暂未实现"}

    @staticmethod
    def verify_citations(text: str, min_citations: int = 0) -> Dict[str, Any]:
        """检查文本中是否包含引用/来源标注"""
        citation_patterns = [
            r"\[\d+\]",
            r"《.*?》",
            r"来源：",
            r"引用",
            r"参考文献",
            r"出自",
        ]
        count = sum(len(re.findall(p, text)) for p in citation_patterns)
        return {
            "has_citations": count >= min_citations,
            "citation_count": count,
            "message": "包含引用标注" if count >= min_citations else "缺少引用标注，请注意事实核查",
        }

    @staticmethod
    def build_fact_check_prompt(original_prompt: str, model_output: str) -> str:
        """构造让模型自我纠错的二次 Prompt"""
        return f"""请对以下输出进行事实核查和自我修正。

原始要求：
{original_prompt}

模型输出：
{model_output}

请检查输出中是否存在与事实不符、前后矛盾、过度推断或编造内容的情况。
如果存在问题，请直接输出修正后的内容；如果没有问题，请原样输出。
只输出最终内容，不要附加解释。
"""

    @classmethod
    async def self_correct(cls, llm, original_prompt: str, model_output: str) -> str:
        """调用 LLM 进行自我修正（预留接口，需传入 llm 实例）"""
        check_prompt = cls.build_fact_check_prompt(original_prompt, model_output)
        messages = [
            {"role": "system", "content": "你是一位严格的事实核查专家。"},
            {"role": "user", "content": check_prompt},
        ]
        corrected = await llm.ainvoke(messages, temperature=0.2)
        return corrected


def combine_guard_results(*results: Dict[str, Any]) -> Dict[str, Any]:
    """合并多个安全检查结果"""
    all_safe = all(r.get("safe", r.get("valid", True)) for r in results)
    messages = [r.get("message", "") for r in results]
    return {
        "safe": all_safe,
        "messages": messages,
        "details": results,
    }
