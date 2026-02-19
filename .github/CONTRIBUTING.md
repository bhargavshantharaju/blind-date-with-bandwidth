# Contributing to Blind Date with Bandwidth

Thank you for your interest in contributing! This project welcomes contributions from anyone.

## Development Setup

1. Fork the repository
2. Clone your fork: `git clone https://github.com/yourusername/blind-date-with-bandwidth.git`
3. Create a feature branch: `git checkout -b feature/your-feature`
4. Install dependencies: `cd raspberry_pi_server && pip install -r requirements.txt`
5. Run tests: `pytest tests/`
6. Make your changes
7. Run tests again: `pytest tests/`
8. Format code: `black raspberry_pi_server/`
9. Commit: `git commit -m "feat: your feature description"`
10. Push: `git push origin feature/your-feature`
11. Create Pull Request

## Code Style

- Python: Black formatter, flake8 linting
- Arduino: 2-space indentation, descriptive comments
- Commit messages: Conventional commits (feat:, fix:, docs:, etc.)

## Testing

- Unit tests required for new features
- Test coverage >80%
- Manual testing on hardware before PR

## Hardware Contributions

- Document any hardware modifications
- Update BOM if adding components
- Provide wiring diagrams for changes

## Reporting Issues

Use the issue templates for bugs and features. Include:
- Hardware setup
- Software versions
- Steps to reproduce
- Expected vs actual behavior