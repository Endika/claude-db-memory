from claude_db_memory.config import md_dir
from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.verify import main


def test_verify_clean(memory_dir):
    add_main(
        {"name": "v1", "type": "note", "description": "d", "body": "b", "tags": [], "project": None}
    )
    res = main({})
    assert res["orphan_rows"] == []
    assert res["orphan_files"] == []
    assert res["drift"] == []


def test_verify_detects_orphan_row(memory_dir):
    add_main(
        {"name": "v1", "type": "note", "description": "d", "body": "b", "tags": [], "project": None}
    )
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
    add_main(
        {
            "name": "v1",
            "type": "note",
            "description": "old",
            "body": "b",
            "tags": [],
            "project": None,
        }
    )
    md = md_dir() / "v1.md"
    md.write_text(md.read_text().replace("old", "changed"))
    res = main({})
    assert "v1" in res["drift"]


def test_verify_fix_flag_returns_not_implemented_note(memory_dir):
    add_main(
        {"name": "v1", "type": "note", "description": "old", "body": "b", "tags": [], "project": None}
    )
    md = md_dir() / "v1.md"
    md.write_text(md.read_text().replace("old", "changed"))
    res = main({"fix": True})
    assert "v1" in res["drift"]
    assert res["fix_applied"] is False
    assert "not yet implemented" in res["fix_note"]


def test_verify_no_fix_flag_does_not_include_fix_note(memory_dir):
    add_main(
        {"name": "v1", "type": "note", "description": "d", "body": "b", "tags": [], "project": None}
    )
    res = main({})
    assert "fix_note" not in res
    assert "fix_applied" not in res
