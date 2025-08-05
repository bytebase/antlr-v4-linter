"""Comprehensive tests for naming rules."""

import pytest
from antlr_v4_linter.core.models import (
    GrammarAST, GrammarDeclaration, GrammarType, Position, Range,
    Rule, RuleConfig, Severity
)
from antlr_v4_linter.rules.naming_rules import (
    ParserRuleNamingRule, LexerRuleNamingRule, InconsistentNamingRule
)


class TestParserRuleNamingRule:
    """Test N001: Parser rule naming rule."""
    
    def test_detects_uppercase_parser_rule(self):
        """Test detection of parser rule starting with uppercase."""
        rule = ParserRuleNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.ERROR)
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="Program",  # Should be lowercase
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 20))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 1
        assert issues[0].rule_id == "N001"
        assert "lowercase" in issues[0].message
        assert len(issues[0].suggestions) > 0
        assert "program" in issues[0].suggestions[0].fix.lower()
    
    def test_accepts_lowercase_parser_rule(self):
        """Test that lowercase parser rules are accepted."""
        rule = ParserRuleNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.ERROR)
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="program",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 20))
                ),
                Rule(
                    name="statement",
                    is_lexer_rule=False,
                    range=Range(Position(4, 1), Position(4, 25))
                ),
                Rule(
                    name="expression_list",
                    is_lexer_rule=False,
                    range=Range(Position(5, 1), Position(5, 30))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0
    
    def test_detects_mixed_case_parser_rule(self):
        """Test detection of mixed case parser rule names."""
        rule = ParserRuleNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.ERROR)
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="myStatement",  # camelCase - should be snake_case
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 25))
                ),
                Rule(
                    name="MyOtherRule",  # PascalCase - wrong
                    is_lexer_rule=False,
                    range=Range(Position(4, 1), Position(4, 25))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        # Only PascalCase is flagged, camelCase is allowed
        assert len(issues) == 1
        assert issues[0].rule_id == "N001"
        assert "MyOtherRule" in issues[0].message
    
    def test_ignores_lexer_rules(self):
        """Test that lexer rules are ignored."""
        rule = ParserRuleNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.ERROR)
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="IDENTIFIER",  # Lexer rule - should be ignored
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 25))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0


class TestLexerRuleNamingRule:
    """Test N002: Lexer rule naming rule."""
    
    def test_detects_lowercase_lexer_rule(self):
        """Test detection of lexer rule starting with lowercase."""
        rule = LexerRuleNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.ERROR)
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="identifier",  # Should be uppercase
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 25))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 1
        assert issues[0].rule_id == "N002"
        assert "uppercase" in issues[0].message
        assert len(issues[0].suggestions) > 0
        assert "IDENTIFIER" in issues[0].suggestions[0].fix
    
    def test_accepts_uppercase_lexer_rule(self):
        """Test that uppercase lexer rules are accepted."""
        rule = LexerRuleNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.ERROR)
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="IDENTIFIER",
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 25))
                ),
                Rule(
                    name="NUMBER",
                    is_lexer_rule=True,
                    range=Range(Position(4, 1), Position(4, 20))
                ),
                Rule(
                    name="STRING_LITERAL",
                    is_lexer_rule=True,
                    range=Range(Position(5, 1), Position(5, 30))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0
    
    def test_detects_mixed_case_lexer_rule(self):
        """Test detection of mixed case lexer rule names."""
        rule = LexerRuleNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.ERROR)
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="MyToken",  # Mixed case - should be all caps
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 20))
                ),
                Rule(
                    name="stringLiteral",  # camelCase - wrong
                    is_lexer_rule=True,
                    range=Range(Position(4, 1), Position(4, 28))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 2
        assert all(issue.rule_id == "N002" for issue in issues)
    
    def test_ignores_parser_rules(self):
        """Test that parser rules are ignored."""
        rule = LexerRuleNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.ERROR)
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="program",  # Parser rule - should be ignored
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 20))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0


class TestInconsistentNamingRule:
    """Test N003: Inconsistent naming rule."""
    
    def test_detects_inconsistent_parser_rule_style(self):
        """Test detection of inconsistent parser rule naming styles."""
        rule = InconsistentNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.WARNING)
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="program",  # snake_case
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 20))
                ),
                Rule(
                    name="statement_list",  # snake_case with underscore
                    is_lexer_rule=False,
                    range=Range(Position(4, 1), Position(4, 30))
                ),
                Rule(
                    name="expressionList",  # camelCase - inconsistent!
                    is_lexer_rule=False,
                    range=Range(Position(5, 1), Position(5, 30))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 1
        assert issues[0].rule_id == "N003"
        # The rule flags statement_list as it doesn't follow the dominant camelCase style
        assert "doesn't follow" in issues[0].message.lower()
        assert "statement_list" in issues[0].message
    
    def test_accepts_consistent_snake_case(self):
        """Test that consistent snake_case is accepted."""
        rule = InconsistentNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.WARNING)
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="program",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 20))
                ),
                Rule(
                    name="statement_list",
                    is_lexer_rule=False,
                    range=Range(Position(4, 1), Position(4, 30))
                ),
                Rule(
                    name="expression_list",
                    is_lexer_rule=False,
                    range=Range(Position(5, 1), Position(5, 31))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0
    
    def test_accepts_consistent_camel_case(self):
        """Test that consistent camelCase is accepted."""
        rule = InconsistentNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.WARNING)
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="program",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 20))
                ),
                Rule(
                    name="statementList",
                    is_lexer_rule=False,
                    range=Range(Position(4, 1), Position(4, 28))
                ),
                Rule(
                    name="expressionList",
                    is_lexer_rule=False,
                    range=Range(Position(5, 1), Position(5, 29))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0
    
    def test_handles_single_word_rules(self):
        """Test that single-word rules don't affect style detection."""
        rule = InconsistentNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.WARNING)
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="program",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 20))
                ),
                Rule(
                    name="statement",
                    is_lexer_rule=False,
                    range=Range(Position(4, 1), Position(4, 24))
                ),
                Rule(
                    name="statement_list",  # snake_case
                    is_lexer_rule=False,
                    range=Range(Position(5, 1), Position(5, 30))
                ),
                Rule(
                    name="expression_list",  # snake_case
                    is_lexer_rule=False,
                    range=Range(Position(6, 1), Position(6, 31))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0
    
    def test_ignores_lexer_rules(self):
        """Test that lexer rules are not considered for consistency."""
        rule = InconsistentNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.WARNING)
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="program",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 20))
                ),
                Rule(
                    name="statement_list",
                    is_lexer_rule=False,
                    range=Range(Position(4, 1), Position(4, 30))
                ),
                Rule(
                    name="IDENTIFIER",  # Lexer rule - ignored
                    is_lexer_rule=True,
                    range=Range(Position(5, 1), Position(5, 25))
                ),
                Rule(
                    name="STRING_LITERAL",  # Lexer rule - ignored
                    is_lexer_rule=True,
                    range=Range(Position(6, 1), Position(6, 30))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0