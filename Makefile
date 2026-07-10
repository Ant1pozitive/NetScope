.PHONY: format lint test clean

format:
	ruff format .
	ruff check . --fix

lint:
	ruff check .
	mypy netscope

test:
	pytest

clean:
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf .ruff_cache
	rm -rf build
	rm -rf dist
	rm -rf *.egg-info