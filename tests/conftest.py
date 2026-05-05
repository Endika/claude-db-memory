from pathlib import Path

import pytest


@pytest.fixture
def memory_dir(tmp_path: Path, monkeypatch) -> Path:
    """Isolated memory directory for tests."""
    d = tmp_path / "memory"
    d.mkdir()
    monkeypatch.setenv("CLAUDE_DB_MEMORY_DIR", str(d))
    return d
