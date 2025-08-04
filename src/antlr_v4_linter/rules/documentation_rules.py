"""Documentation linting rules (D001-D002)."""

from typing import List

from ..core.models import FixSuggestion, GrammarAST, Issue, RuleConfig
from ..core.rule_engine import LintRule


class MissingRuleDocumentationRule(LintRule):
    """D001: Missing documentation for complex rules."""
    
    def __init__(self):
        super().__init__(
            rule_id="D001",
            name="Missing Rule Documentation",
            description="Complex rules should have documentation comments"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        for rule in grammar.rules:
            # Check if rule is complex enough to need documentation
            if self._is_complex_rule(rule):
                # Check if rule has documentation (simplified check)
                if not self._has_documentation(rule):
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        severity=config.severity,
                        message=f"Complex rule '{rule.name}' lacks documentation",
                        file_path=grammar.file_path,
                        range=rule.range,
                        suggestions=[
                            FixSuggestion(
                                description="Add documentation comment",
                                fix=f"Add /* Description of {rule.name} */ before the rule"
                            )
                        ]
                    ))
        
        return issues
    
    def _is_complex_rule(self, rule) -> bool:
        """Determine if a rule is complex enough to need documentation."""
        # Criteria for complexity:
        # - Multiple alternatives (3+)
        # - Many elements in alternatives
        # - Contains actions or predicates
        
        if len(rule.alternatives) >= 3:
            return True
        
        total_elements = sum(len(alt.elements) for alt in rule.alternatives)
        if total_elements > 10:
            return True
        
        # Check for actions or predicates (simplified)
        for alt in rule.alternatives:
            for element in alt.elements:
                if '{' in element.text or '?' in element.text:
                    return True
        
        return False
    
    def _has_documentation(self, rule) -> bool:
        """Check if rule has documentation (simplified)."""
        # In a real implementation, we'd check for comments before the rule
        # For now, we'll assume rules don't have documentation
        return False


class MissingGrammarHeaderRule(LintRule):
    """D002: Missing grammar header documentation."""
    
    def __init__(self):
        super().__init__(
            rule_id="D002",
            name="Missing Grammar Header",
            description="Grammar file should have a header comment with description"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        # Check if grammar has header documentation (simplified)
        if not self._has_header_documentation(grammar):
            issues.append(Issue(
                rule_id=self.rule_id,
                severity=config.severity,
                message="Grammar file lacks header documentation",
                file_path=grammar.file_path,
                range=grammar.declaration.range,
                suggestions=[
                    FixSuggestion(
                        description="Add header comment",
                        fix="""Add at the beginning of file:
/*
 * Grammar: {name}
 * Description: [Brief description]
 * Author: [Your name]
 * Date: [Date]
 */""".format(name=grammar.declaration.name)
                    )
                ]
            ))
        
        return issues
    
    def _has_header_documentation(self, grammar: GrammarAST) -> bool:
        """Check if grammar has header documentation (simplified)."""
        # In a real implementation, we'd check for comments at the beginning
        # For now, we'll assume grammars don't have header documentation
        return False