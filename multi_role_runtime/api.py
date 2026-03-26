import re

from flask import Flask, jsonify, request, send_from_directory

from .engine import ConsensusEngine

app = Flask(__name__, static_folder="web")
engine = ConsensusEngine()


def _read_text(path):
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return ""


def detect_active_task():
    pd = engine.config.project_drive_dir
    active_context = pd / "00-active-context.md"
    text = _read_text(active_context)

    task_id = ""
    task_title = ""
    task_file = ""
    task_status = ""
    owner = ""

    lines = text.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"^###\s*(TASK-\d+[A-Z]?)：?(.*)$", line.strip())
        if m and not task_id:
            task_id = m.group(1).strip()
            task_title = (m.group(2) or "").strip() or "未命名任务"

            for j in range(i + 1, min(i + 10, len(lines))):
                item = lines[j].strip()
                if item.startswith("- **位置**:"):
                    task_file = item.split(":", 1)[1].strip().strip("`")
                elif item.startswith("- **当前状态**:"):
                    task_status = item.split(":", 1)[1].strip()
                elif item.startswith("- **当前负责人**:"):
                    owner = item.split(":", 1)[1].strip().strip("`")
            break

    if not task_id:
        in_progress_dir = pd / "02-task-cards" / "in-progress"
        if in_progress_dir.exists():
            for path in sorted(in_progress_dir.glob("TASK-*.md")):
                m = re.match(r"^(TASK-\d+[A-Z]?)_(.*)\.md$", path.name)
                if m:
                    task_id = m.group(1)
                    task_title = m.group(2)
                    task_file = "project-drive/02-task-cards/in-progress/%s" % path.name
                    task_status = "In Progress"
                    owner = "未标注"
                    break

    if not task_id:
        return None

    stage_line = ""
    for line in lines:
        if line.strip().startswith("**当前阶段**"):
            stage_line = line.split("：", 1)[-1].strip()
            break

    auto_goal = "围绕 %s（%s）达成跨角色共识，产出可执行下一步与责任拆分。" % (task_id, task_title)
    if task_status:
        auto_goal += " 当前状态：%s。" % task_status

    return {
        "task_id": task_id,
        "task_title": task_title,
        "task_file": task_file,
        "task_status": task_status,
        "owner": owner,
        "stage": stage_line,
        "auto_goal": auto_goal,
    }


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/health", methods=["GET"])
def health():
    cfg = engine.config
    return jsonify({
        "ok": True,
        "model": cfg.model,
        "base_url": cfg.base_url,
        "project_drive_dir": str(cfg.project_drive_dir),
        "output_dir": str(cfg.output_dir),
    })


@app.route("/api/active-task", methods=["GET"])
def active_task():
    task = detect_active_task()
    if not task:
        return jsonify({"error": "未检测到活跃 TASK"}), 404
    return jsonify(task)


@app.route("/api/runs", methods=["POST"])
def create_run():
    data = request.get_json(silent=True) or {}
    goal = (data.get("goal") or "").strip()
    if len(goal) < 8:
        return jsonify({"error": "goal 至少 8 个字符"}), 400
    state = engine.create_run(goal)
    return jsonify(state)


@app.route("/api/runs/active-task", methods=["POST"])
def create_run_from_active_task():
    task = detect_active_task()
    if not task:
        return jsonify({"error": "未检测到活跃 TASK"}), 404

    data = request.get_json(silent=True) or {}
    override_goal = (data.get("goal") or "").strip()
    goal = override_goal if len(override_goal) >= 8 else task["auto_goal"]

    state = engine.create_run(goal)
    return jsonify({"task": task, "run": state})


@app.route("/api/runs", methods=["GET"])
def list_runs():
    return jsonify(engine.list_runs())


@app.route("/api/runs/<run_id>", methods=["GET"])
def get_run(run_id):
    state = engine.get_run(run_id)
    if not state:
        return jsonify({"error": "run not found"}), 404
    return jsonify(state)
