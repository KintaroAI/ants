.PHONY: help install install-dev test clean run run-stats show-stats lint format venv venv-clean activate

help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## Create virtual environment
	python3 -m venv venv
	@echo "Virtual environment created. Activate it with: source venv/bin/activate"
	@echo "Or use 'make run' to run the simulation directly"

activate: ## Show activation command
	@echo "To activate the virtual environment, run:"
	@echo "source venv/bin/activate"

install: venv ## Install dependencies in virtual environment
	venv/bin/pip install -r requirements.txt

install-dev: venv ## Install development dependencies in virtual environment
	venv/bin/pip install -r requirements.txt
	venv/bin/pip install pytest pytest-cov flake8 black

test: ## Run tests
	venv/bin/python -m pytest tests/ -v

test-coverage: ## Run tests with coverage
	venv/bin/python -m pytest tests/ --cov=src --cov-report=html

run: ## Run the simulation
	venv/bin/python src/colony.py

run-stats: ## Run the simulation with statistics collection
	venv/bin/python src/colony.py --stats

show-stats: ## Show statistics visualization
	./show_stats.sh

lint: ## Run linting
	venv/bin/flake8 src/ tests/

format: ## Format code with black
	venv/bin/black src/ tests/

clean: ## Clean up generated files
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ htmlcov/

venv-clean: ## Remove virtual environment
	rm -rf venv/ 