from pathlib import Path


def list_agent_manifest_paths(agents_dir: Path) -> list[Path]:
    return sorted(agents_dir.glob("*/manifest.yaml"))
