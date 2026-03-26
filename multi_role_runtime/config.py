import os
from pathlib import Path


class RuntimeConfig(object):
    def __init__(self, base_url, api_key, model, project_drive_dir, output_dir, max_rounds=4):
        self.base_url = base_url
        self.api_key = api_key
        self.model = model
        self.project_drive_dir = project_drive_dir
        self.output_dir = output_dir
        self.max_rounds = max_rounds


def load_config():
    workspace = Path(os.getenv("WORKSPACE_DIR", ".")).resolve()
    project_drive = Path(
        os.getenv("PROJECT_DRIVE_DIR", str(workspace / "project-drive"))
    ).resolve()

    base_url = os.getenv("CUSTOM_LLM_BASE_URL", "https://capi.quan2go.com/v1")
    model = os.getenv("CUSTOM_LLM_MODEL", "gpt-5.3-codex")
    api_key = os.getenv("CUSTOM_LLM_API_KEY", "740B6527-A51F-4C02-BF65-EE035119D39F")

    output_dir = Path(
        os.getenv("RUNTIME_OUTPUT_DIR", str(project_drive / "runtime" / "runs"))
    ).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    return RuntimeConfig(
        base_url=base_url,
        api_key=api_key,
        model=model,
        project_drive_dir=project_drive,
        output_dir=output_dir,
        max_rounds=int(os.getenv("CONSENSUS_MAX_ROUNDS", "4")),
    )
