from flask import Flask, jsonify, request, send_from_directory

from .engine import ConsensusEngine

app = Flask(__name__, static_folder="web")
engine = ConsensusEngine()


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


@app.route("/api/runs", methods=["POST"])
def create_run():
    data = request.get_json(silent=True) or {}
    goal = (data.get("goal") or "").strip()
    if len(goal) < 8:
        return jsonify({"error": "goal 至少 8 个字符"}), 400
    state = engine.create_run(goal)
    return jsonify(state)


@app.route("/api/runs", methods=["GET"])
def list_runs():
    return jsonify(engine.list_runs())


@app.route("/api/runs/<run_id>", methods=["GET"])
def get_run(run_id):
    state = engine.get_run(run_id)
    if not state:
        return jsonify({"error": "run not found"}), 404
    return jsonify(state)
