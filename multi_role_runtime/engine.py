import json
import re
import threading
import uuid
from datetime import datetime

from .config import load_config
from .llm import LLMClient
from .models import new_run_state, new_turn

ROLE_ORDER = [
    "producer",
    "systems-economy",
    "web-tech-lead",
    "visual-ui",
    "prototype-qa",
]

ROLE_PROMPTS = {
    "producer": "你是制作人，关注范围控制、优先级和里程碑，输出可执行裁决。",
    "systems-economy": "你是系统/数值策划，关注核心循环、资源流、公式和可玩节奏。",
    "web-tech-lead": "你是 Web 技术负责人，关注工程可行性、模块拆分、风险与降级方案。",
    "visual-ui": "你是视觉/UI负责人，关注信息架构、交互密度、可读性与一致性。",
    "prototype-qa": "你是原型 QA，关注可验证性、测试门禁、边界条件与质量风险。",
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
            self._persist_state(run_dir, state)

            shared_snapshot = self._collect_project_drive_context()
            discussion_history = []

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

                if agree_count == len(ROLE_ORDER):
                    state["status"] = "completed"
                    state["summary"] = self._build_summary(state)
                    state["finished_at"] = datetime.utcnow().isoformat() + "Z"
                    (run_dir / "consensus.md").write_text(state["summary"], encoding="utf-8")
                    self._persist_state(run_dir, state)
                    return

            state["status"] = "completed"
            state["summary"] = self._build_summary(state, forced=True)
            state["finished_at"] = datetime.utcnow().isoformat() + "Z"
            (run_dir / "consensus.md").write_text(state["summary"], encoding="utf-8")
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

    @staticmethod
    def _build_summary(state, forced=False):
        title = "# 多角色共识结论\n\n"
        if forced:
            status_line = "- 结论：在最大轮次内未全员一致，采用制作人收敛方案。\n"
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
        lines.append("- 将 `consensus.md` 作为 TASK 下一阶段输入。\n")
        lines.append("- 基于最后一轮意见拆分工程任务并进入实现。\n")
        return "".join(lines)

    @staticmethod
    def _persist_state(run_dir, state):
        (run_dir / "state.json").write_text(
            json.dumps(state, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
