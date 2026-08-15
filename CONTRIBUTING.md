# Contributing to AIOps MVP

Thank you for your interest in contributing! Here's how to get started.

## Development Setup

```bash
# Clone repository
git clone https://github.com/yourusername/aiops-mvp.git
cd aiops-mvp

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies + dev tools
pip install -r requirements.txt
pip install pytest pytest-cov black flake8
```

## Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Keep commits atomic and focused
   - Write clear commit messages

3. **Test your changes**
   ```bash
   pytest tests/
   ```

4. **Format code**
   ```bash
   black src/
   flake8 src/
   ```

## Commit Guidelines

- Use clear, descriptive commit messages
- Reference issues when relevant: `Fixes #123`
- Format: `type(scope): description`
  - `feat(detect): add new anomaly detector`
  - `fix(pipeline): handle edge case in preprocessing`
  - `docs(readme): update installation instructions`

## Pull Request Process

1. Push to your fork
2. Create Pull Request with clear description
3. Reference any related issues
4. Wait for CI checks to pass
5. Request review from maintainers

## Code Style

- Follow PEP 8
- Use type hints where possible
- Add docstrings to functions
- Keep lines under 100 characters

## Testing

- Write tests for new features
- Aim for >80% code coverage
- Run `pytest` before submitting PR

## Questions?

Open an issue for questions or discussions.

Thanks for contributing! 🎉
