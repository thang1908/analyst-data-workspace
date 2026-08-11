.PHONY: dev test lint format db-up db-down clean

dev:
	uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v

lint:
	ruff check .
	mypy packages/ apps/

format:
	ruff format .

db-up:
	docker-compose up -d

db-down:
	docker-compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
