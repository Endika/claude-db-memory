from __future__ import annotations

from typing import Any

from claude_db_memory import db
from claude_db_memory.config import db_path, md_dir
from claude_db_memory.md_sync import parse_md_file, regenerate_index


def main(args: dict[str, Any]) -> dict[str, Any]:
    if db_path().exists():
        db_path().unlink()
    db._schema_initialized.pop(str(db_path()), None)
    conn = db.connect()
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
