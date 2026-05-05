from __future__ import annotations

from typing import Any

from claude_db_memory import db
from claude_db_memory.md_sync import write_md, regenerate_index


def main(args: dict[str, Any]) -> dict[str, Any]:
    conn = db.connect()
    memories = db.list_all(conn, limit=10**9)
    for m in memories:
        write_md(m)
    regenerate_index(memories)
    return {"exported": len(memories)}
