"""Error handling linting rules (E001-E002)."""

from typing import List, Set

from ..core.models import FixSuggestion, GrammarAST, Issue, RuleConfig
from ..core.rule_engine import LintRule


class MissingErrorRecoveryRule(LintRule):
    """E001: Missing error recovery strategy."""
    
    def __init__(self):
        super().__init__(
            rule_id="E001",
            name="Missing Error Recovery",
            description="Grammar should include error recovery strategies"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        # Skip lexer-only grammars
        if grammar.declaration.grammar_type.value == "lexer":
            return issues
        
        parser_rules = [rule for rule in grammar.rules if not rule.is_lexer_rule]
        
        # Check for error recovery patterns
        has_error_recovery = False
        rules_without_recovery = []
        
        for rule in parser_rules:
            rule_has_recovery = False
            
            for alt in rule.alternatives:
                for element in alt.elements:
                    # Check for error recovery patterns
                    if any(pattern in element.text for pattern in ['catch', 'finally', 'recover', 'error']):
                        has_error_recovery = True
                        rule_has_recovery = True
            
            # Check for important rules that should have recovery
            if not rule_has_recovery and self._is_important_rule(rule):
                rules_without_recovery.append(rule)
        
        # Report issues for important rules without recovery
        for rule in rules_without_recovery:
            issues.append(Issue(
                rule_id=self.rule_id,
                severity=config.severity,
                message=f"Rule '{rule.name}' should include error recovery for robustness",
                file_path=grammar.file_path,
                range=rule.range,
                suggestions=[
                    FixSuggestion(
                        description="Add error recovery",
                        fix="Consider adding catch blocks or error alternatives"
                    )
                ]
            ))
        
        # Report if no error recovery at all
        if not has_error_recovery and parser_rules:
            issues.append(Issue(
                rule_id=self.rule_id,
                severity=config.severity,
                message="Grammar lacks error recovery strategies",
                file_path=grammar.file_path,
                range=grammar.declaration.range,
                suggestions=[
                    FixSuggestion(
                        description="Add error recovery to key rules",
                        fix="Add catch blocks to handle parsing errors gracefully"
                    )
                ]
            ))
        
        return issues
    
    def _is_important_rule(self, rule) -> bool:
        """Check if a rule is important enough to need error recovery."""
        # Heuristic: top-level rules and statement-like rules
        important_patterns = [
            'statement', 'expression', 'declaration', 'block',
            'program', 'compilation', 'file', 'root', 'main'
        ]
        
        rule_name_lower = rule.name.lower()
        return any(pattern in rule_name_lower for pattern in important_patterns)


class PotentialAmbiguityRule(LintRule):
    """E002: Potential ambiguity in grammar."""
    
    def __init__(self):
        super().__init__(
            rule_id="E002",
            name="Potential Ambiguity",
            description="Grammar rules may have ambiguous alternatives"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        for rule in grammar.rules:
            if not rule.is_lexer_rule and len(rule.alternatives) > 1:
                # Check for ambiguous alternatives
                ambiguities = self._find_ambiguous_alternatives(rule)
                
                if ambiguities:
                    for alt_pair, reason in ambiguities:
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            severity=config.severity,
                            message=f"Rule '{rule.name}' has potentially ambiguous alternatives: {reason}",
                            file_path=grammar.file_path,
                            range=rule.range,
                            suggestions=[
                                FixSuggestion(
                                    description="Resolve ambiguity",
                                    fix="Use predicates, reorder alternatives, or refactor the rule"
                                )
                            ]
                        ))
        
        # Check for left recursion (common source of ambiguity)
        left_recursive_rules = self._find_left_recursive_rules(grammar)
        for rule in left_recursive_rules:
            issues.append(Issue(
                rule_id=self.rule_id,
                severity=config.severity,
                message=f"Rule '{rule.name}' has direct left recursion which may cause ambiguity",
                file_path=grammar.file_path,
                range=rule.range,
                suggestions=[
                    FixSuggestion(
                        description="Eliminate left recursion",
                        fix="Refactor to remove left recursion or ensure ANTLR4 handles it correctly"
                    )
                ]
            ))
        
        return issues
    
    def _find_ambiguous_alternatives(self, rule) -> List:
        """Find potentially ambiguous alternatives in a rule."""
        ambiguities = []
        
        for i, alt1 in enumerate(rule.alternatives):
            for j, alt2 in enumerate(rule.alternatives[i+1:], i+1):
                # Check if alternatives have same first element
                if alt1.elements and alt2.elements:
                    first1 = alt1.elements[0].text
                    first2 = alt2.elements[0].text
                    
                    if first1 == first2:
                        ambiguities.append(
                            ((i, j), f"alternatives {i+1} and {j+1} start with same token '{first1}'")
                        )
                    
                    # Check for optional elements that might cause ambiguity
                    if '?' in first1 or '?' in first2:
                        ambiguities.append(
                            ((i, j), f"alternatives {i+1} and {j+1} have optional elements that may cause ambiguity")
                        )
        
        return ambiguities
    
    def _find_left_recursive_rules(self, grammar: GrammarAST) -> List:
        """Find rules with direct left recursion."""
        left_recursive = []
        
        for rule in grammar.rules:
            if not rule.is_lexer_rule:
                for alt in rule.alternatives:
                    if alt.elements:
                        first_element = alt.elements[0].text
                        # Check if first element is the rule itself (direct left recursion)
                        if first_element == rule.name:
                            left_recursive.append(rule)
                            break
        
        return left_recursive