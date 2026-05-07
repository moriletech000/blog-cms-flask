# Contributing to Blog CMS

Thank you for your interest in contributing to Blog CMS! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Screenshots if applicable

### Suggesting Features

Feature requests are welcome! Please:
- Check if the feature already exists or is planned
- Provide a clear use case
- Explain why it would be valuable
- Consider implementation complexity

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/moriletech000/blog-cms-flask.git
   cd blog-cms-flask
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow existing code style
   - Add tests for new features
   - Update documentation

4. **Test your changes**
   ```bash
   pytest tests/ -v
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add: Brief description of your changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide a clear description
   - Reference any related issues
   - Ensure all tests pass

## Development Setup

### Using Docker

```bash
docker compose up --build
docker compose exec flask flask db upgrade
docker compose exec flask flask seed-db
```

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up database
flask db upgrade
flask seed-db

# Run tests
pytest
```

## Code Style

- Follow PEP 8 for Python code
- Use meaningful variable and function names
- Add docstrings to functions and classes
- Keep functions focused and small
- Write self-documenting code

### Example

```python
def calculate_reading_time(text: str) -> int:
    """
    Calculate estimated reading time in minutes.
    
    Args:
        text: The text content to analyze
        
    Returns:
        Estimated reading time in minutes (minimum 1)
    """
    word_count = len(text.split())
    return max(1, round(word_count / 200))
```

## Testing

- Write tests for new features
- Ensure existing tests pass
- Aim for good test coverage
- Use pytest fixtures for setup

```python
def test_create_post(admin_client, db):
    """Test creating a new post."""
    response = admin_client.post('/admin/posts/new', data={
        'title': 'Test Post',
        'body': '<p>Content</p>',
        'status': 'draft'
    })
    assert response.status_code == 200
```

## Documentation

- Update README.md for major changes
- Add docstrings to new functions
- Update API documentation if needed
- Include examples where helpful

## Commit Messages

Use clear, descriptive commit messages:

- `Add: New feature description`
- `Fix: Bug description`
- `Update: What was updated`
- `Refactor: What was refactored`
- `Docs: Documentation changes`
- `Test: Test additions or changes`

## Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged
4. Your contribution will be credited

## Questions?

- Open an issue for questions
- Check existing documentation
- Review closed issues and PRs

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Blog CMS! 🎉