# ANTLR v4 Grammar Linter

A comprehensive static analysis linter for ANTLR v4 grammar files (.g4) that identifies common issues, enforces best practices, and improves grammar quality and maintainability.

## Features

- **24 Built-in Rules** across 8 categories
- **Configurable Rule Severity** and thresholds
- **Multiple Output Formats** (JSON, XML, text, SARIF)
- **Auto-fixing** capabilities for deterministic issues
- **CLI and Programmatic APIs**
- **IDE Integration** ready

## Installation

```bash
pip install antlr-v4-linter
```

## Quick Start

```bash
# Lint a single grammar file
antlr-lint MyGrammar.g4

# Lint multiple files
antlr-lint src/**/*.g4

# Custom configuration
antlr-lint --config antlr-lint.json MyGrammar.g4

# JSON output
antlr-lint --format json MyGrammar.g4
```

## Rule Categories

1. **Syntax and Structure** (S001-S003)
2. **Naming and Convention** (N001-N003)  
3. **Labeling and Organization** (L001-L003)
4. **Complexity and Maintainability** (C001-C003)
5. **Token and Lexer** (T001-T003)
6. **Error Handling** (E001-E002)
7. **Performance** (P001-P002)
8. **Documentation** (D001-D002)

## Configuration

Create an `antlr-lint.json` file:

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
  "excludePatterns": ["*.generated.g4"],
  "outputFormat": "text"
}
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black src/ tests/
isort src/ tests/

# Type checking
mypy src/
```

## License

MIT License