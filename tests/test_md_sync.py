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
