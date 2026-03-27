import re

from flask import Flask, jsonify, request, send_from_directory

from .engine import ConsensusEngine
from .project_engine import ProjectEngine
from .code_generator import CodeGenerator

app = Flask(__name__, static_folder="web")
engine = ConsensusEngine()
project_engine = ProjectEngine(engine.config)
code_generator = CodeGenerator(engine.config)

# 让 project_engine 共享同一个 consensus_engine 实例
project_engine.consensus_engine = engine


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
                m = re.match(r"^(TASK-\d+[A-Z]?)_(.*)\\.md$", path.name)
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


# ═══════════════════════════════════════════════════
# 项目相关 API（新增）
# ═══════════════════════════════════════════════════

@app.route("/api/projects", methods=["POST"])
def create_project():
    """
    启动新项目。
    Body: { "direction": "火锅店运营，web端显示，界面较为美观，水墨画风" }
    """
    data = request.get_json(silent=True) or {}
    direction = (data.get("direction") or "").strip()
    if len(direction) < 4:
        return jsonify({"error": "方向描述至少 4 个字符"}), 400
    state = project_engine.create_project(direction)
    return jsonify(state)


@app.route("/api/projects", methods=["GET"])
def list_projects():
    return jsonify(project_engine.list_projects())


@app.route("/api/projects/<project_id>", methods=["GET"])
def get_project(project_id):
    state = project_engine.get_project(project_id)
    if not state:
        return jsonify({"error": "项目不存在"}), 404
    return jsonify(state)


# ═══════════════════════════════════════════════════
# 原有共识相关 API
# ═══════════════════════════════════════════════════

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


# ═══════════════════════════════════════════════════
# 代码生成相关 API（新增）
# ═══════════════════════════════════════════════════

@app.route("/api/codegen", methods=["POST"])
def start_code_generation():
    """
    启动代码生成流程。
    Body: { "project_id": "可选，指定项目ID" }
    """
    data = request.get_json(silent=True) or {}
    project_id = data.get("project_id")
    state = code_generator.start_generation(project_id)
    return jsonify(state)


@app.route("/api/codegen", methods=["GET"])
def list_code_generations():
    """列出所有代码生成任务。"""
    return jsonify(code_generator.list_generations())


@app.route("/api/codegen/<gen_id>", methods=["GET"])
def get_code_generation(gen_id):
    """获取指定的代码生成任务状态。"""
    state = code_generator.get_generation(gen_id)
    if not state:
        return jsonify({"error": "代码生成任务不存在"}), 404
    return jsonify(state)


@app.route("/api/codegen/<gen_id>/files", methods=["GET"])
def list_generated_files(gen_id):
    """列出生成的文件。"""
    from pathlib import Path
    state = code_generator.get_generation(gen_id)
    if not state:
        return jsonify({"error": "代码生成任务不存在"}), 404
    
    gen_dir = Path(state["output_dir"])
    if not gen_dir.exists():
        return jsonify({"files": []})
    
    files = []
    for path in sorted(gen_dir.rglob("*")):
        if path.is_file() and not path.name.startswith("."):
            rel_path = str(path.relative_to(gen_dir))
            files.append({
                "path": rel_path,
                "size": path.stat().st_size,
                "ext": path.suffix,
            })
    
    return jsonify({"files": files})


@app.route("/api/codegen/<gen_id>/file/<path:file_path>", methods=["GET"])
def get_generated_file(gen_id, file_path):
    """获取生成的文件内容。"""
    from pathlib import Path
    state = code_generator.get_generation(gen_id)
    if not state:
        return jsonify({"error": "代码生成任务不存在"}), 404
    
    gen_dir = Path(state["output_dir"])
    file_full_path = gen_dir / file_path
    
    if not file_full_path.exists():
        return jsonify({"error": "文件不存在"}), 404
    
    # 安全检查：确保文件在生成目录内
    try:
        file_full_path.relative_to(gen_dir)
    except ValueError:
        return jsonify({"error": "无效的文件路径"}), 400
    
    content = file_full_path.read_text(encoding="utf-8", errors="ignore")
    return jsonify({
        "path": file_path,
        "content": content,
    })


@app.route("/api/codegen/<gen_id>/preview")
def preview_generated_game(gen_id):
    """预览生成的游戏（返回 index.html）。"""
    from pathlib import Path
    state = code_generator.get_generation(gen_id)
    if not state:
        return "代码生成任务不存在", 404
    
    gen_dir = Path(state["output_dir"])
    index_path = gen_dir / "index.html"
    
    if not index_path.exists():
        return "游戏尚未生成完成", 404
    
    return send_from_directory(str(gen_dir), "index.html")


@app.route("/api/codegen/<gen_id>/static/<path:file_path>")
def serve_generated_static(gen_id, file_path):
    """提供生成的静态文件（CSS/JS等）。"""
    from pathlib import Path
    state = code_generator.get_generation(gen_id)
    if not state:
        return "代码生成任务不存在", 404
    
    gen_dir = Path(state["output_dir"])
    return send_from_directory(str(gen_dir), file_path)
