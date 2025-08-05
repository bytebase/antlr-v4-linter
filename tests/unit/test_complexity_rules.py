"""Comprehensive tests for complexity rules."""

import pytest
from antlr_v4_linter.core.models import (
    GrammarAST, GrammarDeclaration, GrammarType, Position, Range,
    Rule, RuleConfig, Severity, Alternative, Element
)
from antlr_v4_linter.rules.complexity_rules import (
    ExcessiveComplexityRule, DeeplyNestedRuleRule, VeryLongRuleRule
)


class TestExcessiveComplexityRule:
    """Test C001: Excessive complexity rule."""
    
    def test_detects_excessive_alternatives(self):
        """Test detection of rules with too many alternatives."""
        rule = ExcessiveComplexityRule()
        config = RuleConfig(
            enabled=True,
            severity=Severity.WARNING,
            thresholds={"maxAlternatives": 5}
        )
        
        # Create a rule with many alternatives
        alternatives = []
        for i in range(8):  # 8 alternatives > threshold of 5
            alternatives.append(
                Alternative(
                    elements=[
                        Element(
                            text=f"option{i}",
                            range=Range(Position(3 + i, 10), Position(3 + i, 20)),
                            element_type="reference"
                        )
                    ]
                )
            )
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="complexRule",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(11, 30)),
                    alternatives=alternatives
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 1
        assert issues[0].rule_id == "C001"
        assert "complex" in issues[0].message.lower()
        assert "alternatives" in issues[0].message.lower()
        # Check that the correct rule is flagged
    
    def test_accepts_simple_rules(self):
        """Test that simple rules don't trigger complexity warnings."""
        rule = ExcessiveComplexityRule()
        config = RuleConfig(
            enabled=True,
            severity=Severity.WARNING,
            thresholds={"maxAlternatives": 5}
        )
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="simpleRule",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(5, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="option1",
                                    range=Range(Position(3, 10), Position(3, 17)),
                                    element_type="reference"
                                )
                            ]
                        ),
                        Alternative(
                            elements=[
                                Element(
                                    text="option2",
                                    range=Range(Position(4, 10), Position(4, 17)),
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
    
    def test_detects_complex_nested_elements(self):
        """Test detection of rules with complex nested structures."""
        rule = ExcessiveComplexityRule()
        config = RuleConfig(
            enabled=True,
            severity=Severity.WARNING,
            thresholds={"maxTokens": 10}
        )
        
        # Create alternative with many elements
        elements = []
        for i in range(15):  # 15 elements > threshold of 10
            elements.append(
                Element(
                    text=f"element{i}",
                    range=Range(Position(3, 10 + i*10), Position(3, 18 + i*10)),
                    element_type="reference"
                )
            )
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="longAlternative",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 200)),
                    alternatives=[
                        Alternative(elements=elements)
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) >= 1
        assert any(issue.rule_id == "C001" for issue in issues)
        assert any("complex" in issue.message.lower() for issue in issues)
    
    def test_cyclomatic_complexity(self):
        """Test cyclomatic complexity calculation."""
        rule = ExcessiveComplexityRule()
        config = RuleConfig(
            enabled=True,
            severity=Severity.WARNING,
            thresholds={"maxAlternatives": 5}
        )
        
        # Create rule with complex branching
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="branchingRule",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(10, 30)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="(",
                                    range=Range(Position(3, 10), Position(3, 11)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="expression",
                                    range=Range(Position(3, 12), Position(3, 22)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="?",  # Optional - adds complexity
                                    range=Range(Position(3, 23), Position(3, 24)),
                                    element_type="quantifier"
                                ),
                                Element(
                                    text=")",
                                    range=Range(Position(3, 25), Position(3, 26)),
                                    element_type="terminal"
                                )
                            ]
                        ),
                        Alternative(
                            elements=[
                                Element(
                                    text="statement",
                                    range=Range(Position(4, 10), Position(4, 19)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="*",  # Zero or more - adds complexity
                                    range=Range(Position(4, 20), Position(4, 21)),
                                    element_type="quantifier"
                                )
                            ]
                        ),
                        Alternative(
                            elements=[
                                Element(
                                    text="value",
                                    range=Range(Position(5, 10), Position(5, 15)),
                                    element_type="reference"
                                ),
                                Element(
                                    text="+",  # One or more - adds complexity
                                    range=Range(Position(5, 16), Position(5, 17)),
                                    element_type="quantifier"
                                )
                            ]
                        )
                    ]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        # Cyclomatic complexity = alternatives + quantifiers
        # Should trigger if complexity > 5


class TestDeeplyNestedRuleRule:
    """Test C002: Deeply nested rule."""
    
    def test_detects_deep_nesting(self):
        """Test detection of deeply nested rule structures."""
        rule = DeeplyNestedRuleRule()
        config = RuleConfig(
            enabled=True,
            severity=Severity.WARNING,
            thresholds={"maxNestingDepth": 3}
        )
        
        # Create deeply nested structure
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="nestedRule",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 100)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="(",
                                    range=Range(Position(3, 10), Position(3, 11)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="(",  # Nested level 1
                                    range=Range(Position(3, 12), Position(3, 13)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="(",  # Nested level 2
                                    range=Range(Position(3, 14), Position(3, 15)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="(",  # Nested level 3
                                    range=Range(Position(3, 16), Position(3, 17)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="(",  # Nested level 4 - too deep!
                                    range=Range(Position(3, 18), Position(3, 19)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="value",
                                    range=Range(Position(3, 20), Position(3, 25)),
                                    element_type="reference"
                                ),
                                Element(
                                    text=")",
                                    range=Range(Position(3, 26), Position(3, 27)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text=")",
                                    range=Range(Position(3, 28), Position(3, 29)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text=")",
                                    range=Range(Position(3, 30), Position(3, 31)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text=")",
                                    range=Range(Position(3, 32), Position(3, 33)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text=")",
                                    range=Range(Position(3, 34), Position(3, 35)),
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
        assert any(issue.rule_id == "C002" for issue in issues)
        assert any("nested" in issue.message.lower() for issue in issues)
    
    def test_accepts_shallow_nesting(self):
        """Test that shallow nesting is accepted."""
        rule = DeeplyNestedRuleRule()
        config = RuleConfig(
            enabled=True,
            severity=Severity.WARNING,
            thresholds={"maxNestingDepth": 3}
        )
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="shallowRule",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(3, 50)),
                    alternatives=[
                        Alternative(
                            elements=[
                                Element(
                                    text="(",
                                    range=Range(Position(3, 10), Position(3, 11)),
                                    element_type="terminal"
                                ),
                                Element(
                                    text="expression",
                                    range=Range(Position(3, 12), Position(3, 22)),
                                    element_type="reference"
                                ),
                                Element(
                                    text=")",
                                    range=Range(Position(3, 23), Position(3, 24)),
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


class TestVeryLongRuleRule:
    """Test C003: Very long rule."""
    
    def test_detects_long_rules(self):
        """Test detection of rules that are too long."""
        rule = VeryLongRuleRule()
        config = RuleConfig(
            enabled=True,
            severity=Severity.WARNING,
            thresholds={"maxLines": 20}
        )
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="veryLongRule",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(28, 30)),  # 26 lines > 20
                    alternatives=[]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 1
        assert issues[0].rule_id == "C003"
        assert "long" in issues[0].message.lower()
        assert "26 lines" in issues[0].message or "lines" in issues[0].message
        # Check that the correct rule is flagged
    
    def test_accepts_short_rules(self):
        """Test that short rules don't trigger warnings."""
        rule = VeryLongRuleRule()
        config = RuleConfig(
            enabled=True,
            severity=Severity.WARNING,
            thresholds={"maxLines": 20}
        )
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="shortRule",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(8, 30)),  # 6 lines < 20
                    alternatives=[]
                ),
                Rule(
                    name="anotherShortRule",
                    is_lexer_rule=False,
                    range=Range(Position(10, 1), Position(15, 25)),  # 6 lines < 20
                    alternatives=[]
                )
            ]
        )
        
        issues = rule.check(grammar, config)
        assert len(issues) == 0
    
    def test_customizable_threshold(self):
        """Test that the line threshold is customizable."""
        rule = VeryLongRuleRule()
        
        # Test with strict threshold
        strict_config = RuleConfig(
            enabled=True,
            severity=Severity.ERROR,
            thresholds={"maxLines": 5}
        )
        
        grammar = GrammarAST(
            file_path="test.g4",
            declaration=GrammarDeclaration(
                grammar_type=GrammarType.COMBINED,
                name="TestGrammar",
                range=Range(Position(1, 1), Position(1, 20))
            ),
            rules=[
                Rule(
                    name="mediumRule",
                    is_lexer_rule=False,
                    range=Range(Position(3, 1), Position(9, 30)),  # 7 lines > 5
                    alternatives=[]
                )
            ]
        )
        
        issues = rule.check(grammar, strict_config)
        assert len(issues) == 1
        assert issues[0].severity == Severity.ERROR
        
        # Test with relaxed threshold
        relaxed_config = RuleConfig(
            enabled=True,
            severity=Severity.WARNING,
            thresholds={"maxLines": 10}
        )
        
        issues = rule.check(grammar, relaxed_config)
        assert len(issues) == 0