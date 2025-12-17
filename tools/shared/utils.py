from pathlib import Path


def get_repo_root(tools_dir: Path) -> Path:
    # The repo root is the parent of the tools directory.
    return tools_dir.parent
