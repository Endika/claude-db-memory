from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from claude_db_memory import db
from claude_db_memory.md_sync import regenerate_index, write_md
from claude_db_memory.models import Memory


def main(args: dict[str, Any]) -> dict[str, Any]:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    m = Memory(
        id=None,
        name=args["name"],
        type=args["type"],
        description=args["description"],
        body=args["body"],
        tags=args.get("tags") or [],
        project=args.get("project"),
        created_at=now,
        updated_at=now,
        source_file=f"memories/{args['name']}.md",
    )
    conn = db.connect()
    new_id = db.insert_memory(conn, m)
    m.id = new_id
    write_md(m)
    regenerate_index(db.list_all(conn, limit=10**9))
    return {"id": new_id, "name": m.name}
