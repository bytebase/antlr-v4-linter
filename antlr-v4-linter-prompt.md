# ANTLR v4 Grammar Linter Design Prompt

## Overview
Design and implement a comprehensive static analysis linter for ANTLR v4 grammar files (.g4) that identifies common issues, enforces best practices, and improves grammar quality and maintainability.

## Linter Architecture

### Core Components
1. **Grammar Parser**: Parse .g4 files into an AST representation
2. **Rule Engine**: Execute configurable linting rules against the AST
3. **Reporter**: Generate formatted output with issues, locations, and suggestions
4. **Configuration Manager**: Handle rule configuration and severity levels

### Target Files
- Combined grammars (.g4 files)
- Lexer grammars (.g4 files with lexer rules)
- Parser grammars (.g4 files with parser rules)

## Linting Rule Categories

### 1. Syntax and Structure Rules

#### S001: Missing EOF Token
- **Issue**: Main parser rule doesn't consume EOF token
- **Detection**: Check if top-level parser rules end with EOF
- **Severity**: Error
- **Fix**: Add EOF to the end of main parser rules

#### S002: Incomplete Input Parsing  
- **Issue**: Grammar doesn't handle all possible input
- **Detection**: Missing ANY rule at end of lexer
- **Severity**: Warning
- **Fix**: Add `ANY: . ;` as last lexer rule

#### S003: Ambiguous String Literals
- **Issue**: Same string literal used in multiple lexer rules
- **Detection**: Duplicate string literals across lexer rules
- **Severity**: Error
- **Fix**: Consolidate or differentiate string literals

### 2. Naming and Convention Rules

#### N001: Parser Rule Naming
- **Issue**: Parser rules don't start with lowercase
- **Detection**: Parser rules starting with uppercase
- **Severity**: Error
- **Fix**: Convert first character to lowercase

#### N002: Lexer Rule Naming
- **Issue**: Lexer rules don't start with uppercase
- **Detection**: Lexer rules starting with lowercase
- **Severity**: Error
- **Fix**: Convert first character to uppercase

#### N003: Inconsistent Naming Convention
- **Issue**: Mixed naming styles (camelCase vs snake_case)
- **Detection**: Pattern analysis across rule names
- **Severity**: Warning
- **Fix**: Suggest consistent naming convention

### 3. Labeling and Organization Rules

#### L001: Missing Alternative Labels
- **Issue**: Complex rules without alternative labels
- **Detection**: Rules with multiple alternatives lacking labels
- **Severity**: Warning
- **Fix**: Add #label syntax to alternatives

#### L002: Missing Element Labels
- **Issue**: Important rule elements without labels
- **Detection**: Unlabeled elements in complex rules
- **Severity**: Info
- **Fix**: Add element=rule syntax

#### L003: Unused Labels
- **Issue**: Labels defined but never referenced
- **Detection**: Label usage analysis
- **Severity**: Warning
- **Fix**: Remove unused labels or add usage

### 4. Complexity and Maintainability Rules

#### C001: Overly Complex Rules
- **Issue**: Rules with excessive complexity
- **Detection**: Count alternatives, nesting depth, rule length
- **Thresholds**: >10 alternatives, >5 nesting levels, >50 tokens
- **Severity**: Warning
- **Fix**: Suggest rule decomposition

#### C002: Deep Left Recursion
- **Issue**: Potentially problematic left recursion patterns
- **Detection**: Analyze recursion depth and patterns
- **Severity**: Warning
- **Fix**: Suggest refactoring to right recursion or iteration

#### C003: Redundant Rules
- **Issue**: Rules that duplicate functionality
- **Detection**: Structural similarity analysis
- **Severity**: Info
- **Fix**: Suggest rule consolidation

### 5. Token and Lexer Rules

#### T001: Inadequate Token Definitions
- **Issue**: Vague or overly broad token patterns
- **Detection**: Check for common token patterns (ID, NUMBER, STRING)
- **Severity**: Warning
- **Fix**: Provide specific token pattern suggestions

#### T002: Missing Whitespace Handling
- **Issue**: No whitespace skip rules defined
- **Detection**: Absence of WS skip rules
- **Severity**: Warning
- **Fix**: Add standard whitespace skip rule

#### T003: Lexer Mode Usage
- **Issue**: Complex lexer without proper mode usage
- **Detection**: Complex lexer rules without mode organization
- **Severity**: Info
- **Fix**: Suggest lexer mode refactoring

### 6. Error Handling and Robustness Rules

#### E001: Missing Error Recovery
- **Issue**: No error recovery mechanisms
- **Detection**: Absence of error handling rules
- **Severity**: Info
- **Fix**: Suggest adding error recovery rules

#### E002: Inadequate Error Productions
- **Issue**: Limited error handling alternatives
- **Detection**: Missing error alternatives in critical rules
- **Severity**: Warning
- **Fix**: Add error production suggestions

### 7. Performance and Optimization Rules

#### P001: Inefficient Rule Ordering
- **Issue**: Common alternatives placed after rare ones
- **Detection**: Analyze alternative ordering patterns
- **Severity**: Info
- **Fix**: Suggest reordering for performance

#### P002: Excessive Backtracking Potential
- **Issue**: Rules that may cause excessive backtracking
- **Detection**: Identify ambiguous rule patterns
- **Severity**: Warning
- **Fix**: Suggest disambiguation techniques

### 8. Documentation and Comments Rules

#### D001: Missing Rule Documentation
- **Issue**: Complex rules without documentation
- **Detection**: Rules above complexity threshold without comments
- **Severity**: Info
- **Fix**: Suggest adding rule documentation

#### D002: Outdated Comments
- **Issue**: Comments that don't match rule implementation
- **Detection**: Comment-code consistency analysis
- **Severity**: Warning
- **Fix**: Update comment suggestions

## Implementation Requirements

### Input Processing
- Parse .g4 files using ANTLR's own grammar parser
- Build comprehensive AST representation
- Handle syntax errors gracefully
- Support multiple file processing

### Rule Configuration
```json
{
  "rules": {
    "S001": { "enabled": true, "severity": "error" },
    "N001": { "enabled": true, "severity": "error" },
    "L001": { "enabled": true, "severity": "warning" },
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
  "outputFormat": "json" // json, xml, text, sarif
}
```

### Output Format
```json
{
  "file": "MyGrammar.g4",
  "issues": [
    {
      "ruleId": "S001",
      "severity": "error",
      "message": "Main parser rule 'program' should end with EOF token",
      "line": 15,
      "column": 1,
      "endLine": 15,
      "endColumn": 20,
      "suggestions": [
        {
          "description": "Add EOF token",
          "fix": "program: statement* EOF;"
        }
      ]
    }
  ],
  "summary": {
    "totalIssues": 5,
    "errorCount": 2,
    "warningCount": 2,
    "infoCount": 1
  }
}
```

### Integration Points
- Command-line interface
- IDE extensions (VS Code, IntelliJ)
- CI/CD pipeline integration
- Build tool plugins (Maven, Gradle, npm)

### Testing Strategy
- Unit tests for each linting rule
- Integration tests with real-world grammars
- Performance tests with large grammar files
- Regression tests for known issues

## Advanced Features

### Auto-fixing
- Implement safe automatic fixes for deterministic issues
- Provide fix suggestions for complex issues
- Support batch fixing across multiple files

### Metrics Collection
- Grammar complexity metrics
- Rule usage statistics  
- Maintainability index calculation
- Historical trend analysis

### Custom Rules
- Plugin architecture for custom rules
- Rule development SDK
- Community rule sharing platform

## Quality Criteria

### Accuracy
- Minimize false positives (< 5%)
- Comprehensive issue detection (> 95% coverage)
- Accurate location reporting

### Performance  
- Process large grammars (>1000 rules) in < 5 seconds
- Memory usage < 100MB for typical grammars
- Incremental analysis support

### Usability
- Clear, actionable error messages
- Helpful fix suggestions
- Configurable rule severity
- Multiple output formats

## Success Metrics
- Reduction in grammar compilation errors
- Improved grammar maintainability scores
- Faster development iteration cycles
- Increased developer adoption rates

## Implementation Priority
1. **Phase 1**: Core syntax and structure rules (S001-S003, N001-N003)
2. **Phase 2**: Labeling and complexity rules (L001-L003, C001-C003)
3. **Phase 3**: Token and error handling rules (T001-T003, E001-E002)
4. **Phase 4**: Performance and documentation rules (P001-P002, D001-D002)
5. **Phase 5**: Advanced features (auto-fixing, metrics, custom rules)