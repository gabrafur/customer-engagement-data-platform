.PHONY: install quality test demo generate clean

install:
	python -m pip install -e '.[dev,spark]'

quality:
	ruff check .
	mypy src

test:
	pytest

generate:
	engagement-platform generate --customers 100 --output data/generated

demo:
	engagement-platform run --config configs/development.yml --customers 100

clean:
	find . -type d -name __pycache__ -prune -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage htmlcov build dist
