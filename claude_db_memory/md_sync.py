from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path

from claude_db_memory.config import ensure_dirs, index_path, md_dir
from claude_db_memory.models import Memory

STRING_FIELDS = frozenset({"name", "type", "description", "created_at", "updated_at"})


def serialize_memory(m: Memory) -> str:
    fm = {
        "name": m.name,
        "type": m.type,
        "description": m.description,
        "tags": m.tags,
        "project": m.project,
        "created_at": m.created_at,
        "updated_at": m.updated_at,
    }
    fm_lines = ["---"]
    for k, v in fm.items():
        fm_lines.append(f"{k}: {json.dumps(v)}")
    fm_lines.append("---")
    return "\n".join(fm_lines) + "\n\n" + m.body.rstrip() + "\n"


def parse_md_file(path: Path) -> Memory:
    text = path.read_text()
    if not text.startswith("---\n"):
        raise ValueError(f"{path}: missing frontmatter delimiter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError(f"{path}: unterminated frontmatter")
    fm_block = text[4:end]
    body = text[end + 5 :].strip()
    fm: dict = {}
    for line in fm_block.splitlines():
        if not line.strip():
            continue
        key, _, raw = line.partition(":")
        key = key.strip()
        raw = raw.strip()
        try:
            fm[key] = json.loads(raw)
        except json.JSONDecodeError as err:
            if key in STRING_FIELDS:
                fm[key] = raw
            else:
                raise ValueError(f"{path}: field {key!r} is not valid JSON: {raw!r}") from err
    return Memory(
        id=None,
        name=fm["name"],
        type=fm["type"],
        description=fm["description"],
        body=body,
        tags=fm.get("tags", []),
        project=fm.get("project"),
        created_at=fm.get("created_at", ""),
        updated_at=fm.get("updated_at", ""),
        source_file=f"memories/{fm['name']}.md",
    )


def write_md(m: Memory) -> Path:
    ensure_dirs()
    path = md_dir() / f"{m.name}.md"
    path.write_text(serialize_memory(m))
    return path


def delete_md(name: str) -> None:
    path = md_dir() / f"{name}.md"
    if path.exists():
        path.unlink()


def regenerate_index(memories: Iterable[Memory]) -> Path:
    ensure_dirs()
    by_type: dict[str, list[Memory]] = {}
    for m in memories:
        by_type.setdefault(m.type, []).append(m)
    lines = ["# Memory Index", ""]
    for type_ in sorted(by_type):
        lines.append(f"## {type_}")
        items = sorted(by_type[type_], key=lambda x: x.updated_at, reverse=True)
        for m in items:
            lines.append(f"- [{m.name}](memories/{m.name}.md) — {m.description}")
        lines.append("")
    path = index_path()
    path.write_text("\n".join(lines))
    return path
