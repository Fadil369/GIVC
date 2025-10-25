# Quick Test Commands Reference

## Setup
```bash
# Activate virtual environment
source venv/bin/activate

# Install test dependencies (if not already installed)
pip install pytest pytest-cov
```

## Running Tests

### All Unit Tests
```bash
pytest tests/unit/ -v
```

### Specific Module Tests
```bash
# Helpers tests
pytest tests/unit/utils/test_helpers.py -v

# Validators tests
pytest tests/unit/utils/test_validators.py -v

# Auth manager tests
pytest tests/unit/auth/test_auth_manager.py -v

# Eligibility service tests
pytest tests/unit/services/test_eligibility.py -v
```

### With Coverage
```bash
# Basic coverage report
pytest tests/unit/ --cov=auth --cov=utils --cov=services

# Coverage with HTML report
pytest tests/unit/ --cov=auth --cov=utils --cov=services --cov-report=html

# Coverage with missing lines
pytest tests/unit/ --cov=auth --cov=utils --cov=services --cov-report=term-missing
```

### Filtering Tests
```bash
# Run only tests matching pattern
pytest tests/unit/ -k "test_validate"

# Run tests by marker
pytest tests/unit/ -m unit

# Exclude slow tests
pytest tests/unit/ -m "not slow"
```

### Debugging
```bash
# Show print statements
pytest tests/unit/ -v -s

# Stop on first failure
pytest tests/unit/ -x

# Show local variables on failure
pytest tests/unit/ -l

# Verbose traceback
pytest tests/unit/ --tb=long
```

### Quick Checks
```bash
# Fast run without coverage
pytest tests/unit/ --no-cov

# Summary only
pytest tests/unit/ -q
```

## Current Test Stats
- **Total Tests:** 72
- **Pass Rate:** 100%
- **Execution Time:** ~1s
- **Coverage:** 74-95% on tested modules

## Viewing Coverage Reports
```bash
# Generate HTML coverage report
pytest tests/unit/ --cov=auth --cov=utils --cov=services --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```
