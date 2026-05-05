from claude_db_memory.operations.add import main as add_main
from claude_db_memory.operations.list_ import main


def seed(memory_dir):
    add_main(
        {
            "name": "fb1",
            "type": "feedback",
            "description": "d",
            "body": "b",
            "tags": [],
            "project": "p1",
        }
    )
    add_main(
        {
            "name": "fb2",
            "type": "feedback",
            "description": "d",
            "body": "b",
            "tags": [],
            "project": "p2",
        }
    )
    add_main(
        {
            "name": "pr1",
            "type": "project",
            "description": "d",
            "body": "b",
            "tags": [],
            "project": "p1",
        }
    )


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
