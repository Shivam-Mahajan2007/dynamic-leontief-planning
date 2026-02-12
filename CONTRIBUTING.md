# Contributing to Dynamic Input–Output Planning Model

Thank you for your interest in contributing! This project welcomes contributions from the community.

## Ways to Contribute

### 1. Report Bugs
Found a bug? Please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs. actual behavior
- Your environment (OS, Python version, etc.)

### 2. Suggest Enhancements
Have an idea? Open an issue describing:
- The feature or enhancement
- Why it would be useful
- Possible implementation approach

### 3. Submit Code
Pull requests are welcome! Please:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Make your changes**
4. **Add tests** if applicable
5. **Update documentation** if needed
6. **Commit with clear messages** (`git commit -m 'Add amazing feature'`)
7. **Push to your fork** (`git push origin feature/amazing-feature`)
8. **Open a Pull Request**

## Code Standards

### Python Style
- Follow PEP 8
- Use meaningful variable names
- Add docstrings to all functions
- Maximum line length: 100 characters

### Documentation
- Update README.md if adding features
- Add examples for new functionality
- Comment complex algorithms

### Testing
- Add unit tests for new functions
- Ensure existing tests pass
- Test with different parameter configurations

## Priority Areas

We especially welcome contributions in:

### Data Adapters
- Loaders for other countries' IO tables
- Converters for different IO table formats
- Integration with OECD, Eurostat databases

### Performance
- Optimization for large-scale systems (n > 10,000)
- Parallelization of Neumann series
- GPU acceleration for matrix operations

### Visualization
- Interactive dashboards
- Real-time monitoring tools
- Comparative analysis plots

### Extensions
- International trade module
- Multi-tier planning systems
- Advanced demand forecasting methods

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/dynamic-leontief-planning.git
cd dynamic-leontief-planning

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# Run tests
python -m pytest tests/
```

## Commit Messages

Use clear, descriptive commit messages:

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Formatting, no code change
- **refactor**: Code restructuring
- **test**: Adding tests
- **chore**: Maintenance tasks

Examples:
```
feat: add support for quarterly planning frequency
fix: correct Neumann series convergence check
docs: update installation instructions for Windows
```

## Questions?

Feel free to:
- Open an issue for discussion
- Email the maintainers
- Join our [discussion forum/slack/discord] (if applicable)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Focus on constructive feedback
- Respect differing viewpoints

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for helping improve this project! 🎉
