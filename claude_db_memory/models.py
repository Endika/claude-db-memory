from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Optional

VALID_TYPES = frozenset({"user", "feedback", "project", "reference", "note"})
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")


def validate_name(name: str) -> None:
    if not NAME_PATTERN.match(name):
        raise ValueError(
            f"Invalid memory name {name!r}: must match {NAME_PATTERN.pattern}"
        )


def validate_type(type_: str) -> None:
    if type_ not in VALID_TYPES:
        raise ValueError(
            f"Invalid memory type {type_!r}: must be one of {sorted(VALID_TYPES)}"
        )


@dataclass
class Memory:
    id: Optional[int]
    name: str
    type: str
    description: str
    body: str
    tags: list[str] = field(default_factory=list)
    project: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    source_file: str = ""

    def __post_init__(self) -> None:
        validate_name(self.name)
        validate_type(self.type)
