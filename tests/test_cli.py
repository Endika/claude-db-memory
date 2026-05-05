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
