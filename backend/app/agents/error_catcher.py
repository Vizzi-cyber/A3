"""
错误捕捉Agent
专门抓取用户代码中的语法错误、逻辑错误和思维误区
"""
from typing import Any, Dict, List, Optional
from .base import BaseAgent
from ..services.llm_factory import BaseLLM, LLMFactory
from ..core.safety import SafetyGuard


class ErrorCatcherAgent(BaseAgent):
    """错误捕捉Agent"""

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(
            agent_id="error_catcher",
            agent_name="错误捕捉师",
            description="专门抓取代码中的语法错误、逻辑错误和思维误区"
        )
        self.llm = llm or LLMFactory.get_default_llm()

    def get_system_prompt(self) -> str:
        return (
            "你是一位资深的C语言编程教师，专门擅长分析学生代码中的错误。\n"
            "你的核心能力是：\n"
            "1. 识别语法错误（如缺少分号、括号不匹配等）\n"
            "2. 发现逻辑错误（如循环条件错误、边界处理不当等）\n"
            "3. 诊断思维误区（如赋值与判断混淆、指针概念不清等）\n\n"
            "重要规则：\n"
            "- 不要输出思考过程，直接给出分析结果\n"
            "- 对于思维误区，要解释为什么学生会犯这种错误\n"
            "- 给出具体的修复建议，而不仅仅是指出错误\n"
        )

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        context:
        {
            "task": "catch_error" | "analyze_misconception" | "validate_code",
            "code": "int main() { ... }",
            "language": "C",
            "student_level": "beginner" | "intermediate" | "advanced",
            "error_output": "optional: compiler error message"
        }
        """
        self.status = "running"
        task = context.get("task", "catch_error")
        code = context.get("code", "")
        language = context.get("language", "C")

        # 输入安全检查
        safety = SafetyGuard.check_input(code)
        if not safety["safe"]:
            return {"status": "blocked", "reason": safety["message"]}

        try:
            if task == "catch_error":
                result = await self._catch_errors(code, language, context)
            elif task == "analyze_misconception":
                result = await self._analyze_misconception(code, language, context)
            elif task == "validate_code":
                result = await self._validate_code(code, language, context)
            else:
                result = {"status": "failed", "error": f"Unknown task: {task}"}

            self.status = "completed"
            return result
        except Exception as e:
            self.status = "failed"
            self.logger.error(f"ErrorCatcherAgent error: {e}")
            return {"status": "failed", "error": str(e)}

    async def _catch_errors(self, code: str, language: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """捕捉代码中的错误"""
        student_level = context.get("student_level", "beginner")
        error_output = context.get("error_output", "")

        prompt = (
            f"请分析以下 {language} 代码中的错误：\n\n"
            f"```{language.lower()}\n{code}\n```\n\n"
        )

        if error_output:
            prompt += f"编译器错误信息：\n```\n{error_output}\n```\n\n"

        prompt += (
            f"学生水平：{student_level}\n\n"
            "请按以下格式分析：\n"
            "1. **语法错误**：列出所有语法错误（如果有）\n"
            "2. **逻辑错误**：列出所有逻辑错误（如果有）\n"
            "3. **思维误区**：识别学生可能存在的思维误区（如果有）\n"
            "4. **修复建议**：给出具体的修复方法\n\n"
            "返回 JSON 格式：\n"
            "{\n"
            '  "syntax_errors": [{"line": 1, "description": "...", "fix": "..."}],\n'
            '  "logic_errors": [{"description": "...", "impact": "...", "fix": "..."}],\n'
            '  "misconceptions": [{"type": "...", "description": "...", "why_student_makes_this_mistake": "...", "correct_concept": "..."}],\n'
            '  "suggestions": ["..."],\n'
            '  "overall_assessment": "..."\n'
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.3)
        return {
            "status": "success",
            "task": "catch_error",
            "analysis": data,
            "code": code,
            "language": language,
        }

    async def _analyze_misconception(self, code: str, language: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """专门分析思维误区"""
        prompt = (
            f"请专门分析以下 {language} 代码中可能存在的思维误区：\n\n"
            f"```{language.lower()}\n{code}\n```\n\n"
            "常见的C语言思维误区包括：\n"
            "- 赋值与判断混淆（如 if(a=1) vs if(a==1)）\n"
            "- 指针与地址混淆\n"
            "- 数组越界思维\n"
            "- 内存管理误区\n"
            "- 循环边界条件错误\n"
            "- 递归终止条件缺失\n\n"
            "请返回 JSON 格式：\n"
            "{\n"
            '  "misconceptions": [\n'
            "    {\n"
            '      "type": "概念混淆",\n'
            '      "location": "第X行",\n'
            '      "what_student_thought": "学生可能的想法",\n'
            '      "correct_concept": "正确的概念",\n'
            '      "why_this_happens": "为什么会产生这种误解",\n'
            '      "how_to_fix": "如何纠正"\n'
            "    }\n"
            "  ],\n"
            '  "learning_suggestions": ["..."]\n'
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.4)
        return {
            "status": "success",
            "task": "analyze_misconception",
            "misconceptions": data.get("misconceptions", []),
            "learning_suggestions": data.get("learning_suggestions", []),
        }

    async def _validate_code(self, code: str, language: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """验证代码正确性"""
        prompt = (
            f"请验证以下 {language} 代码是否正确：\n\n"
            f"```{language.lower()}\n{code}\n```\n\n"
            "请检查：\n"
            "1. 语法是否正确\n"
            "2. 逻辑是否合理\n"
            "3. 是否有潜在的运行时错误\n"
            "4. 代码风格是否良好\n\n"
            "返回 JSON 格式：\n"
            "{\n"
            '  "is_correct": true/false,\n'
            '  "issues": ["..."],\n'
            '  "improvements": ["..."],\n'
            '  "score": 0-100\n'
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.3)
        return {
            "status": "success",
            "task": "validate_code",
            "validation": data,
        }
