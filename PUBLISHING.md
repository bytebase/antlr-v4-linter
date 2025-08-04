# Publishing ANTLR v4 Linter to PyPI

This guide explains how to publish the `antlr-v4-linter` package to PyPI so it can be installed via `uv pip install` or `pip install`.

## Prerequisites

1. **PyPI Account**: Create an account at https://pypi.org if you don't have one
2. **Test PyPI Account** (optional but recommended): Create an account at https://test.pypi.org for testing
3. **API Token**: Generate an API token from PyPI (Account Settings → API tokens)

## Setup Publishing Tools with UV

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install build tools
uv pip install --upgrade build twine
```

## Step 1: Update Version

Update the version in `pyproject.toml`:
```toml
[project]
name = "antlr-v4-linter"
version = "0.1.0"  # Increment this for each release
```

## Step 2: Build the Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build the package
python -m build

# This creates:
# - dist/antlr_v4_linter-0.1.0-py3-none-any.whl
# - dist/antlr_v4_linter-0.1.0.tar.gz
```

## Step 3: Test Installation Locally

```bash
# Create a test virtual environment
uv venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from the wheel file
uv pip install dist/antlr_v4_linter-0.1.0-py3-none-any.whl

# Test the installation
antlr-lint --version
antlr-lint --help

# Deactivate when done
deactivate
```

## Step 4: Upload to Test PyPI (Optional but Recommended)

```bash
# Upload to test.pypi.org first
python -m twine upload --repository testpypi dist/*

# You'll be prompted for:
# - Username: __token__
# - Password: <your-test-pypi-token>
```

Test installation from Test PyPI:
```bash
uv pip install --index-url https://test.pypi.org/simple/ antlr-v4-linter
```

## Step 5: Upload to PyPI

```bash
# Upload to PyPI
python -m twine upload dist/*

# You'll be prompted for:
# - Username: __token__
# - Password: <your-pypi-token>
```

## Step 6: Verify Installation

After uploading, anyone can install the package:

```bash
# Using uv
uv pip install antlr-v4-linter

# Using pip
pip install antlr-v4-linter
```

## Using a .pypirc File (Optional)

To avoid entering credentials each time, create `~/.pypirc`:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-<your-token-here>

[testpypi]
username = __token__
password = pypi-<your-test-token-here>
```

Set proper permissions:
```bash
chmod 600 ~/.pypirc
```

Then upload without prompts:
```bash
python -m twine upload dist/*
python -m twine upload --repository testpypi dist/*
```

## GitHub Actions for Automated Publishing (Optional)

Create `.github/workflows/publish.yml`:

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: python -m twine upload dist/*
```

Add your PyPI token as a GitHub secret: Settings → Secrets → New repository secret → Name: `PYPI_API_TOKEN`

## Version Management

Follow semantic versioning:
- **MAJOR.MINOR.PATCH** (e.g., 1.2.3)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

For pre-releases:
- Alpha: `0.1.0a1`
- Beta: `0.1.0b1`
- Release Candidate: `0.1.0rc1`

## Checklist Before Publishing

- [ ] All tests pass: `pytest`
- [ ] Code is formatted: `black src/ tests/`
- [ ] Imports are sorted: `isort src/ tests/`
- [ ] Type checking passes: `mypy src/`
- [ ] Version number is updated in `pyproject.toml`
- [ ] CHANGELOG is updated with release notes
- [ ] README is up-to-date
- [ ] Package installs correctly locally
- [ ] CLI commands work as expected

## Troubleshooting

### Package Name Already Taken
If `antlr-v4-linter` is taken, consider:
- `antlr4-linter`
- `antlr-grammar-linter`
- `antlr4-grammar-linter`

Update the name in `pyproject.toml`:
```toml
[project]
name = "your-new-package-name"
```

### Missing Dependencies
Ensure all dependencies are listed in `pyproject.toml`:
```toml
dependencies = [
    "antlr4-python3-runtime>=4.13.0",
    "click>=8.0.0",
    "pydantic>=2.0.0",
    "rich>=13.0.0",
]
```

### Module Import Errors
Verify the package structure:
```
src/
└── antlr_v4_linter/
    ├── __init__.py
    ├── cli/
    ├── core/
    └── rules/
```

## Quick Publishing Commands

```bash
# Complete publishing workflow
uv pip install --upgrade build twine
rm -rf dist/ build/
python -m build
python -m twine check dist/*
python -m twine upload dist/*
```

## After Publishing

1. **Test Installation**: `uv pip install antlr-v4-linter`
2. **Check PyPI Page**: https://pypi.org/project/antlr-v4-linter/
3. **Create GitHub Release**: Tag the version and create release notes
4. **Announce**: Share on social media, forums, etc.

## Support

For issues with publishing, check:
- PyPI Documentation: https://packaging.python.org/
- UV Documentation: https://github.com/astral-sh/uv
- Twine Documentation: https://twine.readthedocs.io/