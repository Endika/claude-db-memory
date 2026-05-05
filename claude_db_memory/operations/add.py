from __future__ import annotations

from datetime import datetime, timezone

from claude_db_memory import db
from claude_db_memory.md_sync import write_md, regenerate_index
from claude_db_memory.models import Memory


def main(args: dict) -> dict:
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
    db.init_schema(conn)
    new_id = db.insert_memory(conn, m)
    m.id = new_id
    write_md(m)
    regenerate_index(db.list_all(conn))
    return {"id": new_id, "name": m.name}
