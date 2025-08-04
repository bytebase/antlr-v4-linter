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
        
        parser_rules = [rule for rule in grammar.rules if not rule.is_lexer_rule]
        if not parser_rules:
            return issues
        
        # Check if user has configured specific main rules
        configured_main_rules = config.thresholds.get('mainRules', [])
        if configured_main_rules:
            # Use user-configured main rules
            main_rule_candidates = [
                rule for rule in parser_rules 
                if rule.name in configured_main_rules
            ]
        else:
            # Auto-detect main rules
            # Build a set of all rules that are referenced by other rules
            referenced_rules = set()
            for rule in parser_rules:
                for alternative in rule.alternatives:
                    for element in alternative.elements:
                        # Check if this element is a rule reference
                        if element.element_type == "rule_ref" or (
                            element.text and 
                            element.text[0].islower() and 
                            element.text.isalnum()
                        ):
                            referenced_rules.add(element.text)
            
            # Find potential main parser rules
            main_rule_candidates = []
            
            # Common main rule names
            common_main_names = {'program', 'compilationunit', 'start', 'main', 'root', 'file', 
                               'document', 'script', 'module', 'parse'}
            
            for rule in parser_rules:
                # A rule is likely a main rule if:
                # 1. It's not referenced by other rules AND
                # 2. Either it's the first rule OR has a common main name
                if rule.name not in referenced_rules:
                    if rule == parser_rules[0] or rule.name.lower() in common_main_names:
                        main_rule_candidates.append(rule)
                # OR if it has a very typical main rule name even if referenced
                elif rule.name.lower() in {'program', 'compilationunit', 'start'}:
                    # But only if it's one of the first few rules
                    if parser_rules.index(rule) < 3:
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
                    message=f"Potential main parser rule '{rule.name}' should end with EOF token",
                    file_path=grammar.file_path,
                    range=rule.range,
                    suggestions=[
                        FixSuggestion(
                            description="Add EOF token to rule if this is a main entry point",
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
        
        # Collect all string literals from lexer rules, grouped by mode
        # Structure: {mode: {literal: [(rule, element)]}}
        mode_literals = {}  
        
        lexer_rules = [rule for rule in grammar.rules if rule.is_lexer_rule]
        
        for rule in lexer_rules:
            # Determine the mode for this rule (None for default mode)
            mode = rule.mode if hasattr(rule, 'mode') else None
            
            if mode not in mode_literals:
                mode_literals[mode] = {}
            
            for alternative in rule.alternatives:
                for element in alternative.elements:
                    # Only check actual string literals, not character sets
                    if element.element_type == "terminal" and (
                        element.text.startswith("'") or element.text.startswith('"')
                    ):
                        # Skip empty strings or malformed literals
                        if len(element.text) < 2:
                            continue
                        
                        literal = element.text
                        if literal not in mode_literals[mode]:
                            mode_literals[mode][literal] = []
                        mode_literals[mode][literal].append((rule, element))
        
        # Find ambiguous literals within each mode
        for mode, literal_to_rules in mode_literals.items():
            for literal, rule_elements in literal_to_rules.items():
                if len(rule_elements) > 1:
                    # Get unique rules (same rule might use same literal multiple times)
                    unique_rules = list(set(rule for rule, _ in rule_elements))
                    
                    if len(unique_rules) > 1:
                        mode_str = f" in mode '{mode}'" if mode else ""
                        for rule, element in rule_elements:
                            issues.append(Issue(
                                rule_id=self.rule_id,
                                severity=config.severity,
                                message=f"String literal {literal} is ambiguous{mode_str} (used in multiple lexer rules: {', '.join(r.name for r in unique_rules)})",
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