"""
项目拆解Agent
将C语言项目拆解为可执行的任务树，支持团队协作
"""
from typing import Any, Dict, List, Optional
from .base import BaseAgent
from ..services.llm_factory import BaseLLM, LLMFactory
from ..core.safety import SafetyGuard


class ProjectDecomposerAgent(BaseAgent):
    """项目拆解Agent"""

    # 内置经典C语言项目库
    PROJECT_LIBRARY = {
        "hello_world": {
            "name": "Hello World 程序",
            "difficulty": 1,
            "description": "入门级程序，输出 Hello World",
            "modules": ["main函数", "输出语句"],
            "knowledge_points": ["printf函数", "main函数", "基本语法"],
        },
        "temperature_converter": {
            "name": "温度转换器",
            "difficulty": 1,
            "description": "实现摄氏度与华氏度互相转换",
            "modules": ["输入处理", "转换公式", "结果输出", "循环菜单"],
            "knowledge_points": ["scanf函数", "printf函数", "条件语句", "循环语句", "算术运算"],
        },
        "calculator": {
            "name": "简易计算器",
            "difficulty": 2,
            "description": "实现加减乘除运算",
            "modules": ["输入处理", "运算逻辑", "结果输出", "错误处理"],
            "knowledge_points": ["scanf函数", "条件语句", "算术运算", "数据类型"],
        },
        "guess_number": {
            "name": "猜数字游戏",
            "difficulty": 2,
            "description": "随机生成数字，玩家猜测直到猜中",
            "modules": ["随机数生成", "输入比较", "次数统计", "难度选择"],
            "knowledge_points": ["rand函数", "循环语句", "条件判断", "输入验证"],
        },
        "student_management": {
            "name": "学生成绩管理系统",
            "difficulty": 3,
            "description": "管理学生成绩的增删改查系统",
            "modules": ["数据结构定义", "文件存储", "增删改查功能", "排序统计", "界面菜单"],
            "knowledge_points": ["结构体", "文件操作", "数组", "循环", "函数"],
        },
        "address_book": {
            "name": "通讯录管理系统",
            "difficulty": 3,
            "description": "联系人信息的增删改查与排序",
            "modules": ["联系人结构体", "链表存储", "增删改查", "按姓名排序", "文件读写"],
            "knowledge_points": ["结构体", "链表", "字符串处理", "文件操作", "排序算法"],
        },
        "snake_game": {
            "name": "贪吃蛇游戏",
            "difficulty": 4,
            "description": "经典贪吃蛇游戏",
            "modules": ["游戏界面", "蛇的移动", "食物生成", "碰撞检测", "分数系统"],
            "knowledge_points": ["二维数组", "指针", "链表", "键盘输入处理", "循环"],
        },
        "library_system": {
            "name": "图书管理系统",
            "difficulty": 4,
            "description": "图书借阅管理系统",
            "modules": ["图书数据结构", "用户管理", "借阅记录", "查询功能", "文件持久化"],
            "knowledge_points": ["结构体", "链表", "文件操作", "动态内存分配"],
        },
        "file_compressor": {
            "name": "简易文件压缩工具",
            "difficulty": 5,
            "description": "基于哈夫曼编码实现文件压缩与解压",
            "modules": ["频率统计", "哈夫曼树构建", "编码表生成", "压缩写入", "解压读取"],
            "knowledge_points": ["哈夫曼树", "位运算", "文件二进制读写", "递归", "动态内存分配"],
        },
        "chat_room": {
            "name": "简易聊天室",
            "difficulty": 5,
            "description": "基于Socket的聊天程序",
            "modules": ["Socket通信", "消息处理", "用户管理", "界面显示"],
            "knowledge_points": ["Socket编程", "多线程", "网络协议", "字符串处理"],
        },
    }

    def __init__(self, llm: Optional[BaseLLM] = None):
        super().__init__(
            agent_id="project_decomposer",
            agent_name="项目拆解师",
            description="将C语言项目拆解为可执行的任务树，支持团队协作"
        )
        self.llm = llm or LLMFactory.get_default_llm()

    def get_system_prompt(self) -> str:
        return (
            "你是一位资深的软件项目经理，专门负责将C语言项目拆解为可执行的任务。\n"
            "你的核心能力是：\n"
            "1. 将复杂项目拆解为清晰的模块和子任务\n"
            "2. 分析任务之间的依赖关系\n"
            "3. 估算每个任务的难度和耗时\n"
            "4. 根据团队规模合理分配任务\n\n"
            "重要规则：\n"
            "- 任务拆解要具体到可执行的程度\n"
            "- 考虑任务之间的依赖关系\n"
            "- 根据团队人数合理分配工作量\n"
            "- 为每个任务明确所需的知识点\n"
        )

    async def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        context:
        {
            "task": "decompose" | "get_project_info" | "estimate_workload",
            "project_id": "calculator",  # 或自定义项目名称
            "project_name": "自定义项目名称",
            "team_size": 3,
            "team_level": "beginner" | "intermediate" | "advanced",
            "custom_requirements": "可选：特殊需求描述"
        }
        """
        self.status = "running"
        task = context.get("task", "decompose")

        try:
            if task == "decompose":
                result = await self._decompose_project(context)
            elif task == "get_project_info":
                result = await self._get_project_info(context)
            elif task == "estimate_workload":
                result = await self._estimate_workload(context)
            elif task == "list_projects":
                result = self._list_projects()
            else:
                result = {"status": "failed", "error": f"Unknown task: {task}"}

            self.status = "completed"
            return result
        except Exception as e:
            self.status = "failed"
            self.logger.error(f"ProjectDecomposerAgent error: {e}")
            return {"status": "failed", "error": str(e)}

    def _list_projects(self) -> Dict[str, Any]:
        """列出内置项目库"""
        projects = []
        for proj_id, proj_info in self.PROJECT_LIBRARY.items():
            projects.append({
                "id": proj_id,
                "name": proj_info["name"],
                "difficulty": proj_info["difficulty"],
                "description": proj_info["description"],
            })
        return {
            "status": "success",
            "task": "list_projects",
            "projects": projects,
        }

    async def _get_project_info(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """获取项目信息"""
        project_id = context.get("project_id", "")
        project_name = context.get("project_name", "")

        # 从内置库查找
        if project_id in self.PROJECT_LIBRARY:
            proj = self.PROJECT_LIBRARY[project_id]
            return {
                "status": "success",
                "task": "get_project_info",
                "project": {
                    "id": project_id,
                    **proj,
                },
            }

        # 自定义项目，使用LLM分析
        if project_name:
            prompt = (
                f"请分析以下C语言项目：{project_name}\n\n"
                "返回 JSON 格式：\n"
                "{\n"
                '  "name": "项目名称",\n'
                '  "difficulty": 1-5,\n'
                '  "description": "项目描述",\n'
                '  "modules": ["模块1", "模块2", ...],\n'
                '  "knowledge_points": ["知识点1", "知识点2", ...]\n'
                "}"
            )

            prompt = SafetyGuard.sanitize_prompt(prompt)
            messages = [
                {"role": "system", "content": self.get_system_prompt()},
                {"role": "user", "content": prompt},
            ]

            data = await self.llm.generate_json(messages, temperature=0.3, max_tokens=4096)
            return {
                "status": "success",
                "task": "get_project_info",
                "project": data,
            }

        return {"status": "failed", "error": "请提供 project_id 或 project_name"}

    async def _decompose_project(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """拆解项目为任务树"""
        project_id = context.get("project_id", "")
        project_name = context.get("project_name", "")
        team_size = context.get("team_size", 3)
        team_level = context.get("team_level", "beginner")
        custom_requirements = context.get("custom_requirements", "")

        # 获取项目信息
        project_info = None
        if project_id in self.PROJECT_LIBRARY:
            project_info = self.PROJECT_LIBRARY[project_id]
            project_name = project_info["name"]

        prompt = (
            f"请将以下C语言项目拆解为详细的任务树：\n\n"
            f"项目名称：{project_name}\n"
        )

        if project_info:
            prompt += (
                f"项目描述：{project_info['description']}\n"
                f"主要模块：{', '.join(project_info['modules'])}\n"
                f"涉及知识点：{', '.join(project_info['knowledge_points'])}\n"
            )

        prompt += (
            f"团队人数：{team_size}\n"
            f"团队水平：{team_level}\n"
        )

        if custom_requirements:
            prompt += f"特殊需求：{custom_requirements}\n"

        prompt += (
            "\n请生成详细的任务树，返回 JSON 格式：\n"
            "{\n"
            '  "project_name": "项目名称",\n'
            '  "total_estimated_hours": 10,\n'
            '  "modules": [\n'
            "    {\n"
            '      "id": "module_1",\n'
            '      "name": "模块名称",\n'
            '      "description": "模块描述",\n'
            '      "tasks": [\n'
            "        {\n"
            '          "id": "task_1_1",\n'
            '          "name": "任务名称",\n'
            '          "description": "任务描述",\n'
            '          "difficulty": 1-5,\n'
            '          "estimated_hours": 2,\n'
            '          "knowledge_points": ["知识点1"],\n'
            '          "dependencies": ["task_id_依赖的任务"],\n'
            '          "deliverables": ["交付物1"],\n'
            '          "test_cases": ["测试用例1"]\n'
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ],\n"
            '  "suggested_team_assignments": [\n'
            "    {\n"
            '      "role": "角色名称",\n'
            '      "responsibilities": ["职责1"],\n'
            '      "tasks": ["task_id"]\n'
            "    }\n"
            "  ],\n"
            '  "milestones": [\n'
            "    {\n"
            '      "name": "里程碑名称",\n'
            '      "tasks": ["task_id"],\n'
            '      "deadline_day": 3\n'
            "    }\n"
            "  ]\n"
            "}"
        )

        prompt = SafetyGuard.sanitize_prompt(prompt)
        messages = [
            {"role": "system", "content": self.get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        # 使用更大的 max_tokens 确保完整 JSON 输出
        data = await self.llm.generate_json(messages, temperature=0.4, max_tokens=4096)

        # 如果解析失败，尝试直接解析 raw_text
        if isinstance(data, dict) and data.get("status") == "error" and data.get("raw_text"):
            from ..services.llm_factory import BaseLLM
            parsed = BaseLLM._try_parse_json(data["raw_text"])
            if parsed:
                data = parsed

        # 确保 decomposition 结构完整
        if not isinstance(data, dict):
            data = {}

        # 自动计算 total_estimated_hours（如果 LLM 未返回）
        modules = data.get("modules", [])
        if modules and not data.get("total_estimated_hours"):
            total_hours = sum(
                task.get("estimated_hours", 0)
                for module in modules
                for task in module.get("tasks", [])
            )
            data["total_estimated_hours"] = total_hours or 10

        # 自动计算 milestones（如果 LLM 未返回）
        if modules and not data.get("milestones"):
            milestones = []
            all_tasks = []
            for module in modules:
                for task in module.get("tasks", []):
                    all_tasks.append(task)
            # 按任务数量分成 3 个阶段
            chunk_size = max(1, len(all_tasks) // 3)
            for i in range(0, min(len(all_tasks), 3)):
                start = i * chunk_size
                end = start + chunk_size if i < 2 else len(all_tasks)
                milestones.append({
                    "name": f"里程碑 {i + 1}",
                    "tasks": [t.get("id", f"task_{i}") for t in all_tasks[start:end]],
                    "deadline_day": (i + 1) * 3,
                })
            data["milestones"] = milestones

        # 确保 project_name 存在
        if not data.get("project_name"):
            data["project_name"] = project_name

        return {
            "status": "success",
            "task": "decompose",
            "decomposition": data,
        }

    async def _estimate_workload(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """估算工作量"""
        project_id = context.get("project_id", "")
        team_size = context.get("team_size", 3)
        team_level = context.get("team_level", "beginner")

        if project_id not in self.PROJECT_LIBRARY:
            return {"status": "failed", "error": "未知项目ID"}

        proj = self.PROJECT_LIBRARY[project_id]
        difficulty = proj["difficulty"]

        # 基础估算
        base_hours = {
            1: 2,
            2: 6,
            3: 15,
            4: 30,
            5: 50,
        }

        # 水平系数
        level_factor = {
            "beginner": 1.5,
            "intermediate": 1.0,
            "advanced": 0.7,
        }

        # 团队效率系数（人数增加效率递减）
        team_efficiency = min(team_size * 0.8, 3) / team_size if team_size > 0 else 1

        total_hours = base_hours.get(difficulty, 10) * level_factor.get(team_level, 1.0)
        per_person_hours = total_hours / team_size if team_size > 0 else total_hours
        adjusted_hours = per_person_hours / team_efficiency

        return {
            "status": "success",
            "task": "estimate_workload",
            "project_name": proj["name"],
            "difficulty": difficulty,
            "team_size": team_size,
            "team_level": team_level,
            "estimation": {
                "total_base_hours": total_hours,
                "per_person_hours": round(per_person_hours, 1),
                "adjusted_hours_per_person": round(adjusted_hours, 1),
                "estimated_days": round(adjusted_hours / 4, 1),  # 假设每天4小时有效工作
                "suggested_duration_days": round(adjusted_hours / 4) + 2,  # 加2天缓冲
            },
        }
