# Contributing to Financial Integrity Ecosystem

Thanks for your interest in contributing! This project is a test automation framework built as a portfolio/educational project, and contributions are welcome.

## How to Contribute

### Reporting Bugs

1. Check existing [Issues](https://github.com/Yaniv2809/Financial-Integrity-Ecosystem/issues) to avoid duplicates
2. Use the **Bug Report** issue template
3. Include steps to reproduce, expected vs actual behavior, and your environment details

### Suggesting Features

1. Open an issue using the **Feature Request** template
2. Describe the use case and how it improves the framework

### Submitting Code

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Follow existing code patterns (POM, Action/Verification separation, `@allure.step` decorators)
4. Add tests for new functionality
5. Ensure all tests pass: `pytest -m "not mobile"`
6. Submit a Pull Request with a clear description

## Development Setup

```bash
git clone https://github.com/Yaniv2809/Financial-Integrity-Ecosystem.git
cd Financial-Integrity-Ecosystem
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
playwright install chromium
docker-compose up -d mysql
```

## Code Style

- All test methods: `@allure.title`, `@allure.description`, `@allure.severity`
- Actions/Verifications: `@staticmethod` with `@allure.step`
- Page Objects: locator constants only — no driver interaction
- Data files: CSV for Web, JSON for API/Mobile, filtered by `test_id`

## Questions?

Open an issue with the **Question** label or reach out via the repository discussions.
