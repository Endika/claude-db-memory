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
