.PHONY: install test test-cov lint format type-check check clean

PY := python3
PIP := $(PY) -m pip

install:
	$(PIP) install -e ".[dev]"

test:
	pytest -v

test-cov:
	pytest --cov=claude_db_memory --cov-report=term-missing

lint:
	$(PY) -m ruff check claude_db_memory tests mcp_server.py
	$(PY) -m ruff format --check claude_db_memory tests mcp_server.py

format:
	$(PY) -m ruff format claude_db_memory tests mcp_server.py
	$(PY) -m ruff check --fix claude_db_memory tests mcp_server.py

type-check:
	$(PY) -m mypy claude_db_memory mcp_server.py

check: lint type-check test

clean:
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov dist build *.egg-info
	find . -type d -name __pycache__ -exec rm -rf {} +
