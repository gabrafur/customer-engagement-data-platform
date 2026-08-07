.PHONY: install quality test build demo generate rebuild clean

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

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov build dist
