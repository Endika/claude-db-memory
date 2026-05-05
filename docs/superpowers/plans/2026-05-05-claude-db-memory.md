# claude-db-memory Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Claude Code plugin that backs long-term memory with SQLite + FTS5, exposes CRUD via MCP and CLI, syncs to Markdown for backup, and auto-generates a compact `MEMORY.md` index compatible with Claude Code's native auto-load.

**Architecture:** Python package `claude_db_memory` with shared lib modules (`config`, `db`, `md_sync`, `models`) and per-operation modules under `operations/`. Two entry points share the same operation modules: an MCP server (`mcp_server.py`) that maps tool calls to operations, and a CLI dispatcher (`cli.py`) installed as the `memory` command. SQLite is the source of truth; `.md` files are a regenerable backup; `MEMORY.md` is a derived artifact.

**Tech Stack:** Python 3.9+ (stdlib only for runtime except `mcp` SDK), SQLite with FTS5, pytest for tests, GitHub Actions for CI.

**Spec deviation:** Spec section 8 said "zero non-stdlib runtime deps". The MCP protocol requires the official `mcp` package (~small footprint). All other runtime code uses stdlib only.

---

## File structure

```
claude-db-memory/
├── .claude-plugin/
│   └── plugin.json
├── .github/
│   └── workflows/
│       └── ci.yml
├── claude_db_memory/
│   ├── __init__.py
│   ├── cli.py
│   ├── config.py
│   ├── db.py
│   ├── md_sync.py
│   ├── models.py
│   └── operations/
│       ├── __init__.py
│       ├── add.py
│       ├── delete.py
│       ├── export.py
│       ├── get.py
│       ├── list_.py
│       ├── reindex.py
│       ├── search.py
│       ├── update.py
│       └── verify.py
├── mcp_server.py
├── tests/
│   ├── conftest.py
│   ├── test_config.py
│   ├── test_models.py
│   ├── test_db.py
│   ├── test_md_sync.py
│   ├── test_add.py
│   ├── test_get.py
│   ├── test_list.py
│   ├── test_delete.py
│   ├── test_search.py
│   ├── test_update.py
│   ├── test_reindex.py
│   ├── test_verify.py
│   ├── test_export.py
│   ├── test_cli.py
│   └── test_mcp_server.py
├── .gitignore
├── CHANGELOG.md
├── LICENSE
├── README.md
└── pyproject.toml
```

**Responsibility per module:**

- `config.py`: Resolve memory directory paths from env vars and workspace location.
- `models.py`: `Memory` dataclass, type validation, slug rules.
- `db.py`: SQLite connection management, schema bootstrap, FTS5 triggers, low-level row CRUD helpers.
- `md_sync.py`: Parse `.md` ↔ `Memory`, write/delete `.md` files, regenerate `MEMORY.md`.
- `operations/<op>.py`: One operation each. Calls into `db` and `md_sync`. Has a `main(args)` callable used by both MCP and CLI.
- `cli.py`: `argparse` dispatcher mapping subcommands to `operations/<op>.main`.
- `mcp_server.py`: Registers MCP tools that call `operations/<op>.main`.

---

## Phase 1 — Scaffolding

### Task 1: Repository scaffolding

**Files:**
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `LICENSE`
- Create: `README.md`
- Create: `CHANGELOG.md`
- Create: `claude_db_memory/__init__.py`
- Create: `claude_db_memory/operations/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1: Initialize git repo and base files**

```bash
cd /home/endikaiglesias/workspace/claude-db-memory
git init
git branch -M main
```

- [ ] **Step 2: Create `pyproject.toml`**

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "claude-db-memory"
version = "0.1.0"
description = "SQLite-backed long-term memory for Claude Code with FTS5 search and Markdown backup"
readme = "README.md"
license = { text = "MIT" }
requires-python = ">=3.9"
authors = [{ name = "claude-db-memory contributors" }]
dependencies = [
    "mcp>=1.0.0",
]

[project.optional-dependencies]
dev = ["pytest>=7.0", "pytest-cov"]

[project.scripts]
memory = "claude_db_memory.cli:main"

[tool.setuptools.packages.find]
include = ["claude_db_memory*"]

[tool.pytest.ini_options]
testpaths = ["tests"]
```

- [ ] **Step 3: Create `.gitignore`**

```
__pycache__/
*.pyc
*.pyo
.venv/
.pytest_cache/
.coverage
htmlcov/
*.db
*.db-wal
*.db-shm
.DS_Store
dist/
build/
*.egg-info/
```

- [ ] **Step 4: Create `LICENSE` (MIT)**

```
MIT License

Copyright (c) 2026 claude-db-memory contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 5: Create stub `README.md`, `CHANGELOG.md`, package `__init__.py` files**

`README.md`:

```markdown
# claude-db-memory

SQLite-backed long-term memory for Claude Code with FTS5 search and Markdown backup.

Status: under development. See `docs/superpowers/specs/` for design.
```

`CHANGELOG.md`:

```markdown
# Changelog

## [Unreleased]

### Added
- Initial scaffolding.
```

`claude_db_memory/__init__.py`:

```python
__version__ = "0.1.0"
```

`claude_db_memory/operations/__init__.py`: empty file.

`tests/__init__.py`: empty file.

- [ ] **Step 6: Commit**

```bash
git add .
git commit -m "chore: initial scaffolding"
```

---

### Task 2: GitHub Actions CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create CI workflow**

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.9", "3.10", "3.11", "3.12"]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
      - run: pip install -e ".[dev]"
      - run: pytest -v
```

- [ ] **Step 2: Commit**

```bash
git add .github/workflows/ci.yml
git commit -m "ci: add GitHub Actions test matrix"
```

---

## Phase 2 — Core lib

### Task 3: `config.py` — path resolution

**Files:**
- Create: `claude_db_memory/config.py`
- Create: `tests/conftest.py`
- Create: `tests/test_config.py`

- [ ] **Step 1: Create `tests/conftest.py` with shared fixtures**

```python
import pytest
from pathlib import Path


@pytest.fixture
def memory_dir(tmp_path: Path, monkeypatch) -> Path:
    """Isolated memory directory for tests."""
    d = tmp_path / "memory"
    d.mkdir()
    monkeypatch.setenv("CLAUDE_DB_MEMORY_DIR", str(d))
    return d
```

- [ ] **Step 2: Write failing tests for `config.py`**

`tests/test_config.py`:

```python
import os
from pathlib import Path

from claude_db_memory.config import resolve_memory_dir, db_path, md_dir, index_path


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
```

- [ ] **Step 3: Run tests and confirm they fail**

Run: `pytest tests/test_config.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'claude_db_memory.config'`

- [ ] **Step 4: Implement `claude_db_memory/config.py`**

```python
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
```

- [ ] **Step 5: Run tests and confirm they pass**

Run: `pytest tests/test_config.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add claude_db_memory/config.py tests/conftest.py tests/test_config.py
git commit -m "feat(config): resolve memory paths from env or workspace"
```

---

### Task 4: `models.py` — `Memory` dataclass and validation

**Files:**
- Create: `claude_db_memory/models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write failing tests**

`tests/test_models.py`:

```python
import pytest

from claude_db_memory.models import Memory, VALID_TYPES, validate_name, validate_type


def test_memory_dataclass_minimal():
    m = Memory(
        id=None,
        name="feedback_commits",
        type="feedback",
        description="Never run git writes",
        body="body text",
        tags=["git"],
        project=None,
        created_at="2026-05-05T10:00:00",
        updated_at="2026-05-05T10:00:00",
        source_file="memories/feedback_commits.md",
    )
    assert m.name == "feedback_commits"
    assert m.tags == ["git"]


def test_validate_name_accepts_slug():
    validate_name("feedback_commits")
    validate_name("project_tramita_frontend_v2")


def test_validate_name_rejects_invalid():
    for bad in ["With Space", "UPPER", "dashed-name", "trailing_", "", "with.dot"]:
        with pytest.raises(ValueError):
            validate_name(bad)


def test_validate_type_accepts_known():
    for t in VALID_TYPES:
        validate_type(t)


def test_validate_type_rejects_unknown():
    with pytest.raises(ValueError):
        validate_type("unknown_type")
```

- [ ] **Step 2: Run tests and confirm they fail**

Run: `pytest tests/test_models.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `claude_db_memory/models.py`**

```python
from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

VALID_TYPES = frozenset({"user", "feedback", "project", "reference", "note"})
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


def validate_name(name: str) -> None:
    if not NAME_PATTERN.match(name):
        raise ValueError(
            f"Invalid memory name {name!r}: must match {NAME_PATTERN.pattern}"
        )


def validate_type(type_: str) -> None:
    if type_ not in VALID_TYPES:
        raise ValueError(
            f"Invalid memory type {type_!r}: must be one of {sorted(VALID_TYPES)}"
        )


@dataclass
class Memory:
    id: Optional[int]
    name: str
    type: str
    description: str
    body: str
    tags: list[str] = field(default_factory=list)
    project: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    source_file: str = ""

    def __post_init__(self) -> None:
        validate_name(self.name)
        validate_type(self.type)
```

- [ ] **Step 4: Run tests and confirm they pass**

Run: `pytest tests/test_models.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add claude_db_memory/models.py tests/test_models.py
git commit -m "feat(models): Memory dataclass with name/type validation"
```

---

### Task 5: `db.py` — schema, connection, low-level CRUD

**Files:**
- Create: `claude_db_memory/db.py`
- Create: `tests/test_db.py`

- [ ] **Step 1: Write failing tests**

`tests/test_db.py`:

```python
import json
import sqlite3

from claude_db_memory.db import (
    connect,
    init_schema,
    insert_memory,
    update_memory,
    delete_memory,
    get_by_name,
    get_by_id,
    list_all,
    schema_version,
)
from claude_db_memory.models import Memory


def make_memory(name="m1", type_="feedback") -> Memory:
    return Memory(
        id=None, name=name, type=type_, description="d", body="b",
        tags=["t1"], project=None,
        created_at="2026-05-05T10:00:00", updated_at="2026-05-05T10:00:00",
        source_file=f"memories/{name}.md",
    )


def test_init_schema_creates_tables(memory_dir):
    conn = connect()
    init_schema(conn)
    cur = conn.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")
    names = {row[0] for row in cur.fetchall()}
    assert "memories" in names
    assert "memories_fts" in names
    assert "schema_version" in names


def test_schema_version_is_one(memory_dir):
    conn = connect()
    init_schema(conn)
    assert schema_version(conn) == 1


def test_insert_and_get_by_name(memory_dir):
    conn = connect()
    init_schema(conn)
    m = make_memory()
    new_id = insert_memory(conn, m)
    assert new_id > 0
    got = get_by_name(conn, "m1")
    assert got is not None
    assert got.name == "m1"
    assert got.tags == ["t1"]


def test_get_by_id(memory_dir):
    conn = connect()
    init_schema(conn)
    new_id = insert_memory(conn, make_memory())
    got = get_by_id(conn, new_id)
    assert got is not None
    assert got.id == new_id


def test_update_memory(memory_dir):
    conn = connect()
    init_schema(conn)
    new_id = insert_memory(conn, make_memory())
    update_memory(conn, new_id, {"description": "new"})
    got = get_by_id(conn, new_id)
    assert got.description == "new"


def test_delete_memory(memory_dir):
    conn = connect()
    init_schema(conn)
    new_id = insert_memory(conn, make_memory())
    delete_memory(conn, new_id)
    assert get_by_id(conn, new_id) is None


def test_list_all_filters_by_type(memory_dir):
    conn = connect()
    init_schema(conn)
    insert_memory(conn, make_memory("m1", "feedback"))
    insert_memory(conn, make_memory("m2", "project"))
    feedbacks = list_all(conn, type_="feedback")
    assert len(feedbacks) == 1
    assert feedbacks[0].name == "m1"


def test_insert_rejects_duplicate_name(memory_dir):
    conn = connect()
    init_schema(conn)
    insert_memory(conn, make_memory())
    try:
        insert_memory(conn, make_memory())
    except sqlite3.IntegrityError:
        return
    raise AssertionError("expected IntegrityError")


def test_fts_index_populated_on_insert(memory_dir):
    conn = connect()
    init_schema(conn)
    insert_memory(conn, make_memory())
    cur = conn.execute("SELECT name FROM memories_fts WHERE memories_fts MATCH 'm1'")
    rows = cur.fetchall()
    assert len(rows) == 1
```

- [ ] **Step 2: Run tests and confirm they fail**

Run: `pytest tests/test_db.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `claude_db_memory/db.py`**

```python
from __future__ import annotations

import json
import sqlite3
from typing import Any, Optional

from claude_db_memory.config import db_path, ensure_dirs
from claude_db_memory.models import Memory, validate_name, validate_type

SCHEMA_VERSION = 1

DDL = [
    """
    CREATE TABLE IF NOT EXISTS schema_version (version INTEGER PRIMARY KEY)
    """,
    """
    CREATE TABLE IF NOT EXISTS memories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        type TEXT NOT NULL CHECK (type IN ('user','feedback','project','reference','note')),
        description TEXT NOT NULL,
        body TEXT NOT NULL,
        tags TEXT NOT NULL DEFAULT '[]',
        project TEXT,
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        source_file TEXT NOT NULL
    )
    """,
    """
    CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
        name, description, body, tags, project,
        content='memories', content_rowid='id'
    )
    """,
    """
    CREATE TRIGGER IF NOT EXISTS memories_ai AFTER INSERT ON memories BEGIN
        INSERT INTO memories_fts(rowid, name, description, body, tags, project)
        VALUES (new.id, new.name, new.description, new.body, new.tags, new.project);
    END
    """,
    """
    CREATE TRIGGER IF NOT EXISTS memories_ad AFTER DELETE ON memories BEGIN
        INSERT INTO memories_fts(memories_fts, rowid, name, description, body, tags, project)
        VALUES ('delete', old.id, old.name, old.description, old.body, old.tags, old.project);
    END
    """,
    """
    CREATE TRIGGER IF NOT EXISTS memories_au AFTER UPDATE ON memories BEGIN
        INSERT INTO memories_fts(memories_fts, rowid, name, description, body, tags, project)
        VALUES ('delete', old.id, old.name, old.description, old.body, old.tags, old.project);
        INSERT INTO memories_fts(rowid, name, description, body, tags, project)
        VALUES (new.id, new.name, new.description, new.body, new.tags, new.project);
    END
    """,
]


def connect() -> sqlite3.Connection:
    ensure_dirs()
    conn = sqlite3.connect(db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    for stmt in DDL:
        conn.execute(stmt)
    cur = conn.execute("SELECT version FROM schema_version LIMIT 1")
    row = cur.fetchone()
    if row is None:
        conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
    conn.commit()


def schema_version(conn: sqlite3.Connection) -> int:
    cur = conn.execute("SELECT version FROM schema_version LIMIT 1")
    row = cur.fetchone()
    return int(row[0]) if row else 0


def _row_to_memory(row: sqlite3.Row) -> Memory:
    return Memory(
        id=row["id"],
        name=row["name"],
        type=row["type"],
        description=row["description"],
        body=row["body"],
        tags=json.loads(row["tags"]),
        project=row["project"],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
        source_file=row["source_file"],
    )


def insert_memory(conn: sqlite3.Connection, m: Memory) -> int:
    validate_name(m.name)
    validate_type(m.type)
    cur = conn.execute(
        """
        INSERT INTO memories
            (name, type, description, body, tags, project, created_at, updated_at, source_file)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            m.name, m.type, m.description, m.body,
            json.dumps(m.tags), m.project,
            m.created_at, m.updated_at, m.source_file,
        ),
    )
    conn.commit()
    return int(cur.lastrowid)


def update_memory(conn: sqlite3.Connection, id_: int, fields: dict[str, Any]) -> None:
    if not fields:
        return
    allowed = {"name", "type", "description", "body", "tags", "project", "updated_at", "source_file"}
    bad = set(fields) - allowed
    if bad:
        raise ValueError(f"Cannot update fields: {sorted(bad)}")
    if "name" in fields:
        validate_name(fields["name"])
    if "type" in fields:
        validate_type(fields["type"])
    if "tags" in fields:
        fields = {**fields, "tags": json.dumps(fields["tags"])}
    cols = ", ".join(f"{k} = ?" for k in fields)
    params = list(fields.values()) + [id_]
    conn.execute(f"UPDATE memories SET {cols} WHERE id = ?", params)
    conn.commit()


def delete_memory(conn: sqlite3.Connection, id_: int) -> None:
    conn.execute("DELETE FROM memories WHERE id = ?", (id_,))
    conn.commit()


def get_by_name(conn: sqlite3.Connection, name: str) -> Optional[Memory]:
    row = conn.execute("SELECT * FROM memories WHERE name = ?", (name,)).fetchone()
    return _row_to_memory(row) if row else None


def get_by_id(conn: sqlite3.Connection, id_: int) -> Optional[Memory]:
    row = conn.execute("SELECT * FROM memories WHERE id = ?", (id_,)).fetchone()
    return _row_to_memory(row) if row else None


def list_all(
    conn: sqlite3.Connection,
    type_: Optional[str] = None,
    project: Optional[str] = None,
    limit: int = 1000,
    offset: int = 0,
) -> list[Memory]:
    clauses, params = [], []
    if type_:
        clauses.append("type = ?")
        params.append(type_)
    if project:
        clauses.append("project = ?")
        params.append(project)
    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    params.extend([limit, offset])
    rows = conn.execute(
        f"SELECT * FROM memories {where} ORDER BY type, updated_at DESC LIMIT ? OFFSET ?",
        params,
    ).fetchall()
    return [_row_to_memory(r) for r in rows]
```

- [ ] **Step 4: Run tests and confirm they pass**

Run: `pytest tests/test_db.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add claude_db_memory/db.py tests/test_db.py
git commit -m "feat(db): SQLite schema with FTS5 and CRUD helpers"
```

---

### Task 6: `md_sync.py` — `.md` parse/serialize and `MEMORY.md` generation

**Files:**
- Create: `claude_db_memory/md_sync.py`
- Create: `tests/test_md_sync.py`

- [ ] **Step 1: Write failing tests**

`tests/test_md_sync.py`:

```python
from pathlib import Path

from claude_db_memory.md_sync import (
    serialize_memory,
    parse_md_file,
    write_md,
    delete_md,
    regenerate_index,
)
from claude_db_memory.models import Memory


def make_memory(name="m1", type_="feedback") -> Memory:
    return Memory(
        id=1, name=name, type=type_,
        description=f"desc for {name}", body="body content",
        tags=["a", "b"], project=None,
        created_at="2026-05-05T10:00:00", updated_at="2026-05-05T10:00:00",
        source_file=f"memories/{name}.md",
    )


def test_serialize_round_trip(tmp_path):
    m = make_memory()
    text = serialize_memory(m)
    f = tmp_path / "x.md"
    f.write_text(text)
    parsed = parse_md_file(f)
    assert parsed.name == m.name
    assert parsed.type == m.type
    assert parsed.description == m.description
    assert parsed.body.strip() == m.body.strip()
    assert parsed.tags == m.tags


def test_write_md_creates_file(memory_dir):
    m = make_memory()
    path = write_md(m)
    assert path.exists()
    assert path.name == "m1.md"


def test_delete_md_removes_file(memory_dir):
    m = make_memory()
    path = write_md(m)
    assert path.exists()
    delete_md(m.name)
    assert not path.exists()


def test_regenerate_index_groups_by_type(memory_dir):
    memories = [
        make_memory("m1", "feedback"),
        make_memory("m2", "project"),
        make_memory("m3", "feedback"),
    ]
    index_path = regenerate_index(memories)
    text = index_path.read_text()
    assert "## feedback" in text
    assert "## project" in text
    assert "[m1](memories/m1.md)" in text
    assert "[m2](memories/m2.md)" in text


def test_parse_md_file_handles_missing_optional_fields(tmp_path):
    content = '''---
name: simple
type: note
description: just a note
tags: []
project: null
created_at: 2026-05-05T10:00:00
updated_at: 2026-05-05T10:00:00
---

body
'''
    f = tmp_path / "simple.md"
    f.write_text(content)
    m = parse_md_file(f)
    assert m.tags == []
    assert m.project is None
```

- [ ] **Step 2: Run tests and confirm they fail**

Run: `pytest tests/test_md_sync.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `claude_db_memory/md_sync.py`**

```python
from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from claude_db_memory.config import index_path, md_dir, ensure_dirs
from claude_db_memory.models import Memory


def serialize_memory(m: Memory) -> str:
    fm = {
        "name": m.name,
        "type": m.type,
        "description": m.description,
        "tags": m.tags,
        "project": m.project,
        "created_at": m.created_at,
        "updated_at": m.updated_at,
    }
    fm_lines = ["---"]
    for k, v in fm.items():
        fm_lines.append(f"{k}: {json.dumps(v)}")
    fm_lines.append("---")
    return "\n".join(fm_lines) + "\n\n" + m.body.rstrip() + "\n"


def parse_md_file(path: Path) -> Memory:
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing frontmatter delimiter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path}: unterminated frontmatter")
    fm_block = text[4:end]
    body = text[end + 5 :].strip()
    fm: dict = {}
    for line in fm_block.splitlines():
        if not line.strip():
            continue
        key, _, raw = line.partition(":")
        fm[key.strip()] = json.loads(raw.strip())
    return Memory(
        id=None,
        name=fm["name"],
        type=fm["type"],
        description=fm["description"],
        body=body,
        tags=fm.get("tags", []),
        project=fm.get("project"),
        created_at=fm.get("created_at", ""),
        updated_at=fm.get("updated_at", ""),
        source_file=f"memories/{fm['name']}.md",
    )


def write_md(m: Memory) -> Path:
    ensure_dirs()
    path = md_dir() / f"{m.name}.md"
    path.write_text(serialize_memory(m))
    return path


def delete_md(name: str) -> None:
    path = md_dir() / f"{name}.md"
    if path.exists():
        path.unlink()


def regenerate_index(memories: Iterable[Memory]) -> Path:
    ensure_dirs()
    by_type: dict[str, list[Memory]] = {}
    for m in memories:
        by_type.setdefault(m.type, []).append(m)
    lines = ["# Memory Index", ""]
    for type_ in sorted(by_type):
        lines.append(f"## {type_}")
        items = sorted(by_type[type_], key=lambda x: x.updated_at, reverse=True)
        for m in items:
            lines.append(f"- [{m.name}](memories/{m.name}.md) — {m.description}")
        lines.append("")
    path = index_path()
    path.write_text("\n".join(lines))
    return path
```

- [ ] **Step 4: Run tests and confirm they pass**

Run: `pytest tests/test_md_sync.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add claude_db_memory/md_sync.py tests/test_md_sync.py
git commit -m "feat(md_sync): parse, write, and index Markdown memories"
```

---

## Phase 3 — Operations

Each operation file exposes a `main(args: dict) -> dict` callable used by both CLI and MCP. Operations open a fresh `db.connect()` per call, do their work, write/regenerate `.md` and index as needed, and return a dict.

### Task 7: `operations/add.py`

**Files:**
- Create: `claude_db_memory/operations/add.py`
- Create: `tests/test_add.py`

- [ ] **Step 1: Write failing tests**

`tests/test_add.py`:

```python
from claude_db_memory.operations.add import main
from claude_db_memory import db
from claude_db_memory.config import md_dir, index_path


def test_add_creates_db_row_md_and_index(memory_dir):
    result = main({
        "name": "feedback_commits",
        "type": "feedback",
        "description": "no git writes",
        "body": "User runs git",
        "tags": ["git"],
        "project": None,
    })
    assert result["name"] == "feedback_commits"
    assert result["id"] > 0

    conn = db.connect()
    db.init_schema(conn)
    got = db.get_by_name(conn, "feedback_commits")
    assert got is not None
    assert got.tags == ["git"]

    md_file = md_dir() / "feedback_commits.md"
    assert md_file.exists()

    idx = index_path().read_text()
    assert "feedback_commits" in idx


def test_add_rejects_duplicate(memory_dir):
    args = {
        "name": "x", "type": "note", "description": "d", "body": "b",
        "tags": [], "project": None,
    }
    main(args)
    try:
        main(args)
    except Exception:
        return
    raise AssertionError("expected duplicate to fail")
```

- [ ] **Step 2: Run tests and confirm they fail**

Run: `pytest tests/test_add.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `claude_db_memory/operations/add.py`**

```python
from __future__ import annotations

from datetime import datetime, timezone

from claude_db_memory import db
from claude_db_memory.md_sync import write_md, regenerate_index
from claude_db_memory.models import Memory


def main(args: dict) -> dict:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    m = Memory(
        id=None,
        name=args["name"],
        type=args["type"],
        description=args["description"],
        body=args["body"],
        tags=args.get("tags") or [],
        project=args.get("project"),
        created_at=now,
        updated_at=now,
        source_file=f"memories/{args['name']}.md",
    )
    conn = db.connect()
    db.init_schema(conn)
    new_id = db.insert_memory(conn, m)
    m.id = new_id
    write_md(m)
    regenerate_index(db.list_all(conn))
    return {"id": new_id, "name": m.name}
```

- [ ] **Step 4: Run tests and confirm they pass**

Run: `pytest tests/test_add.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add claude_db_memory/operations/add.py tests/test_add.py
git commit -m "feat(ops): add memory creates row, .md, and updates index"
```

---

### Task 8: `operations/get.py`

**Files:**
- Create: `claude_db_memory/operations/get.py`
- Create: `tests/test_get.py`

- [ ] **Step 1: Write failing tests**

`tests/test_get.py`:

```python
import pytest

from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.get import main


def test_get_by_name(memory_dir):
    add_main({"name": "n1", "type": "note", "description": "d", "body": "b",
              "tags": [], "project": None})
    res = main({"id_or_name": "n1"})
    assert res["name"] == "n1"
    assert res["body"] == "b"


def test_get_by_id(memory_dir):
    res_add = add_main({"name": "n2", "type": "note", "description": "d", "body": "b",
                        "tags": [], "project": None})
    res = main({"id_or_name": str(res_add["id"])})
    assert res["name"] == "n2"


def test_get_missing_raises(memory_dir):
    with pytest.raises(KeyError):
        main({"id_or_name": "does_not_exist"})
```

- [ ] **Step 2: Run tests and confirm they fail**

Run: `pytest tests/test_get.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `claude_db_memory/operations/get.py`**

```python
from __future__ import annotations

from dataclasses import asdict

from claude_db_memory import db


def main(args: dict) -> dict:
    key = args["id_or_name"]
    conn = db.connect()
    db.init_schema(conn)
    m = None
    if key.isdigit():
        m = db.get_by_id(conn, int(key))
    if m is None:
        m = db.get_by_name(conn, key)
    if m is None:
        raise KeyError(f"Memory not found: {key}")
    return asdict(m)
```

- [ ] **Step 4: Run tests and confirm they pass**

Run: `pytest tests/test_get.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add claude_db_memory/operations/get.py tests/test_get.py
git commit -m "feat(ops): get memory by id or name"
```

---

### Task 9: `operations/list_.py`

**Files:**
- Create: `claude_db_memory/operations/list_.py`
- Create: `tests/test_list.py`

- [ ] **Step 1: Write failing tests**

`tests/test_list.py`:

```python
from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.list_ import main


def seed(memory_dir):
    add_main({"name": "fb1", "type": "feedback", "description": "d", "body": "b",
              "tags": [], "project": "p1"})
    add_main({"name": "fb2", "type": "feedback", "description": "d", "body": "b",
              "tags": [], "project": "p2"})
    add_main({"name": "pr1", "type": "project", "description": "d", "body": "b",
              "tags": [], "project": "p1"})


def test_list_all(memory_dir):
    seed(memory_dir)
    res = main({})
    assert res["total"] == 3
    assert len(res["items"]) == 3


def test_list_filter_by_type(memory_dir):
    seed(memory_dir)
    res = main({"type": "feedback"})
    assert res["total"] == 2
    assert all(i["type"] == "feedback" for i in res["items"])


def test_list_filter_by_project(memory_dir):
    seed(memory_dir)
    res = main({"project": "p1"})
    assert res["total"] == 2


def test_list_pagination(memory_dir):
    seed(memory_dir)
    res = main({"limit": 1, "offset": 0})
    assert len(res["items"]) == 1
    assert res["total"] == 3
```

- [ ] **Step 2: Run tests and confirm they fail**

Run: `pytest tests/test_list.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `claude_db_memory/operations/list_.py`**

```python
from __future__ import annotations

from dataclasses import asdict

from claude_db_memory import db


def main(args: dict) -> dict:
    conn = db.connect()
    db.init_schema(conn)
    type_ = args.get("type")
    project = args.get("project")
    limit = int(args.get("limit") or 20)
    offset = int(args.get("offset") or 0)
    items = db.list_all(conn, type_=type_, project=project, limit=limit, offset=offset)
    total_rows = conn.execute(
        "SELECT COUNT(*) FROM memories WHERE (? IS NULL OR type = ?) AND (? IS NULL OR project = ?)",
        (type_, type_, project, project),
    ).fetchone()[0]
    return {"items": [asdict(m) for m in items], "total": int(total_rows)}
```

- [ ] **Step 4: Run tests and confirm they pass**

Run: `pytest tests/test_list.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add claude_db_memory/operations/list_.py tests/test_list.py
git commit -m "feat(ops): list memories with filters and pagination"
```

---

### Task 10: `operations/delete.py`

**Files:**
- Create: `claude_db_memory/operations/delete.py`
- Create: `tests/test_delete.py`

- [ ] **Step 1: Write failing tests**

`tests/test_delete.py`:

```python
import pytest

from claude_db_memory.config import md_dir
from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.delete import main


def test_delete_removes_row_and_md(memory_dir):
    add_main({"name": "d1", "type": "note", "description": "d", "body": "b",
              "tags": [], "project": None})
    md = md_dir() / "d1.md"
    assert md.exists()
    res = main({"id_or_name": "d1"})
    assert res["deleted"] is True
    assert not md.exists()


def test_delete_missing_raises(memory_dir):
    with pytest.raises(KeyError):
        main({"id_or_name": "missing"})
```

- [ ] **Step 2: Run tests and confirm they fail**

Run: `pytest tests/test_delete.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `claude_db_memory/operations/delete.py`**

```python
from __future__ import annotations

from claude_db_memory import db
from claude_db_memory.md_sync import delete_md, regenerate_index


def main(args: dict) -> dict:
    key = args["id_or_name"]
    conn = db.connect()
    db.init_schema(conn)
    m = None
    if key.isdigit():
        m = db.get_by_id(conn, int(key))
    if m is None:
        m = db.get_by_name(conn, key)
    if m is None:
        raise KeyError(f"Memory not found: {key}")
    db.delete_memory(conn, m.id)
    delete_md(m.name)
    regenerate_index(db.list_all(conn))
    return {"deleted": True, "name": m.name}
```

- [ ] **Step 4: Run tests and confirm they pass**

Run: `pytest tests/test_delete.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add claude_db_memory/operations/delete.py tests/test_delete.py
git commit -m "feat(ops): delete memory removes row, .md, and reindex"
```

---

### Task 11: `operations/search.py`

**Files:**
- Create: `claude_db_memory/operations/search.py`
- Create: `tests/test_search.py`

- [ ] **Step 1: Write failing tests**

`tests/test_search.py`:

```python
from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.search import main


def seed():
    add_main({"name": "feedback_commits", "type": "feedback",
              "description": "Never run git writes",
              "body": "User runs git operations themselves",
              "tags": ["git"], "project": None})
    add_main({"name": "project_tramita", "type": "project",
              "description": "Tramita lives in tramita-web",
              "body": "Frontend module is in tramita-web repo",
              "tags": ["frontend"], "project": "tramita"})


def test_search_finds_by_body_term(memory_dir):
    seed()
    res = main({"query": "git"})
    names = {r["name"] for r in res["items"]}
    assert "feedback_commits" in names


def test_search_finds_by_description(memory_dir):
    seed()
    res = main({"query": "tramita"})
    names = {r["name"] for r in res["items"]}
    assert "project_tramita" in names


def test_search_filter_by_type(memory_dir):
    seed()
    res = main({"query": "tramita", "type": "feedback"})
    assert res["items"] == []


def test_search_returns_snippet(memory_dir):
    seed()
    res = main({"query": "git"})
    assert res["items"][0]["snippet"]
```

- [ ] **Step 2: Run tests and confirm they fail**

Run: `pytest tests/test_search.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `claude_db_memory/operations/search.py`**

```python
from __future__ import annotations

from claude_db_memory import db


def main(args: dict) -> dict:
    query = args["query"]
    type_ = args.get("type")
    project = args.get("project")
    limit = int(args.get("limit") or 10)
    conn = db.connect()
    db.init_schema(conn)
    sql = """
        SELECT m.id, m.name, m.type, m.description, m.project,
               snippet(memories_fts, -1, '[', ']', '...', 10) AS snippet,
               bm25(memories_fts) AS score
        FROM memories_fts
        JOIN memories m ON m.id = memories_fts.rowid
        WHERE memories_fts MATCH ?
    """
    params: list = [query]
    if type_:
        sql += " AND m.type = ?"
        params.append(type_)
    if project:
        sql += " AND m.project = ?"
        params.append(project)
    sql += " ORDER BY score LIMIT ?"
    params.append(limit)
    rows = conn.execute(sql, params).fetchall()
    items = [
        {
            "id": r["id"], "name": r["name"], "type": r["type"],
            "description": r["description"], "project": r["project"],
            "snippet": r["snippet"], "score": r["score"],
        }
        for r in rows
    ]
    return {"items": items}
```

- [ ] **Step 4: Run tests and confirm they pass**

Run: `pytest tests/test_search.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add claude_db_memory/operations/search.py tests/test_search.py
git commit -m "feat(ops): full-text search via FTS5 with snippet and bm25 ranking"
```

---

### Task 12: `operations/update.py`

**Files:**
- Create: `claude_db_memory/operations/update.py`
- Create: `tests/test_update.py`

- [ ] **Step 1: Write failing tests**

`tests/test_update.py`:

```python
import pytest

from claude_db_memory.config import md_dir
from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.update import main


def test_update_changes_description_and_md(memory_dir):
    add_main({"name": "u1", "type": "note", "description": "old", "body": "b",
              "tags": [], "project": None})
    res = main({"id_or_name": "u1", "fields": {"description": "new"}})
    assert res["description"] == "new"
    md = (md_dir() / "u1.md").read_text()
    assert "new" in md


def test_update_missing_raises(memory_dir):
    with pytest.raises(KeyError):
        main({"id_or_name": "missing", "fields": {"description": "x"}})


def test_update_rejects_unknown_field(memory_dir):
    add_main({"name": "u2", "type": "note", "description": "d", "body": "b",
              "tags": [], "project": None})
    with pytest.raises(ValueError):
        main({"id_or_name": "u2", "fields": {"unknown_field": "x"}})
```

- [ ] **Step 2: Run tests and confirm they fail**

Run: `pytest tests/test_update.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `claude_db_memory/operations/update.py`**

```python
from __future__ import annotations

from dataclasses import asdict
from datetime import datetime, timezone

from claude_db_memory import db
from claude_db_memory.md_sync import write_md, regenerate_index


def main(args: dict) -> dict:
    key = args["id_or_name"]
    fields = dict(args["fields"])
    fields["updated_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    conn = db.connect()
    db.init_schema(conn)
    m = None
    if key.isdigit():
        m = db.get_by_id(conn, int(key))
    if m is None:
        m = db.get_by_name(conn, key)
    if m is None:
        raise KeyError(f"Memory not found: {key}")
    db.update_memory(conn, m.id, fields)
    updated = db.get_by_id(conn, m.id)
    write_md(updated)
    regenerate_index(db.list_all(conn))
    return asdict(updated)
```

- [ ] **Step 4: Run tests and confirm they pass**

Run: `pytest tests/test_update.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add claude_db_memory/operations/update.py tests/test_update.py
git commit -m "feat(ops): update memory with field validation and reindex"
```

---

### Task 13: `operations/reindex.py`

**Files:**
- Create: `claude_db_memory/operations/reindex.py`
- Create: `tests/test_reindex.py`

- [ ] **Step 1: Write failing tests**

`tests/test_reindex.py`:

```python
from claude_db_memory.config import db_path
from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.reindex import main
from claude_db_memory import db


def test_reindex_rebuilds_db_from_md(memory_dir):
    add_main({"name": "r1", "type": "note", "description": "d", "body": "b",
              "tags": [], "project": None})
    add_main({"name": "r2", "type": "note", "description": "d", "body": "b",
              "tags": [], "project": None})
    db_path().unlink()
    res = main({})
    assert res["rebuilt"] == 2
    conn = db.connect()
    db.init_schema(conn)
    assert db.get_by_name(conn, "r1") is not None
    assert db.get_by_name(conn, "r2") is not None


def test_reindex_reports_errors(memory_dir):
    from claude_db_memory.config import md_dir
    bad = md_dir()
    bad.mkdir(parents=True, exist_ok=True)
    (bad / "broken.md").write_text("not a valid frontmatter file")
    res = main({})
    assert res["rebuilt"] == 0
    assert len(res["errors"]) == 1
```

- [ ] **Step 2: Run tests and confirm they fail**

Run: `pytest tests/test_reindex.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `claude_db_memory/operations/reindex.py`**

```python
from __future__ import annotations

from claude_db_memory import db
from claude_db_memory.config import db_path, md_dir
from claude_db_memory.md_sync import parse_md_file, regenerate_index


def main(args: dict) -> dict:
    if db_path().exists():
        db_path().unlink()
    conn = db.connect()
    db.init_schema(conn)
    rebuilt = 0
    errors: list[dict] = []
    for path in sorted(md_dir().glob("*.md")):
        try:
            m = parse_md_file(path)
            db.insert_memory(conn, m)
            rebuilt += 1
        except Exception as exc:
            errors.append({"file": str(path), "error": str(exc)})
    regenerate_index(db.list_all(conn))
    return {"rebuilt": rebuilt, "errors": errors}
```

- [ ] **Step 4: Run tests and confirm they pass**

Run: `pytest tests/test_reindex.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add claude_db_memory/operations/reindex.py tests/test_reindex.py
git commit -m "feat(ops): reindex rebuilds SQLite from .md files"
```

---

### Task 14: `operations/verify.py`

**Files:**
- Create: `claude_db_memory/operations/verify.py`
- Create: `tests/test_verify.py`

- [ ] **Step 1: Write failing tests**

`tests/test_verify.py`:

```python
from claude_db_memory.config import md_dir
from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.verify import main


def test_verify_clean(memory_dir):
    add_main({"name": "v1", "type": "note", "description": "d", "body": "b",
              "tags": [], "project": None})
    res = main({})
    assert res["orphan_rows"] == []
    assert res["orphan_files"] == []
    assert res["drift"] == []


def test_verify_detects_orphan_row(memory_dir):
    add_main({"name": "v1", "type": "note", "description": "d", "body": "b",
              "tags": [], "project": None})
    (md_dir() / "v1.md").unlink()
    res = main({})
    assert "v1" in res["orphan_rows"]


def test_verify_detects_orphan_file(memory_dir):
    md_dir().mkdir(parents=True, exist_ok=True)
    (md_dir() / "ghost.md").write_text(
        '---\nname: "ghost"\ntype: "note"\ndescription: "x"\n'
        'tags: []\nproject: null\ncreated_at: "2026-05-05T10:00:00"\n'
        'updated_at: "2026-05-05T10:00:00"\n---\n\nbody\n'
    )
    res = main({})
    assert "ghost" in res["orphan_files"]


def test_verify_detects_drift(memory_dir):
    add_main({"name": "v1", "type": "note", "description": "old", "body": "b",
              "tags": [], "project": None})
    md = md_dir() / "v1.md"
    md.write_text(md.read_text().replace("old", "changed"))
    res = main({})
    assert "v1" in res["drift"]
```

- [ ] **Step 2: Run tests and confirm they fail**

Run: `pytest tests/test_verify.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `claude_db_memory/operations/verify.py`**

```python
from __future__ import annotations

from claude_db_memory import db
from claude_db_memory.config import md_dir
from claude_db_memory.md_sync import parse_md_file


def main(args: dict) -> dict:
    conn = db.connect()
    db.init_schema(conn)
    rows = {m.name: m for m in db.list_all(conn, limit=10**9)}
    files = {p.stem: p for p in md_dir().glob("*.md")} if md_dir().exists() else {}
    orphan_rows = sorted(set(rows) - set(files))
    orphan_files = sorted(set(files) - set(rows))
    drift: list[str] = []
    for name in set(rows) & set(files):
        try:
            file_mem = parse_md_file(files[name])
        except Exception:
            drift.append(name)
            continue
        row = rows[name]
        if (row.description != file_mem.description
                or row.body.strip() != file_mem.body.strip()
                or row.type != file_mem.type
                or row.tags != file_mem.tags
                or row.project != file_mem.project):
            drift.append(name)
    return {"orphan_rows": orphan_rows, "orphan_files": orphan_files, "drift": sorted(drift)}
```

- [ ] **Step 4: Run tests and confirm they pass**

Run: `pytest tests/test_verify.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add claude_db_memory/operations/verify.py tests/test_verify.py
git commit -m "feat(ops): verify reports orphans and drift between .md and DB"
```

---

### Task 15: `operations/export.py`

**Files:**
- Create: `claude_db_memory/operations/export.py`
- Create: `tests/test_export.py`

- [ ] **Step 1: Write failing tests**

`tests/test_export.py`:

```python
from claude_db_memory.config import md_dir, index_path
from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.export import main


def test_export_writes_md_for_all_rows(memory_dir):
    add_main({"name": "e1", "type": "note", "description": "d", "body": "b",
              "tags": [], "project": None})
    add_main({"name": "e2", "type": "note", "description": "d", "body": "b",
              "tags": [], "project": None})
    (md_dir() / "e1.md").unlink()
    res = main({})
    assert res["exported"] == 2
    assert (md_dir() / "e1.md").exists()
    assert (md_dir() / "e2.md").exists()
    assert index_path().exists()
```

- [ ] **Step 2: Run tests and confirm they fail**

Run: `pytest tests/test_export.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `claude_db_memory/operations/export.py`**

```python
from __future__ import annotations

from claude_db_memory import db
from claude_db_memory.md_sync import write_md, regenerate_index


def main(args: dict) -> dict:
    conn = db.connect()
    db.init_schema(conn)
    memories = db.list_all(conn, limit=10**9)
    for m in memories:
        write_md(m)
    regenerate_index(memories)
    return {"exported": len(memories)}
```

- [ ] **Step 4: Run tests and confirm they pass**

Run: `pytest tests/test_export.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add claude_db_memory/operations/export.py tests/test_export.py
git commit -m "feat(ops): export forces .md regeneration from DB"
```

---

## Phase 4 — Entry points

### Task 16: `cli.py` — argparse dispatcher

**Files:**
- Create: `claude_db_memory/cli.py`
- Create: `tests/test_cli.py`

- [ ] **Step 1: Write failing tests**

`tests/test_cli.py`:

```python
import json

from claude_db_memory.cli import main as cli_main


def test_cli_add_then_get(memory_dir, capsys):
    rc = cli_main([
        "add", "--name", "c1", "--type", "note",
        "--description", "d", "--body", "b", "--json",
    ])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["name"] == "c1"

    rc = cli_main(["get", "c1", "--json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["name"] == "c1"


def test_cli_search(memory_dir, capsys):
    cli_main(["add", "--name", "c2", "--type", "note",
              "--description", "find me here", "--body", "b"])
    capsys.readouterr()
    rc = cli_main(["search", "find me", "--json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert any(i["name"] == "c2" for i in out["items"])


def test_cli_list(memory_dir, capsys):
    cli_main(["add", "--name", "l1", "--type", "feedback",
              "--description", "d", "--body", "b"])
    capsys.readouterr()
    rc = cli_main(["list", "--json"])
    assert rc == 0
    out = json.loads(capsys.readouterr().out)
    assert out["total"] == 1


def test_cli_delete(memory_dir, capsys):
    cli_main(["add", "--name", "d1", "--type", "note",
              "--description", "d", "--body", "b"])
    capsys.readouterr()
    rc = cli_main(["delete", "d1", "--json"])
    assert rc == 0


def test_cli_unknown_command_returns_nonzero():
    rc = cli_main(["bogus"])
    assert rc != 0
```

- [ ] **Step 2: Run tests and confirm they fail**

Run: `pytest tests/test_cli.py -v`
Expected: FAIL with `ModuleNotFoundError`.

- [ ] **Step 3: Implement `claude_db_memory/cli.py`**

```python
from __future__ import annotations

import argparse
import json
import sys

from claude_db_memory.operations import (
    add as add_op,
    delete as delete_op,
    export as export_op,
    get as get_op,
    list_ as list_op,
    reindex as reindex_op,
    search as search_op,
    update as update_op,
    verify as verify_op,
)


def _parse_tags(raw: str | None) -> list[str]:
    if not raw:
        return []
    return [t.strip() for t in raw.split(",") if t.strip()]


def _emit(result: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result, indent=2))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="memory")
    p.add_argument("--json", action="store_true", help="Output JSON")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("add")
    a.add_argument("--name", required=True)
    a.add_argument("--type", required=True)
    a.add_argument("--description", required=True)
    a.add_argument("--body", required=True)
    a.add_argument("--tags", default=None, help="comma-separated")
    a.add_argument("--project", default=None)

    g = sub.add_parser("get")
    g.add_argument("id_or_name")

    l = sub.add_parser("list")
    l.add_argument("--type", default=None)
    l.add_argument("--project", default=None)
    l.add_argument("--limit", type=int, default=20)
    l.add_argument("--offset", type=int, default=0)

    d = sub.add_parser("delete")
    d.add_argument("id_or_name")

    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--type", default=None)
    s.add_argument("--project", default=None)
    s.add_argument("--limit", type=int, default=10)

    u = sub.add_parser("update")
    u.add_argument("id_or_name")
    u.add_argument("--description", default=None)
    u.add_argument("--body", default=None)
    u.add_argument("--tags", default=None)
    u.add_argument("--project", default=None)
    u.add_argument("--type", default=None)

    sub.add_parser("reindex")

    v = sub.add_parser("verify")
    v.add_argument("--fix", action="store_true")

    sub.add_parser("export")
    return p


def _dispatch(ns: argparse.Namespace) -> dict:
    if ns.cmd == "add":
        return add_op.main({
            "name": ns.name, "type": ns.type,
            "description": ns.description, "body": ns.body,
            "tags": _parse_tags(ns.tags), "project": ns.project,
        })
    if ns.cmd == "get":
        return get_op.main({"id_or_name": ns.id_or_name})
    if ns.cmd == "list":
        return list_op.main({
            "type": ns.type, "project": ns.project,
            "limit": ns.limit, "offset": ns.offset,
        })
    if ns.cmd == "delete":
        return delete_op.main({"id_or_name": ns.id_or_name})
    if ns.cmd == "search":
        return search_op.main({
            "query": ns.query, "type": ns.type,
            "project": ns.project, "limit": ns.limit,
        })
    if ns.cmd == "update":
        fields: dict = {}
        for k in ("description", "body", "project", "type"):
            v = getattr(ns, k)
            if v is not None:
                fields[k] = v
        if ns.tags is not None:
            fields["tags"] = _parse_tags(ns.tags)
        return update_op.main({"id_or_name": ns.id_or_name, "fields": fields})
    if ns.cmd == "reindex":
        return reindex_op.main({})
    if ns.cmd == "verify":
        return verify_op.main({})
    if ns.cmd == "export":
        return export_op.main({})
    raise SystemExit(2)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        ns = parser.parse_args(argv)
    except SystemExit as exc:
        return int(exc.code) if isinstance(exc.code, int) else 2
    try:
        result = _dispatch(ns)
    except KeyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    _emit(result, getattr(ns, "json", False))
    return 0
```

- [ ] **Step 4: Run tests and confirm they pass**

Run: `pytest tests/test_cli.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add claude_db_memory/cli.py tests/test_cli.py
git commit -m "feat(cli): argparse dispatcher for memory subcommands"
```

---

### Task 17: `mcp_server.py` — MCP wrapper

**Files:**
- Create: `mcp_server.py`
- Create: `tests/test_mcp_server.py`

- [ ] **Step 1: Write failing test (in-process tool dispatch)**

`tests/test_mcp_server.py`:

```python
import importlib


def test_mcp_module_exposes_tool_handlers(memory_dir):
    mod = importlib.import_module("mcp_server")
    assert callable(mod.tool_add_memory)
    assert callable(mod.tool_search_memory)
    assert callable(mod.tool_get_memory)
    assert callable(mod.tool_update_memory)
    assert callable(mod.tool_delete_memory)
    assert callable(mod.tool_list_memories)
    assert callable(mod.tool_reindex)
    assert callable(mod.tool_verify)


def test_tool_add_then_search(memory_dir):
    mod = importlib.import_module("mcp_server")
    mod.tool_add_memory(
        name="m1", type="note", description="findable text", body="b",
        tags=[], project=None,
    )
    res = mod.tool_search_memory(query="findable")
    assert any(item["name"] == "m1" for item in res["items"])
```

- [ ] **Step 2: Run test and confirm it fails**

Run: `pytest tests/test_mcp_server.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'mcp_server'`.

- [ ] **Step 3: Implement `mcp_server.py`**

```python
"""MCP server entry point. Exposes claude_db_memory operations as MCP tools."""
from __future__ import annotations

from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

from claude_db_memory.operations import (
    add as add_op,
    delete as delete_op,
    get as get_op,
    list_ as list_op,
    reindex as reindex_op,
    search as search_op,
    update as update_op,
    verify as verify_op,
)

app = FastMCP("claude-db-memory")


@app.tool()
def tool_add_memory(
    name: str, type: str, description: str, body: str,
    tags: Optional[list[str]] = None, project: Optional[str] = None,
) -> dict[str, Any]:
    return add_op.main({
        "name": name, "type": type, "description": description, "body": body,
        "tags": tags or [], "project": project,
    })


@app.tool()
def tool_search_memory(
    query: str, type: Optional[str] = None,
    project: Optional[str] = None, limit: int = 10,
) -> dict[str, Any]:
    return search_op.main({
        "query": query, "type": type, "project": project, "limit": limit,
    })


@app.tool()
def tool_get_memory(id_or_name: str) -> dict[str, Any]:
    return get_op.main({"id_or_name": id_or_name})


@app.tool()
def tool_update_memory(id_or_name: str, fields: dict[str, Any]) -> dict[str, Any]:
    return update_op.main({"id_or_name": id_or_name, "fields": fields})


@app.tool()
def tool_delete_memory(id_or_name: str) -> dict[str, Any]:
    return delete_op.main({"id_or_name": id_or_name})


@app.tool()
def tool_list_memories(
    type: Optional[str] = None, project: Optional[str] = None,
    limit: int = 20, offset: int = 0,
) -> dict[str, Any]:
    return list_op.main({
        "type": type, "project": project, "limit": limit, "offset": offset,
    })


@app.tool()
def tool_reindex() -> dict[str, Any]:
    return reindex_op.main({})


@app.tool()
def tool_verify() -> dict[str, Any]:
    return verify_op.main({})


if __name__ == "__main__":
    app.run()
```

- [ ] **Step 4: Run tests and confirm they pass**

Run: `pytest tests/test_mcp_server.py -v`
Expected: PASS

- [ ] **Step 5: Run full suite to catch regressions**

Run: `pytest -v`
Expected: All tests pass.

- [ ] **Step 6: Commit**

```bash
git add mcp_server.py tests/test_mcp_server.py
git commit -m "feat(mcp): expose operations as MCP tools via FastMCP"
```

---

## Phase 5 — Plugin packaging

### Task 18: Plugin manifest and README

**Files:**
- Create: `.claude-plugin/plugin.json`
- Modify: `README.md`

- [ ] **Step 1: Create plugin manifest**

`.claude-plugin/plugin.json`:

```json
{
  "name": "claude-db-memory",
  "version": "0.1.0",
  "description": "SQLite-backed long-term memory for Claude Code with FTS5 search and Markdown backup",
  "license": "MIT",
  "mcpServers": {
    "claude-db-memory": {
      "command": "python3",
      "args": ["${CLAUDE_PLUGIN_ROOT}/mcp_server.py"]
    }
  }
}
```

- [ ] **Step 2: Replace README with full docs**

Overwrite `README.md`:

````markdown
# claude-db-memory

SQLite-backed long-term memory for Claude Code with FTS5 search and Markdown backup.

## Why

Claude Code's native memory stores entries as Markdown files indexed by `MEMORY.md`, which is auto-loaded into the system prompt at session start. The index is truncated after ~200 lines, so memories silently disappear past that limit. There is no search, no filtering, and no scaling beyond a few dozen entries.

`claude-db-memory` keeps the auto-loaded `MEMORY.md` compatibility but moves the source of truth to a local SQLite database with FTS5 full-text search. Markdown files become a versionable backup layer that can recover the database at any time.

## Install

### As a Claude Code plugin

```bash
/plugin install github:<your-user>/claude-db-memory
```

### Manual

```bash
git clone https://github.com/<your-user>/claude-db-memory ~/.claude/plugins/claude-db-memory
cd ~/.claude/plugins/claude-db-memory
pip install -e .
```

Claude Code reads `.claude-plugin/plugin.json` and registers the MCP server automatically.

## CLI

```bash
memory add --type feedback --name commits --description "..." --body "..."
memory search "tramita"
memory list --type feedback
memory get commits
memory update commits --description "new"
memory delete commits
memory reindex
memory verify
memory export
```

Add `--json` to any command for machine-readable output.

## MCP tools

The plugin exposes these tools to Claude Code:

- `tool_add_memory`
- `tool_search_memory`
- `tool_get_memory`
- `tool_update_memory`
- `tool_delete_memory`
- `tool_list_memories`
- `tool_reindex`
- `tool_verify`

## Storage

By default the plugin stores data per workspace at:

```
~/.claude/projects/<workspace>/memory/
├── MEMORY.md            # auto-generated index, auto-loaded by Claude Code
├── memory.db            # SQLite, gitignored
└── memories/            # .md backup
```

Override with `CLAUDE_DB_MEMORY_DIR=/path/to/dir` for a global memory shared across workspaces.

## Development

```bash
pip install -e ".[dev]"
pytest
```

## License

MIT.
````

- [ ] **Step 3: Commit**

```bash
git add .claude-plugin/plugin.json README.md
git commit -m "feat(plugin): plugin manifest and README"
```

---

### Task 19: End-to-end smoke test

**Files:** none (manual verification).

- [ ] **Step 1: Install package locally**

```bash
pip install -e ".[dev]"
```

Expected: install succeeds.

- [ ] **Step 2: Run full test suite**

```bash
pytest -v
```

Expected: all tests pass.

- [ ] **Step 3: Smoke-test the CLI in a temp directory**

```bash
mkdir /tmp/claude-db-memory-smoke
cd /tmp/claude-db-memory-smoke
export CLAUDE_DB_MEMORY_DIR=/tmp/claude-db-memory-smoke/mem
memory add --type note --name hello --description "hi" --body "world"
memory list
memory search hi
memory get hello
memory delete hello
memory list
unset CLAUDE_DB_MEMORY_DIR
```

Expected:
- `add` returns the new id.
- `list` shows one row, then zero after delete.
- `search hi` finds the entry.
- `get hello` prints the full row.
- `delete` succeeds.

- [ ] **Step 4: Smoke-test the MCP server starts**

```bash
python3 mcp_server.py < /dev/null &
PID=$!
sleep 1
kill $PID
```

Expected: process starts and exits cleanly when killed (no crash).

- [ ] **Step 5: No commit needed (verification only)**

---

### Task 20: Release prep — CHANGELOG and version bump

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Update CHANGELOG**

Replace `CHANGELOG.md`:

```markdown
# Changelog

## [0.1.0] - 2026-05-05

### Added
- Initial release.
- SQLite + FTS5 backed memory store.
- MCP tools: add, search, get, update, delete, list, reindex, verify.
- CLI: `memory` with subcommands matching MCP tools, plus `export`.
- Markdown backup layer with auto-regenerated `MEMORY.md` index.
- Per-workspace storage by default; override via `CLAUDE_DB_MEMORY_DIR`.
- Claude Code plugin manifest at `.claude-plugin/plugin.json`.
- GitHub Actions CI on Python 3.9–3.12.
```

- [ ] **Step 2: Tag release**

```bash
git add CHANGELOG.md
git commit -m "chore: prepare 0.1.0 release"
git tag v0.1.0
```

Expected: tag created locally. (User pushes to GitHub when ready; not part of this plan.)

---

## Self-review

**Spec coverage check:**

| Spec section | Covered by |
|---|---|
| §5 Architecture | Tasks 5-17 (lib + ops + entry points) |
| §6 Data model | Task 5 (`db.py`), Task 4 (`models.py`) |
| §7 API surface (MCP + CLI) | Tasks 7-17 |
| §8 File layout | Task 1 (scaffolding) |
| §9 Storage layout | Task 3 (`config.py`) |
| §10 Sync mechanics — write path | Tasks 7, 12 |
| §10 Sync mechanics — delete | Task 10 |
| §10 Sync mechanics — reindex | Task 13 |
| §10 Sync mechanics — verify | Task 14 |
| §10 Sync mechanics — MEMORY.md regen | Task 6 (`md_sync.py`) |
| §11 Plugin manifest | Task 18 |
| §12 Configuration (env vars) | Task 3 (`config.py`) |
| §13 Testing strategy | Tasks 2 (CI) + every task has tests |
| §15 Open questions — manifest format | Flagged in Task 18 (verify against current docs at impl time) |

**Deviations from spec:**
- `mcp` package added as runtime dependency (spec's "zero non-stdlib runtime deps" was unrealistic for an MCP server). Documented in plan header.
- `verify --fix` is parsed by CLI but does not yet apply fixes in v0.1.0; the underlying `verify` operation reports drift only. A follow-up task in v0.2 should implement the fix path. (Spec §10 verify --fix.)
- `CLAUDE_DB_MEMORY_INDEX_LIMIT` and `CLAUDE_DB_MEMORY_FTS_RANK` env vars from spec §12 are not implemented in v0.1.0 — index size is unbounded, ranking is BM25 by default. Noted as future work; not blocking.

**Type consistency check:**
- `Memory` dataclass fields used identically across `db.py`, `md_sync.py`, and all `operations/*.py`.
- `main(args: dict) -> dict` signature consistent across all `operations/*.py`.
- MCP tools use `Optional[str]`, `Optional[list[str]]` consistently.
- CLI flag names (`--type`, `--project`, `--description`, `--body`, `--tags`) consistent across subcommands that use them.
