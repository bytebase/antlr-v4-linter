# ANTLR v4 Grammar Linter

[![PyPI version](https://badge.fury.io/py/antlr-v4-linter.svg)](https://badge.fury.io/py/antlr-v4-linter)
[![Python versions](https://img.shields.io/pypi/pyversions/antlr-v4-linter.svg)](https://pypi.org/project/antlr-v4-linter/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive static analysis linter for ANTLR v4 grammar files (.g4) that identifies common issues, enforces best practices, and improves grammar quality and maintainability.

## ✨ Features

- **24 Built-in Rules** across 8 categories for comprehensive grammar analysis
- **Configurable Rule Severity** - Set rules as error, warning, or info
- **Multiple Output Formats** - Text (with colors), JSON, XML, SARIF
- **Smart Detection** - Identifies naming issues, complexity problems, performance bottlenecks
- **Flexible Configuration** - JSON-based configuration with rule-specific thresholds
- **CLI and Programmatic APIs** - Use as command-line tool or Python library

## 📦 Installation

```bash
# Using pip
pip install antlr-v4-linter

# Using uv (faster)
uv pip install antlr-v4-linter

# Using pipx (isolated environment)
pipx install antlr-v4-linter
```

## 🚀 Quick Start

```bash
# Lint a single grammar file
antlr-lint lint MyGrammar.g4

# Lint multiple files or directories
antlr-lint lint src/
antlr-lint lint "*.g4"

# Use custom configuration
antlr-lint lint --config antlr-lint.json MyGrammar.g4

# Output in different formats
antlr-lint lint --format json MyGrammar.g4
antlr-lint lint --format xml MyGrammar.g4

# List all available rules
antlr-lint rules

# Create a configuration file
antlr-lint init
```

## 📋 Available Rules

The linter includes **24 rules** organized into 8 categories:

### Syntax and Structure (S001-S003)
- **S001**: Missing EOF token - Main parser rule should end with EOF
- **S002**: Incomplete input parsing - Lexer should have catch-all rule
- **S003**: Ambiguous string literals - Same literal in multiple lexer rules

### Naming and Convention (N001-N003)
- **N001**: Parser rule naming - Must start with lowercase letter
- **N002**: Lexer rule naming - Must start with uppercase letter
- **N003**: Inconsistent naming convention - Mixed camelCase/snake_case

### Labeling and Organization (L001-L003)
- **L001**: Missing alternative labels - Multi-alternative rules need labels
- **L002**: Inconsistent label naming - Labels should follow consistent style
- **L003**: Duplicate labels - Labels must be unique within rule

### Complexity and Maintainability (C001-C003)
- **C001**: Excessive complexity - Rules exceed configurable thresholds
- **C002**: Deeply nested rule - Too many nesting levels
- **C003**: Very long rule - Rule definition spans too many lines

### Token and Lexer (T001-T003)
- **T001**: Overlapping tokens - Token definitions may conflict
- **T002**: Unreachable token - Token shadowed by earlier rules
- **T003**: Unused token - Token defined but never used

### Error Handling (E001-E002)
- **E001**: Missing error recovery - No error handling strategies
- **E002**: Potential ambiguity - Grammar may have ambiguous paths

### Performance (P001-P002)
- **P001**: Excessive backtracking - Patterns causing performance issues
- **P002**: Inefficient lexer pattern - Suboptimal regular expressions

### Documentation (D001-D002)
- **D001**: Missing rule documentation - Complex rules lack comments
- **D002**: Missing grammar header - No file-level documentation

## ⚙️ Configuration

Create an `antlr-lint.json` file in your project root:

```json
{
  "rules": {
    "S001": { "enabled": true, "severity": "error" },
    "N001": { "enabled": true, "severity": "error" },
    "C001": { 
      "enabled": true, 
      "severity": "warning",
      "thresholds": {
        "maxAlternatives": 10,
        "maxNestingDepth": 5,
        "maxTokens": 50
      }
    }
  },
  "excludePatterns": ["*.generated.g4", "build/**/*.g4"],
  "outputFormat": "text"
}
```

### Configuration Options

- **rules**: Configure individual rules with `enabled`, `severity`, and rule-specific `thresholds`
- **excludePatterns**: Glob patterns for files to skip
- **outputFormat**: Choose between `text`, `json`, `xml`, or `sarif`

Generate a default configuration:
```bash
antlr-lint init
```

## 🐍 Programmatic API

Use the linter in your Python code:

```python
from antlr_v4_linter import ANTLRLinter, LinterConfig

# Create linter with default config
linter = ANTLRLinter()

# Or with custom config
config = LinterConfig.from_file("antlr-lint.json")
linter = ANTLRLinter(config)

# Lint a single file
result = linter.lint_file("MyGrammar.g4")
print(f"Found {result.total_issues} issues")

# Lint multiple files
results = linter.lint_files(["Grammar1.g4", "Grammar2.g4"])
for result in results:
    print(f"{result.file_path}: {result.error_count} errors, {result.warning_count} warnings")
```

## 🔧 Development

```bash
# Clone the repository
git clone https://github.com/bytebase/antlr-v4-linter.git
cd antlr-v4-linter

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/

# Build package
python -m build
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- The ANTLR project and community for the excellent parser generator
- All contributors who help improve this linter

## 🔗 Links

- **PyPI Package**: https://pypi.org/project/antlr-v4-linter/
- **GitHub Repository**: https://github.com/bytebase/antlr-v4-linter
- **Issue Tracker**: https://github.com/bytebase/antlr-v4-linter/issues
- **ANTLR Documentation**: https://www.antlr.org/

## 📊 Project Status

- ✅ All 24 rules implemented
- ✅ Published to PyPI
- ✅ Comprehensive test coverage
- ✅ GitHub Actions CI/CD
- 🚧 IDE extensions (coming soon)
- 🚧 Auto-fix capabilities (coming soon)

## 🚀 GitHub Actions Integration

The project includes automated CI/CD workflows:

### Automatic Release on Tag

When you push a version tag (e.g., `0.1.3`), the package is automatically:
1. Built and tested
2. Published to Test PyPI
3. Published to Production PyPI
4. GitHub Release created

```bash
# Create and push a version tag
git tag 0.1.3
git push origin 0.1.3
```

### Manual Release

Use the "Manual Release" workflow in GitHub Actions:
1. Go to Actions → Manual Release
2. Click "Run workflow"
3. Enter version number
4. Choose whether to test on Test PyPI first

### Continuous Integration

All pushes and pull requests run:
- Multi-platform tests (Linux, macOS)
- Python 3.8-3.12 compatibility tests
- Code quality checks (black, isort, flake8, mypy)