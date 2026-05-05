from __future__ import annotations

from typing import Any

from claude_db_memory import db
from claude_db_memory.config import md_dir
from claude_db_memory.md_sync import parse_md_file


def main(args: dict[str, Any]) -> dict[str, Any]:
    conn = db.connect()
    rows = {m.name: m for m in db.list_all(conn, limit=10**9)}
    files = {p.stem: p for p in md_dir().glob("*.md")} if md_dir().exists() else {}
    orphan_rows = sorted(set(rows) - set(files))
    orphan_files = sorted(set(files) - set(rows))
    drift: list[str] = []
    for name in set(rows) & set(files):
        try:
            file_mem = parse_md_file(files[name])
        except Exception:
            drift.append(name)
            continue
        row = rows[name]
        if (row.description != file_mem.description
                or row.body.strip() != file_mem.body.strip()
                or row.type != file_mem.type
                or row.tags != file_mem.tags
                or row.project != file_mem.project):
            drift.append(name)
    return {"orphan_rows": orphan_rows, "orphan_files": orphan_files, "drift": sorted(drift)}
