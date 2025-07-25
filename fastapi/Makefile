# Add this to your Makefile

.PHONY: test test-unit test-integration test-performance test-cov test-fast

# Run all tests
test:
	poetry run pytest

# Run only unit tests
test-unit:
	poetry run pytest -m "unit" tests/

# Run only integration tests  
test-integration:
	poetry run pytest -m "integration" tests/test_integration.py

# Run only integration tests  
test-ratelimit:
	poetry run pytest -m "rate_limiting" tests/test_rate_limiting.py

# Run performance tests
test-performance:
	poetry run pytest -m "performance" tests/test_performance.py

# Run tests with coverage
test-cov:
	poetry run pytest --cov=app --cov-report=html --cov-report=term

# Run fast tests (exclude slow ones)
test-fast:
	poetry run pytest -m "not slow"

# Run tests in parallel
test-parallel:
	poetry run pytest -n auto

# Run specific test file
test-users:
	poetry run pytest tests/api/v1/test_users.py -v

# Run specific test method
test-create-user:
	poetry run pytest tests/api/v1/test_users.py::TestUsersEndpoints::test_create_user_success -v