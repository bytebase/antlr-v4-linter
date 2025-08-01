"""Tests for linting rules."""

import pytest
from antlr_v4_linter.core.models import GrammarAST, GrammarDeclaration, GrammarType, Position, Range, Rule, RuleConfig, Severity
from antlr_v4_linter.rules.syntax_rules import MissingEOFRule, AmbiguousStringLiteralsRule
from antlr_v4_linter.rules.naming_rules import ParserRuleNamingRule, LexerRuleNamingRule


class TestSyntaxRules:
    """Test cases for syntax rules."""
    
    def test_missing_eof_rule(self):
        """Test S001: Missing EOF token rule."""
        rule = MissingEOFRule()
        config = RuleConfig(enabled=True, severity=Severity.ERROR)
        
        # Create a grammar without EOF
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
                    range=Range(Position(3, 1), Position(3, 20)),
                    alternatives=[]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 1
        assert issues[0].rule_id == "S001"
        assert "EOF" in issues[0].message
    
    def test_ambiguous_string_literals_rule(self):
        """Test S003: Ambiguous string literals rule."""
        rule = AmbiguousStringLiteralsRule()
        config = RuleConfig(enabled=True, severity=Severity.ERROR)
        
        # Create grammar with duplicate string literals
        from antlr_v4_linter.core.models import Alternative, Element
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar", 
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="PLUS",
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 15)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="'+'",
                                    range=Range(Position(3, 7), Position(3, 10)),
                                    element_type="terminal"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="ADD",
                    is_lexer_rule=True,
                    range=Range(Position(4, 1), Position(4, 14)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="'+'",
                                    range=Range(Position(4, 6), Position(4, 9)),
                                    element_type="terminal"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 2  # Both rules using the same literal
        assert all(issue.rule_id == "S003" for issue in issues)
        assert all("ambiguous" in issue.message.lower() for issue in issues)


class TestNamingRules:
    """Test cases for naming rules."""
    
    def test_parser_rule_naming(self):
        """Test N001: Parser rule naming rule."""
        rule = ParserRuleNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.ERROR)
        
        # Create grammar with incorrectly named parser rule
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="Program",  # Should start with lowercase
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 20))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 1
        assert issues[0].rule_id == "N001"
        assert "lowercase" in issues[0].message
        assert "program" in issues[0].suggestions[0].fix.lower()
    
    def test_lexer_rule_naming(self):
        """Test N002: Lexer rule naming rule."""
        rule = LexerRuleNamingRule()
        config = RuleConfig(enabled=True, severity=Severity.ERROR)
        
        # Create grammar with incorrectly named lexer rule
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="id",  # Should start with uppercase
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 20))
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 1
        assert issues[0].rule_id == "N002"
        assert "uppercase" in issues[0].message
        assert "ID" in issues[0].suggestions[0].fix