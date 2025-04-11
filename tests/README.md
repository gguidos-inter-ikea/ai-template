# Testing Documentation

This directory contains tests for all major components of the application.

## Test Structure

- `unit/`: Unit tests for individual components
  - `test_rate_limiter_core.py`: Rate limiter core functionality
  - `test_rate_limiter.py`: Rate limiting with actual delay
  - `test_rate_limiter_mock.py`: Rate limiting with mocked Redis
  - `test_dependencies.py`: Dependency injection tests
  - `test_security_monitor.py`: Security monitoring system tests
- `integration/`: Integration tests
  - `test_rate_limiter_integration.py`: Rate limiting with Redis
  - `test_user_api.py`: User API with rate limiting and logging
- `scripts/`: Script tests
- `curl/`: HTTP endpoint tests

## Running Tests

### Prerequisites

- Docker and Docker Compose
- Python 3.9+
- Test dependencies (included in requirements.txt)

### Local Development Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Install additional test dependencies
pip install pytest pytest-asyncio pytest-cov flake8 black mypy
```

### Running Tests with Docker

```bash
# Run all tests
docker compose exec api pytest tests/ -v

# Run specific test file
docker compose exec api pytest tests/unit/test_security_monitor.py -v

# Run with coverage
docker compose exec api pytest tests/ --cov=src --cov-report=html
```

### Running Tests Locally

```bash
# Run all tests
pytest tests/ -v

# Run specific test category
pytest tests/unit/ -v
pytest tests/integration/ -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Continuous Integration

The project uses GitHub Actions for CI/CD. On each push and pull request:

1. **Test Job**:
   - Runs all unit and integration tests
   - Checks code coverage
   - Runs linting (flake8, black, mypy)

2. **Security Job**:
   - Runs security scan with Snyk
   - Checks for vulnerabilities

3. **Docker Job**:
   - Builds and tests Docker image
   - Runs all tests in containerized environment

### CI/CD Pipeline

The pipeline runs on:
- Push to main/master/develop branches
- Pull requests to main/master

Requirements for merging:
- All tests must pass
- Code coverage must meet minimum threshold
- No high-severity security issues
- Successful Docker build and test

## Test Categories

### Unit Tests

- **Rate Limiting**: Core functionality, mocked Redis, actual delays
- **Security Monitor**: Event processing, error handling, alerts
- **Dependencies**: Dependency injection system
- **Configuration**: Environment and settings management

### Integration Tests

- **API Endpoints**: Full HTTP request/response cycle
- **Rate Limiting**: Real Redis integration
- **Security Events**: Log generation and processing
- **Alert System**: Email, Teams, and Slack notifications

### Performance Tests

Located in `tests/performance/`:
- Load testing with different concurrency levels
- Rate limit behavior under load
- Memory usage monitoring

## Best Practices

1. **Test Isolation**:
   - Use fixtures for setup/teardown
   - Mock external services
   - Clean up after tests

2. **Coverage**:
   - Aim for 80%+ coverage
   - Focus on critical paths
   - Include edge cases

3. **Maintenance**:
   - Keep tests up to date
   - Remove obsolete tests
   - Document test requirements

## Notes

- The security monitor tests use mocked time for consistent results
- Integration tests require running Redis instance
- Some tests have intentional delays for rate limit testing
- Use `docker compose exec redis redis-cli FLUSHDB` before rate limit tests 