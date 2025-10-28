# 🤝 Contributing to NPHIES RCM Integration Platform

Thank you for your interest in contributing to the NPHIES RCM Integration Platform! This document provides guidelines and instructions for contributing.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Coding Standards](#coding-standards)
- [Documentation](#documentation)

## 📜 Code of Conduct

This project follows a code of conduct that all contributors are expected to uphold. Please be respectful and professional in all interactions.

## 🚀 Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/GIVC.git
   cd GIVC
   ```
3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/fadil369/GIVC.git
   ```

## 💻 Development Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git

### Installation

1. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # Windows
   .\venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"  # Install development dependencies
   ```

3. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. Install pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## 🔧 Making Changes

### Branching Strategy

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Urgent production fixes

### Creating a Feature Branch

```bash
git checkout develop
git pull upstream develop
git checkout -b feature/your-feature-name
```

### Commit Message Guidelines

Follow conventional commits:

```
type(scope): subject

body

footer
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Example:**
```
feat(eligibility): add batch processing support

Implement batch processing for eligibility checks to handle
multiple member IDs in a single request.

Closes #123
```

## 🧪 Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_services/test_eligibility.py

# Run specific test
pytest tests/test_services/test_eligibility.py::TestEligibilityService::test_check_eligibility
```

### Writing Tests

- Place tests in `tests/` directory
- Mirror the structure of the source code
- Use descriptive test names
- Aim for 80%+ code coverage
- Use fixtures from `conftest.py`

**Example:**
```python
def test_eligibility_check_success(sample_member_id, mock_nphies_response_success):
    """Test successful eligibility check"""
    service = EligibilityService(auth_manager)
    result = service.check_eligibility(sample_member_id, "7000911508", "2025-10-22")
    assert result["status"] == "success"
```

## 📤 Submitting Changes

### Before Submitting

1. **Update from upstream**:
   ```bash
   git checkout develop
   git pull upstream develop
   git checkout your-branch
   git rebase develop
   ```

2. **Run tests**:
   ```bash
   pytest
   ```

3. **Run linters**:
   ```bash
   black .
   isort .
   flake8 .
   mypy .
   ```

4. **Update documentation** if needed

### Creating a Pull Request

1. **Push your branch**:
   ```bash
   git push origin feature/your-feature-name
   ```

2. **Create Pull Request** on GitHub:
   - Set base branch to `develop`
   - Provide clear description
   - Reference related issues
   - Add appropriate labels

3. **PR Template**:
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] All tests pass
   - [ ] New tests added
   - [ ] Coverage maintained/improved
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   - [ ] No new warnings generated
   
   ## Related Issues
   Closes #123
   ```

## 📏 Coding Standards

### Python Style Guide

- Follow PEP 8
- Use Black for formatting (line length: 100)
- Use isort for import sorting
- Use type hints
- Write docstrings for all public functions/classes

### Code Quality

- **Complexity**: Keep functions focused and simple
- **Naming**: Use descriptive names (avoid abbreviations)
- **Comments**: Explain "why", not "what"
- **Error Handling**: Use try-except appropriately
- **Logging**: Use appropriate log levels

### Example Code

```python
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class EligibilityService:
    """
    Service for handling NPHIES eligibility verification.
    
    This service manages eligibility checks for insurance members,
    including building FHIR bundles and parsing responses.
    """
    
    def check_eligibility(
        self,
        member_id: str,
        payer_id: str,
        service_date: str,
        patient_data: Optional[Dict] = None
    ) -> Dict:
        """
        Check insurance eligibility for a member.
        
        Args:
            member_id: Member identification number
            payer_id: Payer/insurance company ID
            service_date: Date of service (YYYY-MM-DD)
            patient_data: Optional patient information
            
        Returns:
            Dictionary containing eligibility status and details
            
        Raises:
            ValueError: If required parameters are invalid
            ConnectionError: If NPHIES API is unreachable
        """
        logger.info(f"Checking eligibility for member {member_id}")
        
        try:
            # Implementation here
            pass
        except Exception as e:
            logger.error(f"Eligibility check failed: {str(e)}")
            raise
```

## 📚 Documentation

### Updating Documentation

- Update README.md for user-facing changes
- Update docstrings for code changes
- Add examples for new features
- Update ARCHITECTURE.md for design changes

### Documentation Standards

- Use Markdown format
- Include code examples
- Add diagrams where helpful
- Keep it concise and clear

## 🐛 Reporting Bugs

### Bug Report Template

```markdown
**Describe the bug**
Clear description of the issue

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '....'
3. See error

**Expected behavior**
What you expected to happen

**Actual behavior**
What actually happened

**Environment:**
 - OS: [e.g. Windows 10]
 - Python Version: [e.g. 3.9]
 - Package Version: [e.g. 2.0.0]

**Additional context**
Any other relevant information
```

## 💡 Feature Requests

### Feature Request Template

```markdown
**Is your feature request related to a problem?**
Clear description of the problem

**Describe the solution you'd like**
Clear description of desired solution

**Describe alternatives considered**
Alternative solutions you've considered

**Additional context**
Any other relevant information
```

## 🏆 Recognition

Contributors will be recognized in:
- README.md Contributors section
- Release notes
- Project documentation

## 📞 Getting Help

- **Issues**: [GitHub Issues](https://github.com/fadil369/GIVC/issues)
- **Discussions**: [GitHub Discussions](https://github.com/fadil369/GIVC/discussions)
- **Documentation**: [Project Wiki](https://github.com/fadil369/GIVC/wiki)

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to make healthcare integration better!** 🙏
