from pathlib import Path

from claude_db_memory.config import db_path, index_path, md_dir, resolve_memory_dir


def test_resolve_memory_dir_uses_env_var(monkeypatch, tmp_path):
    monkeypatch.setenv("CLAUDE_DB_MEMORY_DIR", str(tmp_path))
    assert resolve_memory_dir() == tmp_path


def test_resolve_memory_dir_default_per_workspace(monkeypatch, tmp_path):
    monkeypatch.delenv("CLAUDE_DB_MEMORY_DIR", raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    expected_encoded = str(tmp_path.resolve()).replace("/", "-")
    expected = Path(tmp_path / "home" / ".claude" / "projects" / expected_encoded / "memory")
    assert resolve_memory_dir() == expected


def test_db_path_under_memory_dir(memory_dir):
    assert db_path() == memory_dir / "memory.db"


def test_md_dir_under_memory_dir(memory_dir):
    assert md_dir() == memory_dir / "memories"


def test_index_path_under_memory_dir(memory_dir):
    assert index_path() == memory_dir / "MEMORY.md"
