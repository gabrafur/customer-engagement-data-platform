.PHONY: install quality test build demo generate rebuild benchmark impact clean

install:
	python -m pip install -e '.[dev,spark]'

quality:
	ruff check .
	mypy src

test:
	pytest

build:
	python -m build --wheel

generate:
	engagement-platform generate --customers 100 --output data/generated

demo:
	engagement-platform run --config configs/development.yml --customers 100

rebuild:
	engagement-platform rebuild --config configs/development.yml --customers 100 --as-of-date 2026-06-01

benchmark:
	engagement-platform benchmark --config configs/development.yml --customers 10000

impact:
	engagement-platform impact --registry configs/modules.toml --changed src/engagement_platform/dag.py docs/architecture.md

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov build dist
