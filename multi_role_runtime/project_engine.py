"""
项目引擎：Producer 主导的项目启动与推进流程。

流程：
1. 用户输入一句话方向描述
2. Producer 解析方向，输出完整项目规划（项目定义 + MVP 范围 + 任务拆分 + 里程碑）
3. 自动写入 project-drive 相关文件
4. 按任务优先级逐个发起多角色共识
5. Producer 在每个阶段做收口决策
"""

import json
import threading
import uuid
from datetime import datetime
from pathlib import Path

from .config import load_config
from .llm import LLMClient
from .engine import ConsensusEngine

PRODUCER_SYSTEM_PROMPT = """\
你是一个经验丰富的游戏制作人 / 项目主策划。
你的任务是根据用户给出的一句话方向描述，输出一份完整的项目启动规划。

你必须严格输出中文，并使用以下 JSON 格式返回（不要添加任何其他内容，不要用 markdown 代码块包裹）：

{
  "project_name": "项目名称",
  "theme": "项目主题描述（一段话）",
  "platform": "目标平台",
  "visual_style": "视觉风格描述",
  "core_loop": "核心循环描述（一段话描述玩家的主要行为循环）",
  "mvp_scope": {
    "must_have": ["必做功能1", "必做功能2", "..."],
    "nice_to_have": ["可延后功能1", "..."],
    "not_doing": ["明确不做1", "..."]
  },
  "milestones": [
    {
      "id": "M1",
      "name": "里程碑名称",
      "duration": "预估周期",
      "goal": "里程碑目标",
      "owner": "主责角色"
    }
  ],
  "tasks": [
    {
      "id": "TASK-001",
      "title": "任务标题",
      "description": "任务描述",
      "owner": "主责角色",
      "priority": "P0/P1/P2",
      "acceptance_criteria": ["验收标准1", "验收标准2"],
      "depends_on": [],
      "milestone": "M1"
    }
  ],
  "risks": ["风险1", "风险2"],
  "success_criteria": "项目成功标准描述"
}

要求：
- tasks 至少包含 3-6 个具体可执行任务，按优先级排序
- milestones 至少包含 2-3 个阶段
- 每个 task 的 owner 只能是以下角色之一：producer, systems-economy, web-tech-lead, visual-ui, prototype-qa
- 任务应当从最核心的系统设计开始，逐步到实现、视觉、测试
- MVP 范围要克制，原型验证阶段不要过度扩张
"""


class ProjectEngine:
    """管理项目生命周期：规划 → 任务推进 → 共识 → 收口。"""

    def __init__(self, config=None):
        self.config = config or load_config()
        self.llm = LLMClient(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            model=self.config.model,
        )
        self.consensus_engine = ConsensusEngine(self.config)
        self._lock = threading.Lock()
        self._projects = {}

    def list_projects(self):
        with self._lock:
            return sorted(
                self._projects.values(),
                key=lambda x: x["created_at"],
                reverse=True,
            )

    def get_project(self, project_id):
        with self._lock:
            return self._projects.get(project_id)

    def create_project(self, direction):
        """
        从一句话方向描述启动一个新项目。
        direction: 如 "火锅店运营的项目，web端显示，界面较为美观，水墨画风"
        """
        project_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        project_state = {
            "project_id": project_id,
            "direction": direction,
            "status": "planning",  # planning -> planned -> executing -> completed / failed
            "created_at": datetime.utcnow().isoformat() + "Z",
            "finished_at": None,
            "plan": None,
            "active_task": None,
            "completed_tasks": [],
            "consensus_runs": [],
            "current_phase": "producer_planning",
            "error": None,
            "logs": [],
        }

        with self._lock:
            self._projects[project_id] = project_state

        t = threading.Thread(target=self._run_project, args=(project_id,))
        t.daemon = True
        t.start()

        return project_state

    def _log(self, state, message):
        entry = {
            "time": datetime.utcnow().isoformat() + "Z",
            "message": message,
        }
        state["logs"].append(entry)

    def _run_project(self, project_id):
        state = self.get_project(project_id)
        if not state:
            return

        project_dir = self.config.output_dir / "projects" / project_id
        project_dir.mkdir(parents=True, exist_ok=True)

        try:
            # ═══════════════════════════════════════
            # Phase 1: Producer 规划
            # ═══════════════════════════════════════
            self._log(state, "🎬 Producer 开始规划项目...")
            state["status"] = "planning"
            state["current_phase"] = "producer_planning"
            self._persist_project(project_dir, state)

            plan = self._producer_plan(state["direction"])
            state["plan"] = plan
            state["status"] = "planned"
            state["current_phase"] = "plan_ready"
            self._log(state, "✅ Producer 规划完成：%s" % plan.get("project_name", "未命名"))

            # 写入 project-drive 文件
            self._write_project_drive(plan)
            self._log(state, "📁 项目文件已写入 project-drive")
            self._persist_project(project_dir, state)

            # ═══════════════════════════════════════
            # Phase 2: 逐任务推进
            # ═══════════════════════════════════════
            state["status"] = "executing"
            tasks = plan.get("tasks", [])

            for i, task in enumerate(tasks):
                task_id = task.get("id", "TASK-%03d" % (i + 1))
                task_title = task.get("title", "未命名任务")

                state["current_phase"] = "task_%s" % task_id
                state["active_task"] = task
                self._log(state, "🔄 开始任务 %s: %s" % (task_id, task_title))

                # 写入 task card
                self._write_task_card(task, "in-progress")

                # 更新 active context
                self._update_active_context(plan, task)

                # 发起多角色共识
                goal = (
                    "围绕 %s（%s）达成跨角色共识。\n"
                    "任务描述：%s\n"
                    "验收标准：%s\n"
                    "请各角色从自身职责出发给出判断和可执行建议。"
                ) % (
                    task_id,
                    task_title,
                    task.get("description", ""),
                    "；".join(task.get("acceptance_criteria", [])),
                )

                self._log(state, "🤝 发起多角色共识: %s" % task_id)
                run_state = self.consensus_engine.create_run(goal)
                run_id = run_state["run_id"]
                state["consensus_runs"].append(run_id)
                self._persist_project(project_dir, state)

                # 等待共识完成
                self._wait_for_run(run_id)

                run_result = self.consensus_engine.get_run(run_id)
                if run_result and run_result.get("status") == "completed":
                    self._log(state, "✅ 任务 %s 共识达成" % task_id)
                else:
                    self._log(state, "⚠️ 任务 %s 共识未完全达成，采用制作人收敛方案" % task_id)

                # 将 task 从 in-progress 移到 completed（通过删除并标记）
                state["completed_tasks"].append(task)

                # 移动 task card 到 completed（仍留在 in-progress 但标记完成）
                self._persist_project(project_dir, state)

            # ═══════════════════════════════════════
            # Phase 3: 完成
            # ═══════════════════════════════════════
            state["status"] = "completed"
            state["current_phase"] = "all_done"
            state["active_task"] = None
            state["finished_at"] = datetime.utcnow().isoformat() + "Z"
            self._log(state, "🎉 项目规划与共识全部完成")

            # 写最终总结
            summary = self._build_project_summary(state)
            (project_dir / "project_summary.md").write_text(summary, encoding="utf-8")
            self._persist_project(project_dir, state)

        except Exception as exc:
            state["status"] = "failed"
            state["error"] = str(exc)
            state["finished_at"] = datetime.utcnow().isoformat() + "Z"
            self._log(state, "❌ 项目执行失败: %s" % str(exc))
            self._persist_project(project_dir, state)

    def _producer_plan(self, direction):
        """调用 LLM 让 producer 从方向描述生成完整规划。"""
        user_prompt = (
            "用户给出的项目方向描述：\n\n"
            "%s\n\n"
            "请基于这个方向，输出完整的项目启动规划。"
        ) % direction

        raw = self.llm.complete(PRODUCER_SYSTEM_PROMPT, user_prompt)

        # 尝试提取 JSON
        # 有时 LLM 会用 ```json ... ``` 包裹
        import re
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', raw, re.DOTALL)
        if json_match:
            raw = json_match.group(1)

        # 尝试找到第一个 { 到最后一个 }
        start = raw.find('{')
        end = raw.rfind('}')
        if start != -1 and end != -1:
            raw = raw[start:end + 1]

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            # 兜底：返回结构化的错误信息
            return {
                "project_name": "解析失败",
                "theme": direction,
                "platform": "Web",
                "visual_style": "待定",
                "core_loop": "待 Producer 人工确认",
                "mvp_scope": {"must_have": [], "nice_to_have": [], "not_doing": []},
                "milestones": [],
                "tasks": [],
                "risks": ["Producer 自动规划解析失败，需人工介入"],
                "success_criteria": "待定",
                "_raw_output": raw,
            }

    def _write_project_drive(self, plan):
        """将规划结果写入 project-drive 相关文件。"""
        pd = self.config.project_drive_dir

        # 写 active context
        active_ctx = self._generate_active_context(plan)
        (pd / "00-active-context.md").write_text(active_ctx, encoding="utf-8")

        # 写各个 task card
        tasks = plan.get("tasks", [])
        in_progress_dir = pd / "02-task-cards" / "in-progress"
        pending_dir = pd / "02-task-cards" / "pending"
        in_progress_dir.mkdir(parents=True, exist_ok=True)
        pending_dir.mkdir(parents=True, exist_ok=True)

        for i, task in enumerate(tasks):
            task_id = task.get("id", "TASK-%03d" % (i + 1))
            title = task.get("title", "未命名")
            filename = "%s_%s.md" % (task_id, title.replace("/", "-").replace(" ", "_"))
            content = self._generate_task_card(task, plan)

            if i == 0:
                (in_progress_dir / filename).write_text(content, encoding="utf-8")
            else:
                (pending_dir / filename).write_text(content, encoding="utf-8")

    def _generate_active_context(self, plan):
        """生成 00-active-context.md 的内容。"""
        now = datetime.utcnow().strftime("%Y-%m-%d")
        tasks = plan.get("tasks", [])
        milestones = plan.get("milestones", [])
        mvp = plan.get("mvp_scope", {})

        lines = [
            "# 00-active-context",
            "",
            "**最后更新**：%s" % now,
            "**项目名称**：%s" % plan.get("project_name", "未命名"),
            "**当前阶段**：项目启动与规划",
            "**视觉风格**：%s" % plan.get("visual_style", "待定"),
            "**目标平台**：%s" % plan.get("platform", "Web"),
            "",
            "---",
            "",
            "## 1. 项目主题",
            "",
            plan.get("theme", ""),
            "",
            "## 2. 核心循环",
            "",
            plan.get("core_loop", ""),
            "",
            "## 3. MVP 范围",
            "",
            "### 必做",
        ]
        for item in mvp.get("must_have", []):
            lines.append("- %s" % item)

        lines.append("")
        lines.append("### 可延后")
        for item in mvp.get("nice_to_have", []):
            lines.append("- %s" % item)

        lines.append("")
        lines.append("### 明确不做")
        for item in mvp.get("not_doing", []):
            lines.append("- %s" % item)

        lines.append("")
        lines.append("## 4. 里程碑")
        lines.append("")
        for ms in milestones:
            lines.append("### %s：%s" % (ms.get("id", "?"), ms.get("name", "?")))
            lines.append("- **周期**：%s" % ms.get("duration", "?"))
            lines.append("- **目标**：%s" % ms.get("goal", "?"))
            lines.append("- **主责**：%s" % ms.get("owner", "?"))
            lines.append("")

        lines.append("## 5. 当前活跃任务")
        lines.append("")
        if tasks:
            t = tasks[0]
            tid = t.get("id", "TASK-001")
            lines.append("### %s：%s" % (tid, t.get("title", "")))
            lines.append("- **位置**: `project-drive/02-task-cards/in-progress/%s_%s.md`" % (
                tid, t.get("title", "").replace("/", "-").replace(" ", "_")
            ))
            lines.append("- **当前状态**: 进行中")
            lines.append("- **当前负责人**: `%s`" % t.get("owner", "producer"))
            lines.append("")

        lines.append("## 6. 任务总览")
        lines.append("")
        lines.append("| ID | 标题 | 优先级 | 主责 | 状态 |")
        lines.append("|:--|:--|:--|:--|:--|")
        for i, t in enumerate(tasks):
            status = "进行中" if i == 0 else "待启动"
            lines.append("| %s | %s | %s | %s | %s |" % (
                t.get("id", "?"),
                t.get("title", "?"),
                t.get("priority", "?"),
                t.get("owner", "?"),
                status,
            ))

        lines.append("")
        lines.append("## 7. 风险")
        lines.append("")
        for r in plan.get("risks", []):
            lines.append("- %s" % r)

        lines.append("")
        lines.append("## 8. 成功标准")
        lines.append("")
        lines.append(plan.get("success_criteria", "待定"))
        lines.append("")

        return "\n".join(lines)

    def _generate_task_card(self, task, plan):
        """生成单个 task card 的 md 内容。"""
        lines = [
            "# %s：%s" % (task.get("id", "TASK-???"), task.get("title", "未命名")),
            "",
            "**项目**：%s" % plan.get("project_name", "未命名"),
            "**主责**：%s" % task.get("owner", "未指定"),
            "**优先级**：%s" % task.get("priority", "P1"),
            "**所属里程碑**：%s" % task.get("milestone", "未指定"),
            "",
            "## 任务描述",
            "",
            task.get("description", ""),
            "",
            "## 验收标准",
            "",
        ]
        for ac in task.get("acceptance_criteria", []):
            lines.append("- [ ] %s" % ac)

        lines.append("")
        lines.append("## 依赖")
        lines.append("")
        deps = task.get("depends_on", [])
        if deps:
            for d in deps:
                lines.append("- %s" % d)
        else:
            lines.append("- 无")

        lines.append("")
        return "\n".join(lines)

    def _write_task_card(self, task, status_dir):
        """写入或更新单个 task card。"""
        pd = self.config.project_drive_dir
        target_dir = pd / "02-task-cards" / status_dir
        target_dir.mkdir(parents=True, exist_ok=True)

        task_id = task.get("id", "TASK-???")
        title = task.get("title", "未命名")
        filename = "%s_%s.md" % (task_id, title.replace("/", "-").replace(" ", "_"))

        # 仅在文件不存在时写入（避免覆盖共识结果）
        path = target_dir / filename
        if not path.exists():
            content = self._generate_task_card(task, self.get_project(None) or {})
            path.write_text(content, encoding="utf-8")

    def _update_active_context(self, plan, current_task):
        """更新 active context 中的当前任务信息。"""
        pd = self.config.project_drive_dir
        path = pd / "00-active-context.md"

        if path.exists():
            content = path.read_text(encoding="utf-8")
            # 简单替换当前活跃任务段落（找到 ## 5. 当前活跃任务）
            import re
            task_id = current_task.get("id", "?")
            task_title = current_task.get("title", "?")
            owner = current_task.get("owner", "producer")

            new_section = (
                "## 5. 当前活跃任务\n\n"
                "### %s：%s\n"
                "- **当前状态**: 进行中\n"
                "- **当前负责人**: `%s`\n"
            ) % (task_id, task_title, owner)

            content = re.sub(
                r"## 5\. 当前活跃任务.*?(?=## 6\.)",
                new_section + "\n",
                content,
                flags=re.DOTALL,
            )
            path.write_text(content, encoding="utf-8")

    def _wait_for_run(self, run_id, timeout=600):
        """等待共识运行完成。"""
        import time
        start = time.time()
        while time.time() - start < timeout:
            run_state = self.consensus_engine.get_run(run_id)
            if not run_state:
                return
            if run_state.get("status") in ("completed", "failed"):
                return
            time.sleep(2)

    def _build_project_summary(self, state):
        """构建项目最终总结。"""
        plan = state.get("plan", {})
        lines = [
            "# 项目总结",
            "",
            "**项目名称**：%s" % plan.get("project_name", "未命名"),
            "**创建时间**：%s" % state.get("created_at", "?"),
            "**完成时间**：%s" % state.get("finished_at", "?"),
            "",
            "## 完成的任务",
            "",
        ]
        for task in state.get("completed_tasks", []):
            lines.append("- **%s**: %s" % (task.get("id", "?"), task.get("title", "?")))

        lines.append("")
        lines.append("## 共识运行记录")
        lines.append("")
        for run_id in state.get("consensus_runs", []):
            lines.append("- %s" % run_id)

        lines.append("")
        return "\n".join(lines)

    @staticmethod
    def _persist_project(project_dir, state):
        (project_dir / "state.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
