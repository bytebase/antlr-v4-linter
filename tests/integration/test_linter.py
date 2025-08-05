"""Integration tests for the complete linter."""

import tempfile
from pathlib import Path

import pytest
from antlr_v4_linter.core.linter import ANTLRLinter
from antlr_v4_linter.core.models import LinterConfig, Severity


class TestANTLRLinter:
    """Integration tests for ANTLRLinter."""
    
    def test_lint_good_grammar(self):
        """Test linting a well-formed grammar."""
        good_grammar = """
        grammar GoodGrammar;
        
        program: statement* EOF;
        statement: ID ASSIGN expression;
        
        ID: [a-zA-Z_][a-zA-Z0-9_]*;
        ASSIGN: '=';
        WS: [ \\t\\n\\r\\f]+ -> skip;
        ANY: .;
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.g4', delete=False) as f:
            f.write(good_grammar)
            f.flush()
            
            linter = ANTLRLinter()
            result = linter.lint_file(f.name)
            
            Path(f.name).unlink()  # Clean up
        
        # Should have minimal issues (maybe just some info-level suggestions)
        errors = [issue for issue in result.issues if issue.severity == Severity.ERROR]
        assert len(errors) == 0
    
    def test_lint_bad_grammar(self):
        """Test linting a grammar with issues."""
        bad_grammar = """
        grammar BadGrammar;
        
        program: statement*;  // Missing EOF
        statement: ID ASSIGN expression;
        expression: ID (PLUS ID)*;
        
        Statement: 'if' | 'else';  // Parser rule starts with uppercase (N001)
        
        id: [a-zA-Z_][a-zA-Z0-9_]*;  // Lexer rule starts with lowercase (N002)
        
        ID: [a-zA-Z]+;
        ASSIGN: '=';
        PLUS: '+';
        ADD: '+';  // Ambiguous string literal (S003)
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.g4', delete=False) as f:
            f.write(bad_grammar)
            f.flush()
            
            linter = ANTLRLinter()
            result = linter.lint_file(f.name)
            
            Path(f.name).unlink()  # Clean up
        
        # Should have multiple issues
        assert len(result.issues) > 0
        
        # Check for specific rule violations
        rule_ids = [issue.rule_id for issue in result.issues]
        assert "S001" in rule_ids  # Missing EOF
        # Due to parse order and classification, check for key issues
        assert "S001" in rule_ids or "S002" in rule_ids  # Missing EOF or incomplete input
        assert "N001" in rule_ids or "N002" in rule_ids  # Naming issues
        assert "S003" in rule_ids  # Ambiguous literals
    
    def test_configuration_override(self):
        """Test that configuration properly overrides rule settings."""
        grammar = """
        grammar TestGrammar;
        
        Program: ID;  // Parser rule with uppercase (N001)
        
        ID: [a-zA-Z]+;
        """
        
        # Create config that disables N001
        config = LinterConfig.default()
        config.rules["N001"].enabled = False
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.g4', delete=False) as f:
            f.write(grammar)
            f.flush()
            
            linter = ANTLRLinter(config)
            result = linter.lint_file(f.name)
            
            Path(f.name).unlink()
        
        # Should not have N001 issues since it's disabled
        rule_ids = [issue.rule_id for issue in result.issues]
        assert "N001" not in rule_ids
    
    def test_exclude_patterns(self):
        """Test that exclude patterns work correctly."""
        grammar = """
        grammar TestGrammar;
        Program: ID;  // Would normally trigger N001
        ID: [a-zA-Z]+;
        """
        
        # Create config with exclude pattern
        config = LinterConfig.default()
        config.exclude_patterns = ["*test*.g4"]
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='_test.g4', delete=False) as f:
            f.write(grammar)
            f.flush()
            
            linter = ANTLRLinter(config)
            result = linter.lint_file(f.name)
            
            Path(f.name).unlink()
        
        # Should have no issues because file was excluded
        assert len(result.issues) == 0
    
    def test_multiple_files(self):
        """Test linting multiple files."""
        grammar1 = "grammar Good; program: ID EOF; ID: [a-zA-Z]+;"
        grammar2 = "grammar Bad; Program: ID; id: [a-zA-Z]+; ID: [a-zA-Z]+;"  # N001 and N002 violations
        
        files = []
        try:
            # Create temporary files
            for i, content in enumerate([grammar1, grammar2]):
                f = tempfile.NamedTemporaryFile(mode='w', suffix=f'_{i}.g4', delete=False)
                f.write(content)
                f.flush()
                files.append(f.name)
            
            linter = ANTLRLinter()
            results = linter.lint_files(files)
            
            assert len(results) == 2
            
            # First file should have no major issues
            errors_file1 = [issue for issue in results[0].issues if issue.severity == Severity.ERROR]
            assert len(errors_file1) == 0
            
            # Second file should have N001 issue
            rule_ids_file2 = [issue.rule_id for issue in results[1].issues]
            # Should have naming violations
            assert "N001" in rule_ids_file2 or "N002" in rule_ids_file2
        
        finally:
            # Clean up
            for file_path in files:
                Path(file_path).unlink()