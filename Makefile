.PHONY: help install test lint format run run-prod index docker-build docker-run docker-stop k8s-deploy k8s-logs k8s-status clean

help:
	@echo "RAG System - Available commands:"
	@echo "  install        - Install dependencies"
	@echo "  test           - Run tests"
	@echo "  lint           - Run linters"
	@echo "  format         - Format code"
	@echo "  run            - Run development server"
	@echo "  run-prod       - Run production server"
	@echo "  index          - Index documents"
	@echo "  docker-build   - Build Docker image"
	@echo "  docker-run     - Run Docker container"
	@echo "  docker-stop    - Stop Docker container"
	@echo "  k8s-deploy     - Deploy to Kubernetes"
	@echo "  k8s-logs       - View Kubernetes logs"
	@echo "  k8s-status     - View Kubernetes status"
	@echo "  clean          - Clean generated files"

install:
	pip install -r requirements.txt
	playwright install chromium

test:
	pytest tests/ -v --cov=app --cov-report=html

test-unit:
	pytest tests/unit/ -v

test-integration:
	pytest tests/integration/ -v

test-e2e:
	pytest tests/e2e/ -v -m e2e

test-benchmark:
	pytest tests/performance/ -v -m benchmark

lint:
	flake8 app/ || true
	mypy app/ || true
	black --check app/ || true

format:
	black app/
	isort app/

run:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

index:
	python scripts/index_documents.py

docker-build:
	docker build -t rag-api:latest -f docker/Dockerfile .

docker-run:
	docker-compose -f docker/docker-compose.yml up

docker-stop:
	docker-compose -f docker/docker-compose.yml down

k8s-deploy:
	bash scripts/deploy.sh

k8s-logs:
	kubectl logs -f -n rag-system -l app=rag-api

k8s-status:
	kubectl get all -n rag-system

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
