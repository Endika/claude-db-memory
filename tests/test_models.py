import pytest

from claude_db_memory.models import VALID_TYPES, Memory, validate_name, validate_type


def test_memory_dataclass_minimal():
    m = Memory(
        id=None,
        name="feedback_commits",
        type="feedback",
        description="Never run git writes",
        body="body text",
        tags=["git"],
        project=None,
        created_at="2026-05-05T10:00:00",
        updated_at="2026-05-05T10:00:00",
        source_file="memories/feedback_commits.md",
    )
    assert m.name == "feedback_commits"
    assert m.tags == ["git"]


def test_validate_name_accepts_slug():
    validate_name("feedback_commits")
    validate_name("project_tramita_frontend_v2")


def test_validate_name_rejects_invalid():
    for bad in ["With Space", "UPPER", "dashed-name", "trailing_", "", "with.dot"]:
        with pytest.raises(ValueError):
            validate_name(bad)


def test_validate_type_accepts_known():
    for t in VALID_TYPES:
        validate_type(t)


def test_validate_type_rejects_unknown():
    with pytest.raises(ValueError):
        validate_type("unknown_type")
