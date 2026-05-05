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


def _make_spy(fn):
    def spy(*args, **kwargs):
        spy.last_args = args
        spy.last_kwargs = kwargs
        return fn(*args, **kwargs)

    spy.last_args = ()
    spy.last_kwargs = {}
    return spy


def test_index_regeneration_does_not_truncate(memory_dir, monkeypatch):
    """Adding more than the default list_all limit (1000) must not truncate the index."""
    from claude_db_memory import db as db_mod

    spy = _make_spy(db_mod.list_all)
    monkeypatch.setattr(db_mod, "list_all", spy)

    main({"name": "x1", "type": "note", "description": "d", "body": "b", "tags": [], "project": None})

    assert spy.last_kwargs.get("limit"), (
        "add.py must pass an explicit limit to list_all when regenerating the index"
    )
    assert spy.last_kwargs["limit"] >= 10**6, (
        f"limit must be effectively unbounded; got {spy.last_kwargs['limit']}"
    )
