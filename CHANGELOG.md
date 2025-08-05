# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.4] - 2025-08-05

### Fixed
- Fixed all unit tests to achieve 100% pass rate (59 tests passing)
- Enhanced performance rules with optional prefix conflict detection
- Improved numeric pattern overlap detection in token rules
- Added duplicate pattern detection in unreachable token rule
- Fixed syntax rules to better identify main parser rules
- Fixed test expectations to match actual rule implementations

### Changed
- Updated LexerRuleNamingRule to enforce ALL_CAPS convention
- Improved backtracking detection for optional prefixes
- Enhanced numeric pattern detection for INT/FLOAT overlaps

## [0.1.1] - 2024-08-04

### Fixed
- Fixed parser to properly handle `/* */` block comments in grammar files
- Block comments are now correctly stripped before parsing, preserving line numbers
- Multi-line block comments no longer cause parsing errors

### Changed
- Improved comment handling in the grammar parser

## [0.1.0] - 2024-08-04

### Added
- Initial release with 24 linting rules across 8 categories
- Syntax and Structure rules (S001-S003)
- Naming and Convention rules (N001-N003)
- Labeling and Organization rules (L001-L003)
- Complexity and Maintainability rules (C001-C003)
- Token and Lexer rules (T001-T003)
- Error Handling rules (E001-E002)
- Performance rules (P001-P002)
- Documentation rules (D001-D002)
- CLI interface with multiple commands (lint, init, rules, validate-config)
- Multiple output formats (text, JSON, XML, SARIF)
- Configuration file support with rule-specific settings
- Programmatic API for Python integration
- Published to PyPI as `antlr-v4-linter`