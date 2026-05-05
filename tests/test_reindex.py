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
