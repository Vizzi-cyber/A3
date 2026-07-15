"""
思维溯源Agent
不直接讲知识点，反向推导学生为什么错，归类错误模型
"""
from typing import Any, Dict, List, Optional
from .base import BaseAgent
from ..services.llm_factory import BaseLLM, LLMFactory
from ..core.safety import SafetyGuard


class MisconceptionTracerAgent(BaseAgent):
    """思维溯源Agent"""

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(
            agent_id="misconception_tracer",
            agent_name="思维溯源师",
            description="反向推导学生错误原因，归类错误模型，提供针对性纠正"
        )
        self.llm = llm or LLMFactory.get_default_llm()

    def get_system_prompt(self) -> str:
        return (
            "你是一位教育心理学专家，专门研究学生的编程思维误区。\n"
            "你的核心能力是：\n"
            "1. 反向推导学生为什么会犯某种错误\n"
            "2. 归类错误模型（概念混淆型、逻辑缺失型、语法惯性错误、零基础思维盲区）\n"
            "3. 提供针对性的纠正策略\n\n"
            "重要规则：\n"
            "- 不要直接给答案，要分析学生的思维过程\n"
            "- 每种错误都要解释为什么学生会这样想\n"
            "- 给出具体的纠正方法，而不是泛泛而谈\n"
        )

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        context:
        {
            "task": "trace_error" | "classify_misconception" | "generate_correction",
            "code": "学生提交的代码",
            "error_type": "语法错误/逻辑错误/思维误区",
            "error_description": "错误描述",
            "student_history": {...},  # 学生历史错误记录
            "profile": {...}  # 学生画像
        }
        """
        self.status = "running"
        task = context.get("task", "trace_error")

        try:
            if task == "trace_error":
                result = await self._trace_error(context)
            elif task == "classify_misconception":
                result = await self._classify_misconception(context)
            elif task == "generate_correction":
                result = await self._generate_correction(context)
            else:
                result = {"status": "failed", "error": f"Unknown task: {task}"}

            self.status = "completed"
            return result
        except Exception as e:
            self.status = "failed"
            self.logger.error(f"MisconceptionTracerAgent error: {e}")
            return {"status": "failed", "error": str(e)}

    async def _trace_error(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """追溯错误根源"""
        code = context.get("code", "")
        error_type = context.get("error_type", "")
        error_description = context.get("error_description", "")
        student_history = context.get("student_history", {})
        profile = context.get("profile", {})

        prompt = (
            f"学生提交了以下代码：\n\n"
            f"```c\n{code}\n```\n\n"
            f"错误类型：{error_type}\n"
            f"错误描述：{error_description}\n\n"
        )

        if student_history:
            prompt += f"学生历史错误记录：{student_history}\n\n"

        if profile:
            prompt += f"学生画像：{profile}\n\n"

        prompt += (
            "请深入分析：\n"
            "1. **错误表象**：表面上看是什么错误\n"
            "2. **思维过程**：学生写这段代码时可能在想什么\n"
            "3. **根本原因**：为什么会产生这种思维\n"
            "4. **错误归类**：属于哪种错误模型\n"
            "5. **关联错误**：这种思维误区还可能导致哪些其他错误\n\n"
            "返回 JSON 格式：\n"
            "{\n"
            '  "error_surface": "表象描述",\n'
            '  "thinking_process": "学生可能的思维过程",\n'
            '  "root_cause": "根本原因",\n'
            '  "error_model": {\n'
            '    "type": "概念混淆型/逻辑缺失型/语法惯性错误/零基础思维盲区",\n'
            '    "subtype": "具体子类型",\n'
            '    "description": "错误模型描述"\n'
            "  },\n"
            '  "related_errors": ["可能关联的其他错误"],\n'
            '  "severity": "low/medium/high",\n'
            '  "confidence": 0.0-1.0\n'
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.4, max_tokens=4096)
        if data.get("status") == "error":
            return {
                "status": "failed",
                "task": "trace_error",
                "error": data.get("message", "LLM 返回内容无法解析"),
            }
        return {
            "status": "success",
            "task": "trace_error",
            "trace_result": data,
        }

    async def _classify_misconception(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """分类思维误区"""
        code = context.get("code", "")
        error_description = context.get("error_description", "")

        prompt = (
            f"请对以下代码错误进行思维误区分类：\n\n"
            f"```c\n{code}\n```\n\n"
            f"错误描述：{error_description}\n\n"
            "思维误区分类体系：\n"
            "1. **概念混淆型**：对基本概念理解不清\n"
            "   - 赋值与判断混淆\n"
            "   - 指针与地址混淆\n"
            "   - 数组与指针混淆\n"
            "2. **逻辑缺失型**：逻辑推理能力不足\n"
            "   - 循环边界错误\n"
            "   - 条件判断遗漏\n"
            "   - 递归终止条件缺失\n"
            "3. **语法惯性错误**：受其他语言影响\n"
            "   - Java/Python 语法混用\n"
            "   - 忘记分号\n"
            "   - 括号不匹配\n"
            "4. **零基础思维盲区**：完全没有相关概念\n"
            "   - 不理解内存模型\n"
            "   - 不理解指针本质\n"
            "   - 不理解作用域\n\n"
            "返回 JSON 格式：\n"
            "{\n"
            '  "primary_category": "主要分类",\n'
            '  "subcategory": "子分类",\n'
            '  "confidence": 0.0-1.0,\n'
            '  "evidence": ["支持这个分类的证据"],\n'
            '  "alternative_categories": ["其他可能的分类"]\n'
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.3, max_tokens=4096)
        if data.get("status") == "error":
            return {
                "status": "failed",
                "task": "classify_misconception",
                "error": data.get("message", "LLM 返回内容无法解析"),
            }
        return {
            "status": "success",
            "task": "classify_misconception",
            "classification": data,
        }

    async def _generate_correction(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """生成纠正策略"""
        code = context.get("code", "")
        error_type = context.get("error_type", "")
        misconception_type = context.get("misconception_type", "")
        profile = context.get("profile", {})

        prompt = (
            f"学生代码：\n```c\n{code}\n```\n\n"
            f"错误类型：{error_type}\n"
            f"思维误区类型：{misconception_type}\n\n"
        )

        if profile:
            prompt += f"学生画像：{profile}\n\n"

        prompt += (
            "请生成针对性的纠正策略：\n\n"
            "返回 JSON 格式：\n"
            "{\n"
            '  "correction_strategy": {\n'
            '    "approach": "纠正方法",\n'
            '    "steps": ["步骤1", "步骤2"],\n'
            '    "key_points": ["要点1", "要点2"]\n'
            "  },\n"
            '  "socratic_questions": ["问题1", "问题2"],\n'
            '  "comparison_examples": {\n'
            '    "wrong": "错误示例",\n'
            '    "correct": "正确示例",\n'
            '    "explanation": "解释"\n'
            "  },\n"
            '  "practice_suggestions": ["建议1", "建议2"],\n'
            '  "estimated_correction_time": "30"\n'
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        data = await self.llm.generate_json(messages, temperature=0.5, max_tokens=4096)
        if data.get("status") == "error":
            return {
                "status": "failed",
                "task": "generate_correction",
                "error": data.get("message", "LLM 返回内容无法解析"),
            }
        return {
            "status": "success",
            "task": "generate_correction",
            "correction": data,
        }
