# Contributing to API Threads Carousel Generator

🎉 Thank you for your interest in contributing to our project! This document provides guidelines for contributing to the API Threads Carousel Generator.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

## 🤝 Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. Please:

- Use welcoming and inclusive language
- Respect differing viewpoints and experiences
- Accept constructive criticism gracefully
- Focus on what's best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- Git
- Docker (optional, for containerized development)
- OpenAI API key (for AI features)

### Development Setup

1. **Fork and clone the repository**
   ```bash
   git clone https://github.com/yourusername/api-threads-carousel.git
   cd api-threads-carousel
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Install system fonts (Linux/Ubuntu)**
   ```bash
   sudo apt-get install fonts-dejavu-core fonts-noto-color-emoji fonts-liberation
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

## 💡 How to Contribute

### Types of Contributions

We welcome various types of contributions:

- 🐛 **Bug Reports**: Help us identify and fix issues
- ✨ **Feature Requests**: Suggest new functionality
- 📝 **Documentation**: Improve or add documentation
- 🔧 **Code Contributions**: Bug fixes, new features, optimizations
- 🧪 **Testing**: Add or improve tests
- 🎨 **Design**: UI/UX improvements, examples, templates

### Contribution Workflow

1. **Check existing issues** to avoid duplicates
2. **Create an issue** for bugs or feature requests
3. **Fork the repository** and create a feature branch
4. **Make your changes** following our coding standards
5. **Add or update tests** for your changes
6. **Update documentation** if needed
7. **Submit a pull request**

## 📏 Coding Standards

### Python Code Style

We follow PEP 8 with some modifications:

- **Line length**: 88 characters (Black formatter default)
- **String quotes**: Use double quotes for strings
- **Imports**: Use absolute imports when possible
- **Type hints**: Add type hints for function parameters and return values

### Code Formatting

We use automated code formatting tools:

```bash
# Format code with Black
black .

# Sort imports with isort
isort .

# Lint with flake8
flake8 .

# Type checking with mypy
mypy api/ --ignore-missing-imports
```

### Code Structure

Follow the established project structure:

```
api/
├── __init__.py          # Application factory
├── config.py            # Configuration management
├── routes/              # API endpoints
│   ├── __init__.py
│   ├── carousel.py      # Carousel endpoints
│   ├── health.py        # Health endpoints
│   └── docs.py          # Documentation endpoints
├── services/            # Business logic
│   ├── carousel_generator.py
│   └── ai_config_generator.py
├── schemas/             # Data validation schemas
│   └── carousel.py
└── utils/               # Utility functions
    ├── validators.py
    └── responses.py
```

### Documentation Standards

- **Docstrings**: Use Google-style docstrings for all functions and classes
- **Comments**: Write clear, concise comments for complex logic
- **README**: Keep README.md up to date with new features
- **API Docs**: Update OpenAPI specifications when adding endpoints

Example docstring:
```python
def generate_carousel(self, text: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate carousel images from text content
    
    Args:
        text: Text content with slide separators
        config: Configuration dictionary for styling
        
    Returns:
        Dictionary containing generated slides and metadata
        
    Raises:
        ValueError: If text is invalid or too many slides
        Exception: If image generation fails
    """
```

## 🧪 Testing Guidelines

### Test Structure

- **Unit tests**: Test individual functions and methods
- **Integration tests**: Test API endpoints and service interactions
- **Performance tests**: Test response times and resource usage

### Writing Tests

```python
import pytest
from api import create_app

class TestCarouselAPI:
    @pytest.fixture
    def app(self):
        app = create_app()
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def client(self, app):
        return app.test_client()
    
    def test_generate_carousel_success(self, client):
        """Test successful carousel generation"""
        data = {
            'text': 'Test content',
            'config': {'background_color': '#ffffff'}
        }
        
        response = client.post('/api/v1/generate-carousel', 
                             json=data)
        
        assert response.status_code == 200
        assert response.json['success'] is True
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=api --cov-report=html

# Run specific test file
pytest tests/test_carousel_generator.py

# Run tests in parallel
pytest -n auto
```

### Test Coverage

- Aim for **85%+ code coverage**
- Write tests for **error conditions**
- Test **edge cases** and **boundary conditions**
- Mock **external dependencies** (OpenAI, file system)

## 🔄 Pull Request Process

### Before Submitting

1. **Run the full test suite**
   ```bash
   pytest
   flake8 .
   black --check .
   mypy api/
   ```

2. **Update documentation** if your changes affect:
   - API endpoints
   - Configuration options
   - Installation procedures
   - Usage examples

3. **Add tests** for new functionality

4. **Check breaking changes** and update version accordingly

### PR Guidelines

1. **Title**: Use clear, descriptive titles
   - ✅ `Add support for custom font loading`
   - ❌ `Fix stuff`

2. **Description**: Include:
   - What changes were made
   - Why the changes were necessary
   - How to test the changes
   - Screenshots for UI changes
   - Breaking changes (if any)

3. **Size**: Keep PRs focused and reasonably sized
   - Prefer multiple small PRs over one large PR
   - Separate bug fixes from feature additions

4. **Commits**: Use conventional commit messages
   ```
   feat: add custom font support for carousel generation
   fix: resolve memory leak in image processing
   docs: update API documentation for new endpoints
   test: add integration tests for AI config generation
   ```

### PR Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## How Has This Been Tested?
- [ ] Unit tests
- [ ] Integration tests
- [ ] Manual testing

## Screenshots (if applicable)
Add screenshots to show the changes.

## Checklist
- [ ] My code follows the style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

## 🐛 Issue Reporting

### Bug Reports

When reporting bugs, include:

1. **Environment details**:
   - OS and version
   - Python version
   - Package versions (`pip freeze`)

2. **Steps to reproduce**:
   - Exact steps to reproduce the issue
   - Expected vs actual behavior
   - Error messages (full stack trace)

3. **Minimal example**:
   - Provide minimal code that reproduces the issue
   - Include relevant configuration

### Feature Requests

For new features, include:

1. **Use case**: Describe the problem you're trying to solve
2. **Proposed solution**: How should it work?
3. **Alternatives**: What alternatives have you considered?
4. **Additional context**: Screenshots, mockups, examples

### Issue Templates

Use our issue templates for consistency:
- 🐛 Bug Report
- ✨ Feature Request
- 📝 Documentation Issue
- ❓ Question

## 🏷️ Labels and Milestones

We use labels to categorize issues and PRs:

- **Type**: `bug`, `enhancement`, `documentation`, `question`
- **Priority**: `critical`, `high`, `medium`, `low`
- **Component**: `api`, `ai`, `images`, `docs`, `tests`
- **Status**: `needs-review`, `work-in-progress`, `blocked`

## 🚀 Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backwards compatible)
- **PATCH**: Bug fixes (backwards compatible)

### Release Checklist

1. Update version in relevant files
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Update documentation
6. Create GitHub release
7. Build and push Docker images
8. Deploy to staging
9. Deploy to production

## 🎯 Development Tips

### Local Development

```bash
# Use development server with auto-reload
export FLASK_ENV=development
export FLASK_DEBUG=true
python app.py

# Or use Flask CLI
flask run --debug
```

### Docker Development

```bash
# Build development image
docker build -t carousel-api-dev .

# Run with volume mounting for live reload
docker run -p 5000:5000 -v $(pwd):/app carousel-api-dev
```

### Debugging

- Use Python debugger (`pdb`) for complex issues
- Add logging statements for tracing execution
- Use Flask's debug mode for development
- Check logs in `logs/` directory

### Performance Considerations

- **Image Processing**: Use efficient PIL operations
- **Memory Usage**: Clean up large objects after use
- **API Response Times**: Aim for <2s response times
- **Rate Limiting**: Test with high concurrency

## 📚 Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Pillow Documentation](https://pillow.readthedocs.io/)
- [OpenAI API Documentation](https://platform.openai.com/docs/)

### Tools
- [Black Code Formatter](https://black.readthedocs.io/)
- [Flake8 Linter](https://flake8.pycqa.org/)
- [Pytest Testing Framework](https://pytest.org/)
- [MyPy Type Checker](https://mypy.readthedocs.io/)

### Community
- 💬 [Discussions](https://github.com/yourusername/api-threads-carousel/discussions)
- 🐛 [Issues](https://github.com/yourusername/api-threads-carousel/issues)
- 📧 Email: support@apithreads.ru

## ❓ Questions?

If you have questions about contributing:

1. Check the [FAQ](docs/faq.md)
2. Search existing [issues](https://github.com/yourusername/api-threads-carousel/issues)
3. Start a [discussion](https://github.com/yourusername/api-threads-carousel/discussions)
4. Contact the maintainers

Thank you for contributing to API Threads Carousel Generator! 🎉
