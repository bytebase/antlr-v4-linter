"""Syntax and structure linting rules (S001-S003)."""

import re
from typing import List, Set

from ..core.models import FixSuggestion, GrammarAST, Issue, Position, Range, RuleConfig
from ..core.rule_engine import LintRule


class MissingEOFRule(LintRule):
    """S001: Main parser rule doesn't consume EOF token."""
    
    def __init__(self):
        super().__init__(
            rule_id="S001",
            name="Missing EOF Token",
            description="Main parser rule should end with EOF token to ensure complete input parsing"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        # Skip lexer grammars
        if grammar.declaration.grammar_type.value == "lexer":
            return issues
        
        # Find potential main parser rules (first parser rule or rules starting with common names)
        main_rule_candidates = []
        parser_rules = [rule for rule in grammar.rules if not rule.is_lexer_rule]
        
        if parser_rules:
            # First parser rule is often the main rule
            main_rule_candidates.append(parser_rules[0])
            
            # Also check for common main rule names
            common_main_names = ['program', 'compilationUnit', 'start', 'main', 'root', 'file']
            for rule in parser_rules:
                if rule.name.lower() in common_main_names:
                    main_rule_candidates.append(rule)
        
        # Remove duplicates
        main_rule_candidates = list(set(main_rule_candidates))
        
        for rule in main_rule_candidates:
            has_eof = False
            
            # Check if any alternative ends with EOF
            for alternative in rule.alternatives:
                if alternative.elements:
                    last_element = alternative.elements[-1]
                    if last_element.text.upper() == "EOF":
                        has_eof = True
                        break
            
            if not has_eof:
                issues.append(Issue(
                    rule_id=self.rule_id,
                    severity=config.severity,
                    message=f"Main parser rule '{rule.name}' should end with EOF token",
                    file_path=grammar.file_path,
                    range=rule.range,
                    suggestions=[
                        FixSuggestion(
                            description="Add EOF token to rule",
                            fix=f"{rule.name}: {self._get_rule_content_with_eof(rule)};"
                        )
                    ]
                ))
        
        return issues
    
    def _get_rule_content_with_eof(self, rule) -> str:
        """Generate rule content with EOF added."""
        if not rule.alternatives:
            return "/* rule content */ EOF"
        
        # Simple approach: add EOF to the first alternative
        return "/* existing content */ EOF"


class IncompleteInputParsingRule(LintRule):
    """S002: Grammar doesn't handle all possible input (missing ANY rule)."""
    
    def __init__(self):
        super().__init__(
            rule_id="S002",
            name="Incomplete Input Parsing",
            description="Lexer should have an ANY rule to catch unhandled input"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        # Only check lexer and combined grammars
        if grammar.declaration.grammar_type.value == "parser":
            return issues
        
        # Check if there's an ANY rule or similar catch-all
        lexer_rules = [rule for rule in grammar.rules if rule.is_lexer_rule]
        has_any_rule = False
        
        for rule in lexer_rules:
            # Check for common catch-all patterns
            for alternative in rule.alternatives:
                for element in alternative.elements:
                    if (element.text in [".", "ANY"] or 
                        rule.name.upper() in ["ANY", "ERROR", "UNKNOWN"]):
                        has_any_rule = True
                        break
                if has_any_rule:
                    break
            if has_any_rule:
                break
        
        if not has_any_rule and lexer_rules:
            # Find a good position to suggest adding the rule (end of lexer rules)
            last_lexer_rule = lexer_rules[-1]
            
            issues.append(Issue(
                rule_id=self.rule_id,
                severity=config.severity,
                message="Lexer missing catch-all rule for unhandled input",
                file_path=grammar.file_path,
                range=last_lexer_rule.range,
                suggestions=[
                    FixSuggestion(
                        description="Add ANY rule at end of lexer",
                        fix="ANY: .;"
                    )
                ]
            ))
        
        return issues


class AmbiguousStringLiteralsRule(LintRule):
    """S003: Same string literal used in multiple lexer rules."""
    
    def __init__(self):
        super().__init__(
            rule_id="S003",
            name="Ambiguous String Literals",
            description="String literals should not appear in multiple lexer rules"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        # Collect all string literals from lexer rules
        literal_to_rules = {}  # literal -> list of rules that use it
        
        lexer_rules = [rule for rule in grammar.rules if rule.is_lexer_rule]
        
        for rule in lexer_rules:
            for alternative in rule.alternatives:
                for element in alternative.elements:
                    if element.element_type == "terminal" and (
                        element.text.startswith("'") or element.text.startswith('"')
                    ):
                        literal = element.text
                        if literal not in literal_to_rules:
                            literal_to_rules[literal] = []
                        literal_to_rules[literal].append((rule, element))
        
        # Find ambiguous literals
        for literal, rule_elements in literal_to_rules.items():
            if len(rule_elements) > 1:
                # Get unique rules (same rule might use same literal multiple times)
                unique_rules = list(set(rule for rule, _ in rule_elements))
                
                if len(unique_rules) > 1:
                    for rule, element in rule_elements:
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            severity=config.severity,
                            message=f"String literal {literal} is ambiguous (used in multiple lexer rules: {', '.join(r.name for r in unique_rules)})",
                            file_path=grammar.file_path,
                            range=element.range,
                            suggestions=[
                                FixSuggestion(
                                    description="Use unique string literals or consolidate rules",
                                    fix=f"Consider using a shared token rule for {literal}"
                                )
                            ]
                        ))
        
        return issues