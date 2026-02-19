.PHONY: help install dev-setup test lint format coverage load-test flash-a flash-b logs clean

help:
	@echo "Blind Date with Bandwidth - Development Tasks"
	@echo "=============================================="
	@echo "make install          - Install dependencies"
	@echo "make dev-setup        - Full development environment setup"
	@echo "make test             - Run all tests"
	@echo "make lint             - Check code style (flake8)"
	@echo "make format           - Format code (black)"
	@echo "make coverage         - Generate coverage report"
	@echo "make load-test        - Run locust load tests"
	@echo "make flash-a          - Flash ESP32 Station A"
	@echo "make flash-b          - Flash ESP32 Station B"
	@echo "make logs             - Tail Pi server logs"
	@echo "make clean            - Clean build artifacts"

install:
	pip install -r requirements.txt
	pip install -r requirements-test.txt

dev-setup: install
	mkdir -p logs
	mkdir -p data
	apt-get update && apt-get install -y mosquitto mosquitto-clients
	systemctl start mosquitto || true
	echo "✓ Development environment ready"

test:
	cd raspberry_pi_server && pytest tests/ -v --asyncio-mode=auto --cov=. --cov-report=term-missing

lint:
	flake8 raspberry_pi_server/ --max-line-length=100 --exclude=venv,tests
	pylint raspberry_pi_server/*.py 2>/dev/null || true

format:
	black raspberry_pi_server/ --line-length=100
	isort raspberry_pi_server/ --profile black

coverage:
	coverage run -m pytest raspberry_pi_server/tests/
	coverage report -m
	coverage html
	@echo "Coverage report: htmlcov/index.html"

load-test:
	cd raspberry_pi_server && locust -f tests/load_test.py -u 50 -r 5 --run-time 5m http://localhost:5000

flash-a:
	platformio run --target upload -e esp32 -d esp32_firmware

flash-b:
	platformio run --target upload -e esp32 -d esp32_firmware

logs:
	tail -f logs/blind_date.log

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name '*.pyc' -delete
	rm -rf .pytest_cache/ htmlcov/ .coverage
	rm -rf build/ dist/ *.egg-info/
