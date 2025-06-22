# Makefile for chinochau project

.PHONY: help install run-app run-backend lint test test-backend test-coverage test-unit test-integration test-fast test-watch

help:
	@echo "Available commands:"
	@echo "  install         Install all dependencies using Poetry"
	@echo "  run-backend     Run the FastAPI backend server"
	@echo "  lint            Run flake8 linter on the codebase"
	@echo "  test            Run all tests"
	@echo "  test-backend    Run backend tests only"
	@echo "  test-coverage   Run tests with coverage report"
	@echo "  test-unit       Run unit tests only"
	@echo "  test-integration Run integration tests only"
	@echo "  run-frontend    Run the React + Vite frontend dev server"

install:
	poetry install

run-backend:
	poetry run uvicorn backend.main:app --reload

run-frontend:
	cd frontend && npm install && npm run dev

lint:
	poetry run flake8 chinochau backend

test:
	@echo "🧪 Running all tests..."
	poetry run pytest backend/tests/

test-backend:
	@echo "🔍 Running backend tests with verbose output..."
	poetry run pytest backend/tests/ -v

test-coverage:
	@echo "📊 Running tests with coverage report..."
	poetry run pytest backend/tests/ --cov=backend --cov-report=html --cov-report=term
	@echo "📈 Coverage report generated in htmlcov/index.html"

test-unit:
	@echo "🔬 Running unit tests only..."
	poetry run pytest backend/tests/ -m "not integration" -v

test-integration:
	@echo "🔗 Running integration tests only..."
	poetry run pytest backend/tests/ -m integration -v
