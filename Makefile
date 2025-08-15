# Makefile for MCP Container Server

.PHONY: help install test lint run build docker-build docker-run clean dev

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	pip install -r requirements.txt

test: ## Run tests
	pytest tests/ -v

lint: ## Run linting
	python -m py_compile src/server.py
	python -m py_compile tests/test_server.py

run: ## Run server in development mode
	python -m src.server --log-level DEBUG

dev: install ## Setup development environment
	@echo "Development environment ready!"
	@echo "Run 'make run' to start the server"

build: test lint ## Build and validate the project
	@echo "Build completed successfully!"

docker-build: ## Build Docker container
	docker build -t mcp-server .

docker-run: docker-build ## Run Docker container
	docker run -p 8000:8000 mcp-server

docker-test: ## Test Docker container
	docker run -d -p 8001:8000 --name mcp-test mcp-server
	sleep 5
	curl -f http://localhost:8001/health || (docker logs mcp-test && exit 1)
	docker stop mcp-test && docker rm mcp-test

compose-up: ## Start with docker-compose
	docker-compose up -d

compose-down: ## Stop docker-compose
	docker-compose down

compose-logs: ## View docker-compose logs
	docker-compose logs -f

clean: ## Clean up temporary files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	docker system prune -f

health-check: ## Check server health
	curl -f http://localhost:8000/health

integration-test: ## Run integration tests
	@echo "Starting server for integration tests..."
	python -m src.server --port 8002 &
	@PID=$$!; \
	sleep 3; \
	echo "Testing health endpoint..."; \
	curl -f http://localhost:8002/health || (kill $$PID && exit 1); \
	echo "Testing root endpoint..."; \
	curl -f http://localhost:8002/ || (kill $$PID && exit 1); \
	echo "Integration tests passed!"; \
	kill $$PID