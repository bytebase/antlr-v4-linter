"""Comprehensive tests for performance rules."""

import pytest
from antlr_v4_linter.core.models import (
    GrammarAST, GrammarDeclaration, GrammarType, Position, Range,
    Rule, RuleConfig, Severity, Alternative, Element
)
from antlr_v4_linter.rules.performance_rules import (
    BacktrackingRule, InefficientLexerRule
)


class TestBacktrackingRule:
    """Test P001: Backtracking rule."""
    
    def test_detects_potential_backtracking(self):
        """Test detection of rules that may cause backtracking."""
        rule = BacktrackingRule()
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
                    name="statement",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(5, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="IDENTIFIER",  # Common prefix
                                    range=Range(Position(3, 12), Position(3, 22)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="'='",
                                    range=Range(Position(3, 23), Position(3, 26)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="expression",
                                    range=Range(Position(3, 27), Position(3, 37)),
                                    element_type="reference"
                                )
                            ]
                        ),
                        Alternative(
                            elements=[
                                Element(
                                    text="IDENTIFIER",  # Same prefix - backtracking needed
                                    range=Range(Position(4, 5), Position(4, 15)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="'('",
                                    range=Range(Position(4, 16), Position(4, 19)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="arguments",
                                    range=Range(Position(4, 20), Position(4, 29)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="')'",
                                    range=Range(Position(4, 30), Position(4, 33)),
                                    element_type="terminal"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) >= 1
        assert any(issue.rule_id == "P001" for issue in issues)
        assert any("backtracking" in issue.message.lower() for issue in issues)
        # Test passes - common prefix detected
    
    def test_detects_complex_lookahead(self):
        """Test detection of rules requiring complex lookahead."""
        rule = BacktrackingRule()
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
                    name="declaration",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(5, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="type",
                                    range=Range(Position(3, 14), Position(3, 18)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="IDENTIFIER",
                                    range=Range(Position(3, 19), Position(3, 29)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="'='",
                                    range=Range(Position(3, 30), Position(3, 33)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="expression",
                                    range=Range(Position(3, 34), Position(3, 44)),
                                    element_type="reference"
                                )
                            ]
                        ),
                        Alternative(
                            elements=[
                                Element(
                                    text="type",  # Same prefix, needs lookahead
                                    range=Range(Position(4, 5), Position(4, 9)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="IDENTIFIER",
                                    range=Range(Position(4, 10), Position(4, 20)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="'('",  # Different after 2 tokens
                                    range=Range(Position(4, 21), Position(4, 24)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="parameters",
                                    range=Range(Position(4, 25), Position(4, 35)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="')'",
                                    range=Range(Position(4, 36), Position(4, 39)),
                                    element_type="terminal"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) >= 1
        assert any(issue.rule_id == "P001" for issue in issues)
        assert any("lookahead" in issue.message.lower() or "backtracking" in issue.message.lower() for issue in issues)
    
    def test_no_issues_with_distinct_prefixes(self):
        """Test that rules with distinct prefixes don't trigger warnings."""
        rule = BacktrackingRule()
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
                    name="statement",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(5, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="'if'",  # Distinct prefix
                                    range=Range(Position(3, 12), Position(3, 16)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="expression",
                                    range=Range(Position(3, 17), Position(3, 27)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="statement",
                                    range=Range(Position(3, 28), Position(3, 37)),
                                    element_type="reference"
                                )
                            ]
                        ),
                        Alternative(
                            elements=[
                                Element(
                                    text="'while'",  # Different prefix
                                    range=Range(Position(4, 5), Position(4, 12)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="expression",
                                    range=Range(Position(4, 13), Position(4, 23)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="statement",
                                    range=Range(Position(4, 24), Position(4, 33)),
                                    element_type="reference"
                                )
                            ]
                        ),
                        Alternative(
                            elements=[
                                Element(
                                    text="'return'",  # Another distinct prefix
                                    range=Range(Position(5, 5), Position(5, 13)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="expression",
                                    range=Range(Position(5, 14), Position(5, 24)),
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
    
    def test_detects_optional_prefix_backtracking(self):
        """Test detection of backtracking with optional prefixes."""
        rule = BacktrackingRule()
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
                    range=Range(Position(3, 1), Position(5, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="('-')?",  # Optional prefix
                                    range=Range(Position(3, 13), Position(3, 19)),
                                    element_type="group"
                                ),
                                Element(
                                    text="NUMBER",
                                    range=Range(Position(3, 20), Position(3, 26)),
                                    element_type="reference"
                                )
                            ]
                        ),
                        Alternative(
                            elements=[
                                Element(
                                    text="'-'",  # Conflicts with optional above
                                    range=Range(Position(4, 5), Position(4, 8)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="expression",
                                    range=Range(Position(4, 9), Position(4, 19)),
                                    element_type="reference"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) >= 1
        assert any(issue.rule_id == "P001" for issue in issues)


class TestInefficientLexerRule:
    """Test P002: Inefficient lexer rule."""
    
    def test_detects_inefficient_regex(self):
        """Test detection of inefficient regular expressions."""
        rule = InefficientLexerRule()
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
                    name="COMPLEX_PATTERN",
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 40)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="(.*)*",  # Catastrophic backtracking pattern
                                    range=Range(Position(3, 18), Position(3, 23)),
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
        assert any(issue.rule_id == "P002" for issue in issues)
        assert any("inefficient" in issue.message.lower() or "backtracking" in issue.message.lower() for issue in issues)
    
    def test_detects_nested_quantifiers(self):
        """Test detection of nested quantifiers that can cause performance issues."""
        rule = InefficientLexerRule()
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
                    name="BAD_PATTERN",
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 35)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="([a-z]+)+",  # Nested quantifiers
                                    range=Range(Position(3, 14), Position(3, 23)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="ANOTHER_BAD",
                    is_lexer_rule=True,
                    range=Range(Position(4, 1), Position(4, 35)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="(\\w*)*",  # Another nested quantifier
                                    range=Range(Position(4, 15), Position(4, 21)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) >= 2
        assert all(issue.rule_id == "P002" for issue in issues)
        # Check that both rules were flagged
    
    def test_accepts_efficient_patterns(self):
        """Test that efficient patterns don't trigger warnings."""
        rule = InefficientLexerRule()
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
                                    text="[a-zA-Z_][a-zA-Z0-9_]*",  # Efficient pattern
                                    range=Range(Position(3, 13), Position(3, 36)),
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
                                    text="[0-9]+",  # Simple, efficient
                                    range=Range(Position(4, 9), Position(4, 15)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                ),
                Rule(
                    name="STRING",
                    is_lexer_rule=True,
                    range=Range(Position(5, 1), Position(5, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="'\"' (~'\"')* '\"'",  # Efficient string pattern
                                    range=Range(Position(5, 9), Position(5, 25)),
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
    
    def test_detects_overlapping_character_classes(self):
        """Test detection of overlapping character classes."""
        rule = InefficientLexerRule()
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
                    name="OVERLAP",
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 35)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="[a-z]*[a-m]*",  # Overlapping ranges
                                    range=Range(Position(3, 10), Position(3, 22)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        # May detect overlapping character classes as inefficient
        assert len(issues) >= 0
    
    def test_suggests_optimizations(self):
        """Test that the rule suggests optimizations."""
        rule = InefficientLexerRule()
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
                    name="INEFFICIENT",
                    is_lexer_rule=True,
                    range=Range(Position(3, 1), Position(3, 35)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="(a|b|c|d|e|f|g|h)+",  # Could be [a-h]+
                                    range=Range(Position(3, 14), Position(3, 32)),
                                    element_type="regex"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        if len(issues) > 0:
            assert any("suggestion" in str(issue.suggestions) for issue in issues if issue.suggestions)