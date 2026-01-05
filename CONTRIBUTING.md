# Contributing to Execution Lane

Thank you for your interest in contributing to Execution Lane! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help maintain a welcoming environment

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/Omni-Defi-Production-System1/execution_lane-/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (Python version, OS, etc.)
   - Relevant logs or error messages

### Suggesting Features

1. Check existing issues and pull requests
2. Create an issue with:
   - Clear feature description
   - Use case and benefits
   - Potential implementation approach

### Submitting Changes

1. **Fork the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/execution_lane-.git
   cd execution_lane-
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style
   - Add tests for new functionality
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Run tests
   pytest tests/
   
   # Check code style
   flake8 src/
   black src/ --check
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```
   
   Commit message format:
   - `Add: ` for new features
   - `Fix: ` for bug fixes
   - `Update: ` for updates to existing features
   - `Docs: ` for documentation changes
   - `Refactor: ` for code refactoring

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Go to the original repository
   - Click "New Pull Request"
   - Select your branch
   - Fill in the PR template

## Development Setup

### Environment Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
npm install

# Install development dependencies
pip install pytest pytest-asyncio pytest-cov black flake8 mypy
```

### Running Tests

```bash
# All tests
pytest tests/

# With coverage
pytest --cov=src tests/

# Specific test file
pytest tests/test_core.py -v
```

### Code Style

We follow these conventions:

**Python:**
- PEP 8 style guide
- Black for formatting (line length: 100)
- Type hints where appropriate
- Docstrings for all public functions/classes

**JavaScript:**
- ESLint for linting
- Prettier for formatting
- JSDoc comments for functions

### Code Formatting

```bash
# Format Python code
black src/ tests/

# Check formatting
black src/ tests/ --check

# Lint Python code
flake8 src/ tests/

# Type checking
mypy src/
```

## Project Structure

```
execution_lane-/
├── src/              # Source code
│   ├── core/         # Core engines
│   ├── strategies/   # Trading strategies
│   ├── data/         # Data modules
│   └── utils/        # Utilities
├── tests/            # Test suite
├── docs/             # Documentation
└── config/           # Configuration files
```

## Pull Request Guidelines

### PR Checklist

- [ ] Code follows project style guidelines
- [ ] Tests added for new functionality
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Commit messages are clear
- [ ] Branch is up to date with main

### PR Description Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
Describe testing performed

## Screenshots (if applicable)
Add screenshots for UI changes

## Checklist
- [ ] Tests pass
- [ ] Documentation updated
- [ ] Code follows style guide
```

## Documentation

When adding or updating features:

1. Update relevant documentation in `docs/`
2. Update module docstrings
3. Add code examples where helpful
4. Update README if needed

## Testing Guidelines

### Writing Tests

- One test file per module: `test_<module_name>.py`
- Descriptive test names: `test_<functionality>_<scenario>`
- Use fixtures for common setup
- Test edge cases and error conditions

### Test Example

```python
def test_calculate_output_with_zero_reserves(math_engine):
    """Test handling of zero reserves"""
    amount_out, impact = math_engine.calculate_constant_product_output(
        amount_in=Decimal('1000'),
        reserve_in=Decimal('0'),  # Invalid
        reserve_out=Decimal('500000'),
        fee=Decimal('0.003')
    )
    
    assert amount_out == Decimal('0')
    assert impact == Decimal('1')
```

## Security

### Reporting Security Issues

**DO NOT** create public issues for security vulnerabilities.

Instead, email: security@example.com (replace with actual email)

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

### Security Best Practices

- Never commit secrets or API keys
- Use environment variables for sensitive data
- Follow secure coding practices
- Review dependencies for vulnerabilities

## Questions?

- Create a [GitHub Issue](https://github.com/Omni-Defi-Production-System1/execution_lane-/issues)
- Check existing documentation in `docs/`
- Review code examples in the repository

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Execution Lane! 🚀
