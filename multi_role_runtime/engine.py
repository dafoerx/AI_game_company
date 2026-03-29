import json
import re
import threading
import uuid
from datetime import datetime

from .config import load_config
from .llm import LLMClient
from .models import new_run_state, new_turn
from .design_spec import (
    detect_theme,
    generate_design_spec,
    verify_design_spec,
    get_scaffolding,
)

ROLE_ORDER = [
    "producer",
    "systems-economy",
    "web-tech-lead",
    "visual-ui",
    "prototype-qa",
    "design-verifier",
]

ROLE_PROMPTS = {
    "producer": "你是制作人，关注范围控制、优先级和里程碑，输出可执行裁决。",
    "systems-economy": "你是系统/数值策划，关注核心循环、资源流、公式和可玩节奏。",
    "web-tech-lead": "你是 Web 技术负责人，关注工程可行性、模块拆分、风险与降级方案。",
    "visual-ui": "你是视觉/UI负责人，关注信息架构、交互密度、可读性与一致性。",
    "prototype-qa": "你是原型 QA，关注可验证性、测试门禁、边界条件与质量风险。",
    "design-verifier": (
        "你是设计验证专家，关注设计规格的完整性和可执行性。"
        "你需要检查：实体定义是否充分、状态机是否闭环、数值是否平衡、"
        "交互流程是否清晰、核心情感体验是否有机制承载。"
        "如果设计规格不足以指导代码生成，你必须明确指出缺失项。"
    ),
}


class ConsensusEngine(object):
    def __init__(self, config=None):
        self.config = config or load_config()
        self.llm = LLMClient(
            base_url=self.config.base_url,
            api_key=self.config.api_key,
            model=self.config.model,
        )
        self._lock = threading.Lock()
        self._runs = {}

    def list_runs(self):
        with self._lock:
            return sorted(self._runs.values(), key=lambda x: x["started_at"], reverse=True)

    def get_run(self, run_id):
        with self._lock:
            return self._runs.get(run_id)

    def create_run(self, goal):
        run_id = datetime.utcnow().strftime("%Y%m%d-%H%M%S") + "-" + uuid.uuid4().hex[:6]
        state = new_run_state(run_id, goal, self.config.max_rounds)
        with self._lock:
            self._runs[run_id] = state

        t = threading.Thread(target=self._run_in_background, args=(run_id,))
        t.daemon = True
        t.start()
        return state

    def _run_in_background(self, run_id):
        state = self.get_run(run_id)
        if not state:
            return

        run_dir = self.config.output_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)

        try:
            state["status"] = "running"
            # Initialize new fields for design spec output
            state["design_spec"] = None
            state["design_verification"] = None
            state["theme_mapping"] = None
            state["escalation_triggered"] = False
            self._persist_state(run_dir, state)

            shared_snapshot = self._collect_project_drive_context()
            discussion_history = []
            consecutive_all_revise = 0

            for round_index in range(1, state["max_rounds"] + 1):
                state["current_round"] = round_index
                agree_count = 0
                round_dir = run_dir / ("round-%s" % round_index)
                round_dir.mkdir(parents=True, exist_ok=True)

                for role in ROLE_ORDER:
                    content = self._generate_role_output(
                        role=role,
                        goal=state["goal"],
                        round_index=round_index,
                        shared_context=shared_snapshot,
                        discussion_history=discussion_history,
                    )
                    consensus = self._parse_consensus(content)
                    if consensus == "AGREE":
                        agree_count += 1

                    turn = new_turn(role, round_index, content, consensus)
                    state["turns"].append(turn)
                    discussion_history.append("[%s]\n%s" % (role, content))

                    (round_dir / ("%s.md" % role)).write_text(content, encoding="utf-8")
                    self._persist_state(run_dir, state)

                # Track consecutive all-REVISE rounds for escalation
                if agree_count == 0:
                    consecutive_all_revise += 1
                else:
                    consecutive_all_revise = 0

                # Escalation: if 2+ consecutive rounds are all REVISE,
                # inject a focused reconciliation prompt
                if consecutive_all_revise >= 2 and round_index < state["max_rounds"]:
                    state["escalation_triggered"] = True
                    escalation_content = self._generate_escalation_reconciliation(
                        goal=state["goal"],
                        shared_context=shared_snapshot,
                        discussion_history=discussion_history,
                    )
                    discussion_history.append(
                        "[ESCALATION-RECONCILIATION]\n%s" % escalation_content
                    )
                    (round_dir / "escalation.md").write_text(
                        escalation_content, encoding="utf-8"
                    )
                    self._persist_state(run_dir, state)

                if agree_count == len(ROLE_ORDER):
                    state["status"] = "completed"
                    state["summary"] = self._build_summary(state)
                    state["finished_at"] = datetime.utcnow().isoformat() + "Z"
                    (run_dir / "consensus.md").write_text(state["summary"], encoding="utf-8")
                    # Generate design spec after successful consensus
                    self._generate_and_verify_design_spec(
                        state, run_dir, discussion_history
                    )
                    self._persist_state(run_dir, state)
                    return

            state["status"] = "completed"
            state["summary"] = self._build_summary(state, forced=True)
            state["finished_at"] = datetime.utcnow().isoformat() + "Z"
            (run_dir / "consensus.md").write_text(state["summary"], encoding="utf-8")
            # Generate design spec even after forced convergence
            self._generate_and_verify_design_spec(
                state, run_dir, discussion_history
            )
            self._persist_state(run_dir, state)

        except Exception as exc:
            state["status"] = "failed"
            state["error"] = str(exc)
            state["finished_at"] = datetime.utcnow().isoformat() + "Z"
            self._persist_state(run_dir, state)

    def _collect_project_drive_context(self):
        pd = self.config.project_drive_dir
        chunks = []

        candidates = [
            pd / "00-active-context.md",
            pd / "README.md",
        ]

        in_progress_dir = pd / "02-task-cards" / "in-progress"
        if in_progress_dir.exists():
            for path in sorted(in_progress_dir.glob("*.md"))[:4]:
                candidates.append(path)

        for path in candidates:
            if path.exists():
                txt = path.read_text(encoding="utf-8", errors="ignore")
                chunks.append("## FILE: %s\n%s" % (path.name, txt[:6000]))

        return "\n\n".join(chunks)

    def _generate_role_output(self, role, goal, round_index, shared_context, discussion_history):
        system_prompt = (
            "你在一个单机多角色共识系统中工作。"
            "所有角色访问同一个 project-drive 目录，不通过 git 上传。"
            "请严格输出中文，并在最后一行明确写 CONSENSUS: AGREE 或 CONSENSUS: REVISE。"
        )

        if discussion_history:
            recent = "\n\n".join(discussion_history[-6:])
        else:
            recent = "（首轮，无历史）"

        user_prompt = (
            "角色：%s\n"
            "角色职责：%s\n\n"
            "本轮目标：%s\n"
            "当前轮次：%s\n\n"
            "共享目录快照（来自 @project-drive）：\n%s\n\n"
            "最近讨论记录：\n%s\n\n"
            "请输出：\n"
            "1) 本角色判断（3-6条）\n"
            "2) 对其他角色的冲突点/共识点\n"
            "3) 下一步建议（必须可执行）\n"
            "4) 最后一行写：CONSENSUS: AGREE 或 CONSENSUS: REVISE\n"
        ) % (role, ROLE_PROMPTS[role], goal, round_index, shared_context, recent)

        return self.llm.complete(system_prompt, user_prompt)

    @staticmethod
    def _parse_consensus(content):
        m = re.search(r"CONSENSUS\s*:\s*(AGREE|REVISE)", content, re.IGNORECASE)
        if not m:
            return "REVISE"
        return m.group(1).upper()

    def _generate_escalation_reconciliation(self, goal, shared_context, discussion_history):
        """
        When multiple consecutive rounds end with all REVISE,
        generate a focused reconciliation prompt to break the deadlock.
        """
        system_prompt = (
            "你是一位资深的项目调解专家。多角色讨论已经连续多轮无法达成共识。\n"
            "你需要：\n"
            "1. 分析各角色分歧的根本原因\n"
            "2. 提出一个折中方案，明确列出每个角色需要让步的点\n"
            "3. 给出一份可以被所有角色接受的最小可行方案\n"
            "4. 将方案转化为具体的、可执行的设计决策（不是模糊的建议）\n"
            "请用中文输出。"
        )

        recent = "\n\n".join(discussion_history[-10:])
        user_prompt = (
            "目标：%s\n\n"
            "共享上下文：\n%s\n\n"
            "讨论历史（最近记录）：\n%s\n\n"
            "请分析分歧并提出折中方案。"
        ) % (goal, shared_context[:3000], recent)

        return self.llm.complete(system_prompt, user_prompt)

    def _generate_and_verify_design_spec(self, state, run_dir, discussion_history):
        """
        After consensus (or forced convergence), generate a structured
        design specification and verify it.

        This is the key bridge between "discussion" and "code generation".
        """
        try:
            # Detect theme from goal and context
            goal = state.get("goal", "")
            theme_mapping = detect_theme(goal)
            state["theme_mapping"] = {
                "theme_id": theme_mapping.get("theme_id"),
                "label": theme_mapping.get("label"),
                "scaffolding_type": theme_mapping.get("scaffolding_type"),
            }

            # Collect discussion texts for spec generation
            discussion_texts = [
                t["content"] for t in state.get("turns", [])
                if t.get("content")
            ]

            # Build a minimal plan dict from the goal and context
            plan = self._extract_plan_from_context()

            # Generate structured design spec
            spec = generate_design_spec(
                self.llm, plan, theme_mapping, discussion_texts
            )
            state["design_spec"] = spec

            # Write design spec to file
            spec_path = run_dir / "design_spec.json"
            spec_path.write_text(
                json.dumps(spec, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            # Verify the design spec
            verification = verify_design_spec(self.llm, spec, theme_mapping)
            state["design_verification"] = verification

            # Write verification report
            verify_path = run_dir / "design_verification.json"
            verify_path.write_text(
                json.dumps(verification, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            # Update summary with spec status
            spec_status = "✅ 通过" if verification.get("passed") else "⚠️ 需改进"
            spec_score = verification.get("score", 0)
            state["summary"] += (
                "\n## 设计规格输出\n"
                "- 设计规格文件：`design_spec.json`\n"
                "- 验证状态：%s（得分：%s/100）\n"
                "- 游戏类型：%s\n"
                "- 脚手架类型：%s\n"
            ) % (
                spec_status,
                spec_score,
                theme_mapping.get("label", "未知"),
                theme_mapping.get("scaffolding_type", "未知"),
            )

            blocking = verification.get("blocking_issues", [])
            if blocking:
                state["summary"] += "\n### 阻塞性问题\n"
                for issue in blocking:
                    state["summary"] += "- %s\n" % issue

            # Re-write consensus.md with updated summary
            (run_dir / "consensus.md").write_text(
                state["summary"], encoding="utf-8"
            )

        except Exception as exc:
            state["design_spec"] = {"error": str(exc)}
            state["design_verification"] = {
                "passed": False,
                "error": str(exc),
            }

    def _extract_plan_from_context(self):
        """Extract a plan-like dict from the active context file."""
        pd = self.config.project_drive_dir
        active_ctx_path = pd / "00-active-context.md"
        plan = {
            "project_name": "",
            "theme": "",
            "core_loop": "",
            "visual_style": "",
            "platform": "Web",
            "mvp_scope": {"must_have": [], "nice_to_have": [], "not_doing": []},
        }

        if not active_ctx_path.exists():
            return plan

        content = active_ctx_path.read_text(encoding="utf-8", errors="ignore")

        for line in content.splitlines():
            if line.startswith("**项目名称**"):
                plan["project_name"] = line.split("：", 1)[-1].strip()
            elif line.startswith("**视觉风格**"):
                plan["visual_style"] = line.split("：", 1)[-1].strip()
            elif line.startswith("**目标平台**"):
                plan["platform"] = line.split("：", 1)[-1].strip()

        if "## 1. 项目主题" in content:
            start = content.find("## 1. 项目主题")
            end = content.find("## 2.", start)
            if end > start:
                plan["theme"] = content[start:end].replace(
                    "## 1. 项目主题", ""
                ).strip()

        if "## 2. 核心循环" in content:
            start = content.find("## 2. 核心循环")
            end = content.find("## 3.", start)
            if end > start:
                plan["core_loop"] = content[start:end].replace(
                    "## 2. 核心循环", ""
                ).strip()

        return plan

    @staticmethod
    def _build_summary(state, forced=False):
        title = "# 多角色共识结论\n\n"
        if forced:
            if state.get("escalation_triggered"):
                status_line = (
                    "- 结论：在最大轮次内未全员一致，"
                    "已触发升级调解，采用制作人收敛方案。\n"
                )
            else:
                status_line = (
                    "- 结论：在最大轮次内未全员一致，"
                    "采用制作人收敛方案。\n"
                )
        else:
            status_line = "- 结论：已达成全员一致共识。\n"

        lines = [
            title,
            "- 目标：%s\n" % state["goal"],
            status_line,
            "- 总轮次：%s\n\n" % state["current_round"],
            "## 最终各角色态度\n",
        ]

        latest = {}
        for turn in state["turns"]:
            latest[turn["role"]] = turn["consensus"]

        for role in ROLE_ORDER:
            lines.append("- %s: %s\n" % (role, latest.get(role, "REVISE")))

        lines.append("\n## 执行建议\n")
        lines.append("- 将 `consensus.md` 和 `design_spec.json` 作为代码生成输入。\n")
        lines.append("- 设计规格已自动生成并验证，可直接驱动代码生成引擎。\n")
        lines.append("- 基于最后一轮意见拆分工程任务并进入实现。\n")
        return "".join(lines)

    @staticmethod
    def _persist_state(run_dir, state):
        (run_dir / "state.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
