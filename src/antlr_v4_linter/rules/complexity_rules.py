"""Complexity and maintainability linting rules (C001-C003)."""

from typing import List

from ..core.models import FixSuggestion, GrammarAST, Issue, RuleConfig
from ..core.rule_engine import LintRule


class ExcessiveComplexityRule(LintRule):
    """C001: Rule exceeds complexity thresholds."""
    
    def __init__(self):
        super().__init__(
            rule_id="C001",
            name="Excessive Rule Complexity",
            description="Rules should not exceed complexity thresholds for maintainability"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        # Get thresholds from config
        max_alternatives = config.thresholds.get("maxAlternatives", 10)
        max_nesting_depth = config.thresholds.get("maxNestingDepth", 5)
        max_tokens = config.thresholds.get("maxTokens", 50)
        
        for rule in grammar.rules:
            complexity_issues = []
            
            # Check number of alternatives
            if len(rule.alternatives) > max_alternatives:
                complexity_issues.append(
                    f"too many alternatives ({len(rule.alternatives)} > {max_alternatives})"
                )
            
            # Check nesting depth
            max_depth = self._calculate_max_nesting_depth(rule)
            if max_depth > max_nesting_depth:
                complexity_issues.append(
                    f"excessive nesting depth ({max_depth} > {max_nesting_depth})"
                )
            
            # Check total tokens
            total_tokens = self._count_total_tokens(rule)
            if total_tokens > max_tokens:
                complexity_issues.append(
                    f"too many tokens ({total_tokens} > {max_tokens})"
                )
            
            if complexity_issues:
                issues.append(Issue(
                    rule_id=self.rule_id,
                    severity=config.severity,
                    message=f"Rule '{rule.name}' is too complex: {', '.join(complexity_issues)}",
                    file_path=grammar.file_path,
                    range=rule.range,
                    suggestions=[
                        FixSuggestion(
                            description="Break down into smaller rules",
                            fix=f"Consider extracting alternatives or sub-expressions into separate rules"
                        )
                    ]
                ))
        
        return issues
    
    def _calculate_max_nesting_depth(self, rule) -> int:
        """Calculate maximum nesting depth in a rule."""
        max_depth = 0
        
        for alt in rule.alternatives:
            depth = self._calculate_alt_depth(alt)
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    def _calculate_alt_depth(self, alternative) -> int:
        """Calculate nesting depth of an alternative."""
        if not alternative.elements:
            return 0
        
        # Simple heuristic: count parentheses nesting
        max_depth = 0
        current_depth = 0
        
        for element in alternative.elements:
            text = element.text
            for char in text:
                if char == '(':
                    current_depth += 1
                    max_depth = max(max_depth, current_depth)
                elif char == ')':
                    current_depth = max(0, current_depth - 1)
        
        return max_depth
    
    def _count_total_tokens(self, rule) -> int:
        """Count total number of tokens/elements in a rule."""
        total = 0
        
        for alt in rule.alternatives:
            total += len(alt.elements)
        
        return total


class DeeplyNestedRuleRule(LintRule):
    """C002: Deeply nested rule structure."""
    
    def __init__(self):
        super().__init__(
            rule_id="C002",
            name="Deeply Nested Rule",
            description="Rules should avoid deep nesting for readability"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        # Default threshold for deep nesting
        max_nesting = 4
        
        for rule in grammar.rules:
            max_depth = self._calculate_max_nesting_depth(rule)
            
            if max_depth > max_nesting:
                issues.append(Issue(
                    rule_id=self.rule_id,
                    severity=config.severity,
                    message=f"Rule '{rule.name}' has deep nesting (depth: {max_depth})",
                    file_path=grammar.file_path,
                    range=rule.range,
                    suggestions=[
                        FixSuggestion(
                            description="Flatten nested structures",
                            fix="Extract nested expressions into separate rules"
                        )
                    ]
                ))
        
        return issues
    
    def _calculate_max_nesting_depth(self, rule) -> int:
        """Calculate maximum nesting depth in a rule."""
        max_depth = 0
        
        for alt in rule.alternatives:
            # Count nested parentheses, brackets, and subrule references
            depth = 0
            current_depth = 0
            
            for element in alt.elements:
                text = element.text
                for char in text:
                    if char in '([{':
                        current_depth += 1
                        max_depth = max(max_depth, current_depth)
                    elif char in ')]}':
                        current_depth = max(0, current_depth - 1)
        
        return max_depth


class VeryLongRuleRule(LintRule):
    """C003: Very long rule definition."""
    
    def __init__(self):
        super().__init__(
            rule_id="C003",
            name="Very Long Rule",
            description="Rules should be kept concise for maintainability"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        # Default threshold for rule length (in lines)
        max_lines = 30
        
        for rule in grammar.rules:
            # Calculate rule length (simple approximation)
            if rule.range:
                rule_lines = rule.range.end.line - rule.range.start.line + 1
                
                if rule_lines > max_lines:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        severity=config.severity,
                        message=f"Rule '{rule.name}' is very long ({rule_lines} lines)",
                        file_path=grammar.file_path,
                        range=rule.range,
                        suggestions=[
                            FixSuggestion(
                                description="Break into smaller rules",
                                fix="Consider splitting this rule into multiple smaller rules"
                            )
                        ]
                    ))
        
        return issues