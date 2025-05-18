# Makefile for chinochau project

.PHONY: help install run-app run-backend lint test

help:
	@echo "Available commands:"
	@echo "  install      Install all dependencies using Poetry"
	@echo "  run-backend  Run the FastAPI backend server"
	@echo "  lint         Run flake8 linter on the codebase"
	@echo "  test         Run all tests"
	@echo "  run-frontend Run the React + Vite frontend dev server"

install:
	poetry install

run-backend:
	poetry run uvicorn backend.main:app --reload

run-frontend:
	cd frontend && npm install && npm run dev

lint:
	poetry run flake8 chinochau backend

test:
	poetry run pytest tests
