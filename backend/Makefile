.PHONY: help install dev test lint format clean migrate reset-db test-scraper scrape-sites

help:
	@echo "Available commands:"
	@echo "  install     - Install dependencies"
	@echo "  dev         - Run development server"
	@echo "  test        - Run tests"
	@echo "  lint        - Run linting (flake8, mypy)"
	@echo "  format      - Format code (black, isort)"
	@echo "  migrate     - Generate and apply migrations"
	@echo "  reset-db    - Reset database"
	@echo "  test-scraper - Test scraper with URL"
	@echo "  scrape-sites - Show supported scraping sites"
	@echo "  clean       - Clean cache and temp files"

install:
	uv sync

dev:
	uv run uvicorn app.main:app --reload --port 8000

test:
	uv run python -m unittest discover tests/ -v
	uv run coverage run -m unittest discover tests/
	uv run coverage report
	uv run coverage html

lint:
	uv run flake8 app/
	uv run mypy app/

format:
	uv run black app/ tests/
	uv run isort app/ tests/

migrate:
	uv run alembic revision --autogenerate -m "Auto migration"
	uv run alembic upgrade head

reset-db:
	uv run alembic downgrade base
	uv run alembic upgrade head

test-scraper:
	@echo "Usage: make test-scraper URL=<url> [CATEGORY=<category>]"
	@if [ -z "$(URL)" ]; then \
		echo "Error: URL parameter is required"; \
		echo "Example: make test-scraper URL=https://amazon.com/product"; \
	else \
		uv run python scripts/test_scraper.py "$(URL)" $(CATEGORY); \
	fi

scrape-sites:
	uv run python scripts/test_scraper.py --sites

clean:
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.pyc" -delete
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .coverage