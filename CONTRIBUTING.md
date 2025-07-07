# Contributing to K8s Multi-Cluster Dashboard

Thank you for considering contributing to the K8s Multi-Cluster Dashboard! This document provides guidelines and instructions for contributing to this project.

## Code of Conduct

By participating in this project, you agree to abide by our code of conduct. Please be respectful and considerate of others.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue in the GitHub repository with the following information:

- A clear, descriptive title
- A detailed description of the issue
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Screenshots (if applicable)
- Environment information (OS, Python version, etc.)

### Suggesting Enhancements

We welcome suggestions for enhancements! Please create an issue with:

- A clear, descriptive title
- A detailed description of the proposed enhancement
- Any relevant examples or mockups

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature-name`)
3. Make your changes
4. Run tests and ensure they pass
5. Commit your changes (`git commit -m 'Add some feature'`)
6. Push to the branch (`git push origin feature/your-feature-name`)
7. Open a Pull Request

#### Pull Request Guidelines

- Follow the coding style of the project
- Include tests for new features
- Update documentation as needed
- Keep pull requests focused on a single topic
- Reference any relevant issues

## Development Setup

1. Clone the repository
2. Install uv if you don't have it already
3. Run `uv pip install -r requirements.txt` to set up the development environment
4. Run `source .venv/bin/activate` to activate the virtual environment

## Testing

Run tests with:

```bash
uv run pytest
```

## Code Style

This project uses:
- Black for code formatting
- isort for import sorting

You can run these tools with:

```bash
uv run black .
uv run ruff .
```

## Documentation

Please update documentation when making changes to the code. This includes:

- Code comments
- Function/method docstrings
- README updates (if applicable)

## License

By contributing to this project, you agree that your contributions will be licensed under the project's MIT License.
