# claude-db-memory

SQLite-backed long-term memory for Claude Code with FTS5 search and Markdown backup.

## Why

Claude Code's native memory stores entries as Markdown files indexed by `MEMORY.md`, which is auto-loaded into the system prompt at session start. The index is truncated after ~200 lines, so memories silently disappear past that limit. There is no search, no filtering, and no scaling beyond a few dozen entries.

`claude-db-memory` keeps the auto-loaded `MEMORY.md` compatibility but moves the source of truth to a local SQLite database with FTS5 full-text search. Markdown files become a versionable backup layer that can recover the database at any time.

## Install

### As a Claude Code plugin

```bash
/plugin install github:Endika/claude-db-memory
```

### Manual

```bash
git clone https://github.com/Endika/claude-db-memory ~/.claude/plugins/claude-db-memory
cd ~/.claude/plugins/claude-db-memory
pip install -e .
```

Claude Code reads `.claude-plugin/plugin.json` and registers the MCP server automatically.

## CLI

```bash
memory add --type feedback --name commits --description "..." --body "..."
memory search "tramita"
memory list --type feedback
memory get commits
memory update commits --description "new"
memory delete commits
memory reindex
memory verify
memory export
```

Add `--json` to any command for machine-readable output.

## MCP tools

The plugin exposes these tools to Claude Code:

- `tool_add_memory`
- `tool_search_memory`
- `tool_get_memory`
- `tool_update_memory`
- `tool_delete_memory`
- `tool_list_memories`
- `tool_reindex`
- `tool_verify`

## Storage

By default the plugin stores data per workspace at:

```
~/.claude/projects/<workspace>/memory/
├── MEMORY.md            # auto-generated index, auto-loaded by Claude Code
├── memory.db            # SQLite, gitignored
└── memories/            # .md backup
```

Override with `CLAUDE_DB_MEMORY_DIR=/path/to/dir` for a global memory shared across workspaces.

## Development

```bash
make install        # pip install -e ".[dev]"
make check          # lint + type-check + tests
make format         # auto-format (ruff)
make test           # pytest only
make test-cov       # pytest with coverage
```

## Release process

This project uses [Release Please](https://github.com/googleapis/release-please) to automate versioning and releases based on [Conventional Commits](https://www.conventionalcommits.org/).

- Every commit on `main` triggers Release Please.
- It maintains a release PR that aggregates pending changes into `CHANGELOG.md` and bumps the version in `pyproject.toml`.
- Merging the release PR creates a tag (`vX.Y.Z`) and a GitHub release.

Conventional commit prefixes:
- `feat:` -> minor version bump
- `fix:` -> patch version bump
- `feat!:` / `BREAKING CHANGE:` -> major version bump
- `chore:`, `docs:`, `ci:`, `refactor:`, `test:` -> no version bump (still appear in changelog under their section)

## Continuous integration

GitHub Actions runs three parallel jobs on every push and PR:

- **lint** -- `ruff check` + `ruff format --check`
- **type-check** -- `mypy`
- **test** -- `pytest` on Python 3.10, 3.11, 3.12

## License

MIT.
