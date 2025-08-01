from abc import ABC, abstractmethod
from typing import List

from .models import GrammarAST, Issue, LinterConfig, RuleConfig, Severity


class LintRule(ABC):
    """Base class for all linting rules."""
    
    def __init__(self, rule_id: str, name: str, description: str):
        self.rule_id = rule_id
        self.name = name
        self.description = description
    
    @abstractmethod
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        """Check the grammar and return any issues found."""
        pass
    
    def is_enabled(self, config: LinterConfig) -> bool:
        """Check if this rule is enabled in the configuration."""
        rule_config = config.rules.get(self.rule_id)
        return rule_config is not None and rule_config.enabled
    
    def get_severity(self, config: LinterConfig) -> Severity:
        """Get the severity level for this rule."""
        rule_config = config.rules.get(self.rule_id)
        if rule_config:
            return rule_config.severity
        return Severity.WARNING


class RuleEngine:
    """Engine that runs all linting rules against a grammar."""
    
    def __init__(self):
        self.rules: List[LintRule] = []
    
    def register_rule(self, rule: LintRule) -> None:
        """Register a linting rule with the engine."""
        self.rules.append(rule)
    
    def register_rules(self, rules: List[LintRule]) -> None:
        """Register multiple linting rules with the engine."""
        self.rules.extend(rules)
    
    def run_rules(self, grammar: GrammarAST, config: LinterConfig) -> List[Issue]:
        """Run all enabled rules against the grammar and return issues."""
        all_issues = []
        
        for rule in self.rules:
            if rule.is_enabled(config):
                rule_config = config.rules.get(rule.rule_id, RuleConfig())
                issues = rule.check(grammar, rule_config)
                
                # Update severity based on configuration
                for issue in issues:
                    issue.severity = rule.get_severity(config)
                
                all_issues.extend(issues)
        
        return all_issues
    
    def get_rule(self, rule_id: str) -> LintRule:
        """Get a specific rule by ID."""
        for rule in self.rules:
            if rule.rule_id == rule_id:
                return rule
        raise ValueError(f"Rule {rule_id} not found")
    
    def list_rules(self) -> List[str]:
        """List all registered rule IDs."""
        return [rule.rule_id for rule in self.rules]