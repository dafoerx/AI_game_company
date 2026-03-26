from datetime import datetime


def utc_now_iso():
    return datetime.utcnow().isoformat() + "Z"


def new_run_state(run_id, goal, max_rounds):
    return {
        "run_id": run_id,
        "status": "queued",
        "goal": goal,
        "started_at": utc_now_iso(),
        "finished_at": None,
        "current_round": 0,
        "max_rounds": max_rounds,
        "turns": [],
        "summary": "",
        "error": None,
    }


def new_turn(role, round_index, content, consensus):
    return {
        "role": role,
        "round_index": round_index,
        "content": content,
        "consensus": consensus,
        "created_at": utc_now_iso(),
    }
