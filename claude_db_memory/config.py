import os
from pathlib import Path


def resolve_memory_dir() -> Path:
    if env := os.getenv("CLAUDE_DB_MEMORY_DIR"):
        return Path(env)
    workspace = Path.cwd().resolve()
    encoded = str(workspace).replace("/", "-")
    return Path.home() / ".claude" / "projects" / encoded / "memory"


def db_path() -> Path:
    return resolve_memory_dir() / "memory.db"


def md_dir() -> Path:
    return resolve_memory_dir() / "memories"


def index_path() -> Path:
    return resolve_memory_dir() / "MEMORY.md"


def ensure_dirs() -> None:
    resolve_memory_dir().mkdir(parents=True, exist_ok=True)
    md_dir().mkdir(parents=True, exist_ok=True)
