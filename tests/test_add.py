from claude_db_memory import db
from claude_db_memory.config import index_path, md_dir
from claude_db_memory.operations.add import main


def test_add_creates_db_row_md_and_index(memory_dir):
    result = main(
        {
            "name": "feedback_commits",
            "type": "feedback",
            "description": "no git writes",
            "body": "User runs git",
            "tags": ["git"],
            "project": None,
        }
    )
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
        "name": "x",
        "type": "note",
        "description": "d",
        "body": "b",
        "tags": [],
        "project": None,
    }
    main(args)
    try:
        main(args)
    except Exception:
        return
    raise AssertionError("expected duplicate to fail")
