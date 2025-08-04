import fnmatch
from pathlib import Path
from typing import List, Union

from .models import GrammarAST, LintResult, LinterConfig
from .parser import SimpleGrammarParser
from .reporter import Reporter, ReporterFactory
from .rule_engine import RuleEngine


class ANTLRLinter:
    """Main linter class that coordinates parsing, rule checking, and reporting."""
    
    def __init__(self, config: LinterConfig = None):
        self.config = config or LinterConfig.default()
        self.parser = SimpleGrammarParser()
        self.rule_engine = RuleEngine()
        self._register_default_rules()
    
    def _register_default_rules(self) -> None:
        """Register all default linting rules."""
        from ..rules.syntax_rules import (
            MissingEOFRule,
            IncompleteInputParsingRule,
            AmbiguousStringLiteralsRule
        )
        from ..rules.naming_rules import (
            ParserRuleNamingRule,
            LexerRuleNamingRule,
            InconsistentNamingRule
        )
        from ..rules.labeling_rules import (
            MissingAlternativeLabelsRule,
            InconsistentLabelNamingRule,
            DuplicateLabelsRule
        )
        from ..rules.complexity_rules import (
            ExcessiveComplexityRule,
            DeeplyNestedRuleRule,
            VeryLongRuleRule
        )
        from ..rules.token_rules import (
            OverlappingTokensRule,
            UnreachableTokenRule,
            UnusedTokenRule
        )
        from ..rules.error_handling_rules import (
            MissingErrorRecoveryRule,
            PotentialAmbiguityRule
        )
        from ..rules.performance_rules import (
            BacktrackingRule,
            InefficientLexerRule
        )
        from ..rules.documentation_rules import (
            MissingRuleDocumentationRule,
            MissingGrammarHeaderRule
        )
        
        # Register all rules
        rules = [
            # Syntax and Structure (S001-S003)
            MissingEOFRule(),
            IncompleteInputParsingRule(),
            AmbiguousStringLiteralsRule(),
            
            # Naming and Convention (N001-N003)
            ParserRuleNamingRule(),
            LexerRuleNamingRule(),
            InconsistentNamingRule(),
            
            # Labeling and Organization (L001-L003)
            MissingAlternativeLabelsRule(),
            InconsistentLabelNamingRule(),
            DuplicateLabelsRule(),
            
            # Complexity and Maintainability (C001-C003)
            ExcessiveComplexityRule(),
            DeeplyNestedRuleRule(),
            VeryLongRuleRule(),
            
            # Token and Lexer (T001-T003)
            OverlappingTokensRule(),
            UnreachableTokenRule(),
            UnusedTokenRule(),
            
            # Error Handling (E001-E002)
            MissingErrorRecoveryRule(),
            PotentialAmbiguityRule(),
            
            # Performance (P001-P002)
            BacktrackingRule(),
            InefficientLexerRule(),
            
            # Documentation (D001-D002)
            MissingRuleDocumentationRule(),
            MissingGrammarHeaderRule(),
        ]
        
        self.rule_engine.register_rules(rules)
    
    def lint_file(self, file_path: str) -> LintResult:
        """Lint a single grammar file."""
        # Check if file should be excluded
        if self._should_exclude_file(file_path):
            return LintResult(file_path=file_path, issues=[])
        
        try:
            # Parse the grammar
            grammar = self.parser.parse_file(file_path)
            
            # Run linting rules
            issues = self.rule_engine.run_rules(grammar, self.config)
            
            return LintResult(file_path=file_path, issues=issues)
        
        except Exception as e:
            # Create an error issue for parsing failures
            from .models import Issue, Position, Range, Severity
            
            error_issue = Issue(
                rule_id="PARSE_ERROR",
                severity=Severity.ERROR,
                message=f"Failed to parse grammar file: {str(e)}",
                file_path=file_path,
                range=Range(Position(1, 1), Position(1, 1))
            )
            
            return LintResult(file_path=file_path, issues=[error_issue])
    
    def lint_files(self, file_paths: List[str]) -> List[LintResult]:
        """Lint multiple grammar files."""
        results = []
        
        for file_path in file_paths:
            result = self.lint_file(file_path)
            results.append(result)
        
        return results
    
    def lint_directory(self, directory: str, pattern: str = "*.g4") -> List[LintResult]:
        """Lint all grammar files in a directory."""
        directory_path = Path(directory)
        
        if not directory_path.exists() or not directory_path.is_dir():
            raise ValueError(f"Directory not found: {directory}")
        
        # Find all .g4 files
        file_paths = []
        for file_path in directory_path.rglob(pattern):
            if file_path.is_file():
                file_paths.append(str(file_path))
        
        return self.lint_files(file_paths)
    
    def _should_exclude_file(self, file_path: str) -> bool:
        """Check if file should be excluded based on patterns."""
        file_name = Path(file_path).name
        
        for pattern in self.config.exclude_patterns:
            if fnmatch.fnmatch(file_name, pattern):
                return True
        
        return False
    
    def format_results(self, results: List[LintResult], format_name: str = None) -> str:
        """Format lint results using the specified reporter."""
        format_name = format_name or self.config.output_format
        reporter = ReporterFactory.create_reporter(format_name)
        return reporter.format_results(results)
    
    def print_results(self, results: List[LintResult], use_colors: bool = True) -> None:
        """Print results to console with optional colors."""
        from .reporter import TextReporter
        
        reporter = TextReporter(use_colors=use_colors)
        if hasattr(reporter, 'format_results_rich') and use_colors:
            reporter.format_results_rich(results)
        else:
            print(reporter.format_results(results))
    
    def register_rule(self, rule) -> None:
        """Register a custom linting rule."""
        self.rule_engine.register_rule(rule)
    
    def get_rule_engine(self) -> RuleEngine:
        """Get the rule engine for advanced usage."""
        return self.rule_engine
    
    def get_config(self) -> LinterConfig:
        """Get the current configuration."""
        return self.config
    
    def update_config(self, config: LinterConfig) -> None:
        """Update the linter configuration."""
        self.config = config