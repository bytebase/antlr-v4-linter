"""Naming and convention linting rules (N001-N003)."""

import re
from typing import List, Set

from ..core.models import FixSuggestion, GrammarAST, Issue, Position, Range, Rule, RuleConfig
from ..core.rule_engine import LintRule


class ParserRuleNamingRule(LintRule):
    """N001: Parser rules should start with lowercase letter."""
    
    def __init__(self):
        super().__init__(
            rule_id="N001",
            name="Parser Rule Naming",
            description="Parser rule names must start with a lowercase letter"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        parser_rules = [rule for rule in grammar.rules if not rule.is_lexer_rule]
        
        for rule in parser_rules:
            if rule.name and not rule.name[0].islower():
                correct_name = rule.name[0].lower() + rule.name[1:]
                
                issues.append(Issue(
                    rule_id=self.rule_id,
                    severity=config.severity,
                    message=f"Parser rule '{rule.name}' should start with lowercase letter",
                    file_path=grammar.file_path,
                    range=rule.range,
                    suggestions=[
                        FixSuggestion(
                            description=f"Rename to '{correct_name}'",
                            fix=f"{correct_name}: /* rule content */;"
                        )
                    ]
                ))
        
        return issues


class LexerRuleNamingRule(LintRule):
    """N002: Lexer rules should start with uppercase letter."""
    
    def __init__(self):
        super().__init__(
            rule_id="N002",
            name="Lexer Rule Naming", 
            description="Lexer rule names must start with an uppercase letter"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        lexer_rules = [rule for rule in grammar.rules if rule.is_lexer_rule]
        
        for rule in lexer_rules:
            if rule.name and not rule.name[0].isupper():
                correct_name = rule.name[0].upper() + rule.name[1:]
                
                issues.append(Issue(
                    rule_id=self.rule_id,
                    severity=config.severity,
                    message=f"Lexer rule '{rule.name}' should start with uppercase letter",
                    file_path=grammar.file_path,
                    range=rule.range,
                    suggestions=[
                        FixSuggestion(
                            description=f"Rename to '{correct_name}'",
                            fix=f"{correct_name}: /* rule content */;"
                        )
                    ]
                ))
        
        return issues


class InconsistentNamingRule(LintRule):
    """N003: Mixed naming styles (camelCase vs snake_case)."""
    
    def __init__(self):
        super().__init__(
            rule_id="N003",
            name="Inconsistent Naming Convention",
            description="Rule names should follow a consistent naming convention"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        # Analyze naming patterns separately for parser and lexer rules
        parser_rules = [rule for rule in grammar.rules if not rule.is_lexer_rule and rule.name]
        lexer_rules = [rule for rule in grammar.rules if rule.is_lexer_rule and rule.name]
        
        # Check parser rules for consistency
        if len(parser_rules) > 1:
            issues.extend(self._check_parser_rule_consistency(parser_rules, grammar.file_path, config))
        
        # Check lexer rules for consistency (though they should all be uppercase)
        if len(lexer_rules) > 1:
            issues.extend(self._check_lexer_rule_consistency(lexer_rules, grammar.file_path, config))
        
        return issues
    
    def _check_parser_rule_consistency(self, parser_rules: List[Rule], file_path: str, config: RuleConfig) -> List[Issue]:
        """Check consistency among parser rules."""
        issues = []
        
        camel_case_rules = []
        snake_case_rules = []
        other_rules = []
        
        for rule in parser_rules:
            if self._is_camel_case(rule.name):
                camel_case_rules.append(rule)
            elif self._is_snake_case(rule.name):
                snake_case_rules.append(rule)
            else:
                other_rules.append(rule)
        
        # If we have a mix of styles, report inconsistency
        styles_found = []
        if camel_case_rules:
            styles_found.append("camelCase")
        if snake_case_rules:
            styles_found.append("snake_case")
        
        if len(styles_found) > 1:
            # Determine the dominant style
            dominant_style = "camelCase" if len(camel_case_rules) >= len(snake_case_rules) else "snake_case"
            
            # Report issues for rules not following dominant style
            inconsistent_rules = snake_case_rules if dominant_style == "camelCase" else camel_case_rules
            
            for rule in inconsistent_rules:
                suggested_name = self._convert_to_style(rule.name, dominant_style)
                
                issues.append(Issue(
                    rule_id=self.rule_id,
                    severity=config.severity,
                    message=f"Parser rule '{rule.name}' doesn't follow the dominant {dominant_style} naming convention",
                    file_path=file_path,
                    range=rule.range,
                    suggestions=[
                        FixSuggestion(
                            description=f"Rename to follow {dominant_style} convention",
                            fix=f"Consider renaming to '{suggested_name}'"
                        )
                    ]
                ))
        
        return issues
    
    def _check_lexer_rule_consistency(self, lexer_rules: List[Rule], file_path: str, config: RuleConfig) -> List[Issue]:
        """Check consistency among lexer rules (should mostly be UPPER_CASE)."""
        issues = []
        
        # For lexer rules, we primarily care about consistent use of underscores vs no underscores
        with_underscores = []
        without_underscores = []
        
        for rule in lexer_rules:
            if '_' in rule.name:
                with_underscores.append(rule)
            else:
                without_underscores.append(rule)
        
        # Only report if there's a significant mix and one style dominates
        if len(with_underscores) > 0 and len(without_underscores) > 0:
            # Only report if the minority is significant (>25% of rules)
            total = len(lexer_rules)
            minority_size = min(len(with_underscores), len(without_underscores))
            
            if minority_size > total * 0.25:
                dominant_style = "UPPER_CASE" if len(without_underscores) > len(with_underscores) else "UPPER_SNAKE_CASE"
                minority_rules = with_underscores if len(without_underscores) > len(with_underscores) else without_underscores
                
                for rule in minority_rules:
                    suggested_name = rule.name.replace('_', '') if '_' in rule.name else rule.name
                    
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        severity=config.severity,
                        message=f"Lexer rule '{rule.name}' doesn't follow the dominant {dominant_style} naming convention",
                        file_path=file_path,
                        range=rule.range,
                        suggestions=[
                            FixSuggestion(
                                description=f"Rename to follow {dominant_style} convention",
                                fix=f"Consider renaming to '{suggested_name}'"
                            )
                        ]
                    ))
        
        return issues
    
    def _is_camel_case(self, name: str) -> bool:
        """Check if name follows camelCase convention."""
        # Should start with lowercase, contain uppercase letters, no underscores
        if not name or not name[0].islower():
            return False
        
        return bool(re.match(r'^[a-z][a-zA-Z0-9]*$', name) and re.search(r'[A-Z]', name))
    
    def _is_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case convention."""
        # Should be all lowercase with underscores
        return bool(re.match(r'^[a-z][a-z0-9_]*$', name) and '_' in name)
    
    def _convert_to_style(self, name: str, target_style: str) -> str:
        """Convert name to target naming style."""
        if target_style == "camelCase":
            return self._to_camel_case(name)
        elif target_style == "snake_case":
            return self._to_snake_case(name)
        return name
    
    def _to_camel_case(self, name: str) -> str:
        """Convert name to camelCase."""
        # Handle snake_case to camelCase
        if '_' in name:
            parts = name.split('_')
            return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])
        
        # Ensure first letter is lowercase for parser rules
        return name[0].lower() + name[1:] if name else name
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case."""
        # Handle camelCase to snake_case
        result = re.sub('([A-Z])', r'_\1', name).lower()
        return result.lstrip('_')