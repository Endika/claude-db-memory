.PHONY: install test test-cov lint format type-check check clean

SRC := claude_db_memory tests mcp_server.py

install:
	uv sync --all-groups

test:
	uv run pytest -v

test-cov:
	uv run pytest --cov=claude_db_memory --cov-report=term-missing

lint:
	uv run ruff check $(SRC)
	uv run ruff format --check $(SRC)

format:
	uv run ruff format $(SRC)
	uv run ruff check --fix $(SRC)

type-check:
	uv run mypy claude_db_memory mcp_server.py

check: lint type-check test

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist build *.egg-info .venv
	find . -type d -name __pycache__ -exec rm -rf {} +
