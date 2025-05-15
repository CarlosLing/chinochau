# Makefile for chinochau project

.PHONY: help install run-app run-backend lint test

help:
	@echo "Available commands:"
	@echo "  install      Install all dependencies using Poetry"
	@echo "  run-app      Run the Streamlit frontend app"
	@echo "  run-backend  Run the FastAPI backend server"
	@echo "  lint         Run flake8 linter on the codebase"
	@echo "  test         Run all tests"

install:
	poetry install

run-app:
	poetry run streamlit run app.py

run-backend:
	poetry run uvicorn backend.main:app --reload

lint:
	poetry run flake8 chinochau backend

test:
	poetry run pytest tests
