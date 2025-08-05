"""Comprehensive tests for token rules."""

import pytest
from antlr_v4_linter.core.models import (
    GrammarAST, GrammarDeclaration, GrammarType, Position, Range,
    Rule, RuleConfig, Severity, Alternative, Element
)
from antlr_v4_linter.rules.token_rules import (
    OverlappingTokensRule, UnreachableTokenRule, UnusedTokenRule
)


class TestOverlappingTokensRule:
    """Test T001: Overlapping tokens rule."""
    
    def test_detects_overlapping_keyword_and_identifier(self):
        """Test detection of keywords that can overlap with identifiers."""
        rule = OverlappingTokensRule()
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
                    name="IF",
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 12)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="'if'",
                                    range=Range(Position(3, 5), Position(3, 9)),
                                    element_type="terminal"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="IDENTIFIER",
                    is_lexer_rule=True,
                    range=Range(Position(4, 1), Position(4, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="[a-zA-Z]+",
                                    range=Range(Position(4, 13), Position(4, 23)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) >= 1
        assert any(issue.rule_id == "T001" for issue in issues)
        assert any("overlap" in issue.message.lower() for issue in issues)
    
    def test_detects_overlapping_number_patterns(self):
        """Test detection of overlapping number token patterns."""
        rule = OverlappingTokensRule()
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
                    name="INTEGER",
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 20)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="[0-9]+",
                                    range=Range(Position(3, 10), Position(3, 17)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="DECIMAL",
                    is_lexer_rule=True,
                    range=Range(Position(4, 1), Position(4, 25)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="[0-9]+",
                                    range=Range(Position(4, 10), Position(4, 17)),
                                    element_type="regex"
                                ),
                                Element(
                                    text="'.'",
                                    range=Range(Position(4, 18), Position(4, 21)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="[0-9]+",
                                    range=Range(Position(4, 22), Position(4, 29)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="NUMBER",  # Can match both INTEGER and DECIMAL patterns
                    is_lexer_rule=True,
                    range=Range(Position(5, 1), Position(5, 20)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="[0-9]+",
                                    range=Range(Position(5, 9), Position(5, 16)),
                                    element_type="regex"
                                ),
                                Element(
                                    text="('.' [0-9]+)?",
                                    range=Range(Position(5, 17), Position(5, 31)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) >= 1
        assert any(issue.rule_id == "T001" for issue in issues)
    
    def test_no_issues_with_distinct_tokens(self):
        """Test that distinct non-overlapping tokens don't trigger issues."""
        rule = OverlappingTokensRule()
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
                    name="PLUS",
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 13)),
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
                    range=Range(Position(4, 1), Position(4, 14)),
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
                ),
                Rule(
                    name="NUMBER",
                    is_lexer_rule=True,
                    range=Range(Position(5, 1), Position(5, 18)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="[0-9]+",
                                    range=Range(Position(5, 9), Position(5, 16)),
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


class TestUnreachableTokenRule:
    """Test T002: Unreachable token rule."""
    
    def test_detects_unreachable_token_after_generic(self):
        """Test detection of specific tokens defined after generic patterns."""
        rule = UnreachableTokenRule()
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
                    name="IDENTIFIER",  # Generic pattern first
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
                    name="IF",  # Specific keyword after - unreachable!
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
                ),
                Rule(
                    name="ELSE",  # Another unreachable keyword
                    is_lexer_rule=True,
                    range=Range(Position(5, 1), Position(5, 14)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="'else'",
                                    range=Range(Position(5, 7), Position(5, 13)),
                                    element_type="terminal"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) >= 2
        assert all(issue.rule_id == "T002" for issue in issues)
        # Check that unreachable tokens are detected
        assert len(issues) >= 2
    
    def test_correct_order_no_issues(self):
        """Test that correct token ordering produces no issues."""
        rule = UnreachableTokenRule()
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
                    name="IF",  # Specific keywords first
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 12)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="'if'",
                                    range=Range(Position(3, 5), Position(3, 9)),
                                    element_type="terminal"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="ELSE",
                    is_lexer_rule=True,
                    range=Range(Position(4, 1), Position(4, 14)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="'else'",
                                    range=Range(Position(4, 7), Position(4, 13)),
                                    element_type="terminal"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="IDENTIFIER",  # Generic pattern last
                    is_lexer_rule=True,
                    range=Range(Position(5, 1), Position(5, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="[a-zA-Z]+",
                                    range=Range(Position(5, 13), Position(5, 23)),
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
    
    def test_detects_duplicate_patterns(self):
        """Test detection of duplicate token patterns."""
        rule = UnreachableTokenRule()
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
                    name="WHITESPACE",
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 25)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="[ \\t\\r\\n]+",
                                    range=Range(Position(3, 13), Position(3, 24)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="WS",  # Same pattern - unreachable!
                    is_lexer_rule=True,
                    range=Range(Position(4, 1), Position(4, 20)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="[ \\t\\r\\n]+",
                                    range=Range(Position(4, 5), Position(4, 16)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) >= 1
        assert any(issue.rule_id == "T002" for issue in issues)
        # Check that duplicate pattern is detected
        assert len(issues) >= 1


class TestUnusedTokenRule:
    """Test T003: Unused token rule."""
    
    def test_detects_unused_tokens(self):
        """Test detection of defined but unused tokens."""
        rule = UnusedTokenRule()
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
                    range=Range(Position(3, 1), Position(3, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="IDENTIFIER",  # Uses IDENTIFIER
                                    range=Range(Position(3, 10), Position(3, 20)),
                                    element_type="reference"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="IDENTIFIER",  # Used in program rule
                    is_lexer_rule=True,
                    range=Range(Position(5, 1), Position(5, 30)),
                    alternatives=[]
                ),
                Rule(
                    name="NUMBER",  # Not used anywhere!
                    is_lexer_rule=True,
                    range=Range(Position(6, 1), Position(6, 20)),
                    alternatives=[]
                ),
                Rule(
                    name="STRING",  # Not used anywhere!
                    is_lexer_rule=True,
                    range=Range(Position(7, 1), Position(7, 20)),
                    alternatives=[]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 2
        assert all(issue.rule_id == "T003" for issue in issues)
        # Check that unused tokens are detected
        assert len(issues) == 2
    
    def test_accepts_used_tokens(self):
        """Test that used tokens don't trigger warnings."""
        rule = UnusedTokenRule()
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
                    name="expression",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 50)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="NUMBER",
                                    range=Range(Position(3, 13), Position(3, 19)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="PLUS",
                                    range=Range(Position(3, 20), Position(3, 24)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="NUMBER",
                                    range=Range(Position(3, 25), Position(3, 31)),
                                    element_type="reference"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="NUMBER",
                    is_lexer_rule=True,
                    range=Range(Position(5, 1), Position(5, 20)),
                    alternatives=[]
                ),
                Rule(
                    name="PLUS",
                    is_lexer_rule=True,
                    range=Range(Position(6, 1), Position(6, 15)),
                    alternatives=[]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0
    
    def test_ignores_skip_tokens(self):
        """Test that skip tokens are not flagged as unused."""
        rule = UnusedTokenRule()
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
                    range=Range(Position(3, 1), Position(3, 20)),
                    alternatives=[]
                ),
                Rule(
                    name="WS",  # Whitespace with skip - shouldn't be flagged
                    is_lexer_rule=True,
                    range=Range(Position(5, 1), Position(5, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="[ \\t\\r\\n]+",
                                    range=Range(Position(5, 5), Position(5, 16)),
                                    element_type="regex"
                                ),
                                Element(
                                    text="-> skip",
                                    range=Range(Position(5, 17), Position(5, 24)),
                                    element_type="action"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="COMMENT",  # Comment with skip
                    is_lexer_rule=True,
                    range=Range(Position(6, 1), Position(6, 35)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="'//' ~[\\r\\n]*",
                                    range=Range(Position(6, 10), Position(6, 24)),
                                    element_type="regex"
                                ),
                                Element(
                                    text="-> skip",
                                    range=Range(Position(6, 25), Position(6, 32)),
                                    element_type="action"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0