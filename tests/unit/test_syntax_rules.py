"""Comprehensive tests for syntax rules."""

import pytest
from antlr_v4_linter.core.models import (
    GrammarAST, GrammarDeclaration, GrammarType, Position, Range,
    Rule, RuleConfig, Severity, Alternative, Element
)
from antlr_v4_linter.rules.syntax_rules import (
    MissingEOFRule, IncompleteInputParsingRule, AmbiguousStringLiteralsRule
)


class TestMissingEOFRule:
    """Test S001: Missing EOF token rule."""
    
    def test_detects_missing_eof_in_main_rule(self):
        """Test detection of missing EOF in main parser rule."""
        rule = MissingEOFRule()
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
                    range=Range(Position(3, 1), Position(3, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="statement",
                                    range=Range(Position(3, 10), Position(3, 19)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="*",
                                    range=Range(Position(3, 20), Position(3, 21)),
                                    element_type="quantifier"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 1
        assert issues[0].rule_id == "S001"
        assert "EOF" in issues[0].message
        assert issues[0].severity == Severity.ERROR
        assert issues[0].range.start.line == 3
    
    def test_passes_with_eof_present(self):
        """Test that rule passes when EOF is present."""
        rule = MissingEOFRule()
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
                    range=Range(Position(3, 1), Position(3, 35)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="statement",
                                    range=Range(Position(3, 10), Position(3, 19)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="*",
                                    range=Range(Position(3, 20), Position(3, 21)),
                                    element_type="quantifier"
                                ),
                                Element(
                                    text="EOF",
                                    range=Range(Position(3, 22), Position(3, 25)),
                                    element_type="reference"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0
    
    def test_disabled_rule_returns_no_issues(self):
        """Test that disabled rule returns no issues."""
        rule = MissingEOFRule()
        config = RuleConfig(enabled=False, severity=Severity.ERROR)
        
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
        assert len(issues) == 0
    
    def test_ignores_non_main_rules(self):
        """Test that rule ignores non-main parser rules."""
        rule = MissingEOFRule()
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
                    name="program",  # Main rule that references statement
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="statement",
                                    range=Range(Position(3, 10), Position(3, 19)),
                                    element_type="rule_ref"
                                ),
                                Element(
                                    text="*",
                                    range=Range(Position(3, 20), Position(3, 21)),
                                    element_type="suffix"
                                ),
                                Element(
                                    text="EOF",
                                    range=Range(Position(3, 22), Position(3, 25)),
                                    element_type="token_ref"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="statement",  # Not a main rule - referenced by program
                    is_lexer_rule=False,
                    range=Range(Position(5, 1), Position(5, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="ID",
                                    range=Range(Position(5, 12), Position(5, 14)),
                                    element_type="token_ref"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        # Should only flag rules that don't already have EOF
        assert len(issues) == 0


class TestIncompleteInputParsingRule:
    """Test S002: Incomplete input parsing rule."""
    
    def test_detects_missing_any_rule_in_lexer(self):
        """Test detection of missing ANY catch-all rule in lexer."""
        rule = IncompleteInputParsingRule()
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
                    name="IDENTIFIER",
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="[a-zA-Z]+",
                                    range=Range(Position(3, 13), Position(3, 23)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="NUMBER",
                    is_lexer_rule=True,
                    range=Range(Position(4, 1), Position(4, 20)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="[0-9]+",
                                    range=Range(Position(4, 10), Position(4, 16)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                )
                # Missing ANY rule to catch unrecognized characters
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 1
        assert issues[0].rule_id == "S002"
        assert "catch-all" in issues[0].message.lower() or "any" in issues[0].message.lower()
        assert issues[0].severity == Severity.WARNING
    
    def test_passes_with_any_rule_present(self):
        """Test that rule passes when ANY catch-all rule is present."""
        rule = IncompleteInputParsingRule()
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
                    name="IDENTIFIER",
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="[a-zA-Z]+",
                                    range=Range(Position(3, 13), Position(3, 23)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="ANY",  # Catch-all rule present
                    is_lexer_rule=True,
                    range=Range(Position(4, 1), Position(4, 15)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text=".",
                                    range=Range(Position(4, 6), Position(4, 7)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0
    
    def test_skips_parser_only_grammars(self):
        """Test that rule skips parser-only grammars."""
        rule = IncompleteInputParsingRule()
        config = RuleConfig(enabled=True, severity=Severity.WARNING)
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.PARSER,  # Parser-only grammar
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="program",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 35)),
                    alternatives=[]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0


class TestAmbiguousStringLiteralsRule:
    """Test S003: Ambiguous string literals rule."""
    
    def test_detects_duplicate_string_literals(self):
        """Test detection of duplicate string literals in lexer rules."""
        rule = AmbiguousStringLiteralsRule()
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
        assert len(issues) == 2
        assert all(issue.rule_id == "S003" for issue in issues)
        assert all("ambiguous" in issue.message.lower() for issue in issues)
        # Check that both rules are flagged
        assert len(issues) == 2
    
    def test_no_issues_with_unique_literals(self):
        """Test that unique string literals don't trigger issues."""
        rule = AmbiguousStringLiteralsRule()
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
                    name="MINUS",
                    is_lexer_rule=True,
                    range=Range(Position(4, 1), Position(4, 16)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="'-'",
                                    range=Range(Position(4, 8), Position(4, 11)),
                                    element_type="terminal"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0
    
    def test_detects_duplicates_across_alternatives(self):
        """Test detection of duplicates within different alternatives."""
        rule = AmbiguousStringLiteralsRule()
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
                    name="KEYWORD",
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="'if'",
                                    range=Range(Position(3, 10), Position(3, 14)),
                                    element_type="terminal"
                                )
                            ]
                        ),
                        Alternative(
                            elements=[
                                Element(
                                    text="'else'",
                                    range=Range(Position(3, 17), Position(3, 23)),
                                    element_type="terminal"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="IF",
                    is_lexer_rule=True,
                    range=Range(Position(4, 1), Position(4, 12)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="'if'",
                                    range=Range(Position(4, 5), Position(4, 9)),
                                    element_type="terminal"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 2
        assert all(issue.rule_id == "S003" for issue in issues)
        assert all("'if'" in issue.message for issue in issues)