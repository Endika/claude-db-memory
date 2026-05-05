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
