"""Labeling and organization linting rules (L001-L003)."""

from typing import Dict, List, Set

from ..core.models import FixSuggestion, GrammarAST, Issue, RuleConfig
from ..core.rule_engine import LintRule


class MissingAlternativeLabelsRule(LintRule):
    """L001: Missing labels for alternatives in parser rules."""
    
    def __init__(self):
        super().__init__(
            rule_id="L001",
            name="Missing Alternative Labels",
            description="Parser rules with multiple alternatives should have labels for clarity"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        parser_rules = [rule for rule in grammar.rules if not rule.is_lexer_rule]
        
        for rule in parser_rules:
            # Check if rule has multiple alternatives
            if len(rule.alternatives) > 1:
                # Check if any alternative is missing a label
                unlabeled_count = sum(1 for alt in rule.alternatives if not alt.label)
                
                if unlabeled_count > 0:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        severity=config.severity,
                        message=f"Rule '{rule.name}' has {unlabeled_count} unlabeled alternative(s) out of {len(rule.alternatives)}",
                        file_path=grammar.file_path,
                        range=rule.range,
                        suggestions=[
                            FixSuggestion(
                                description="Add labels to alternatives",
                                fix=f"Add #label syntax to each alternative in '{rule.name}'"
                            )
                        ]
                    ))
        
        return issues


class InconsistentLabelNamingRule(LintRule):
    """L002: Inconsistent label naming convention."""
    
    def __init__(self):
        super().__init__(
            rule_id="L002",
            name="Inconsistent Label Naming",
            description="Labels should follow a consistent naming convention"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        # Collect all labels
        all_labels = []
        label_locations = {}  # label -> (rule, alternative)
        
        for rule in grammar.rules:
            if not rule.is_lexer_rule:
                for idx, alt in enumerate(rule.alternatives):
                    if alt.label:
                        all_labels.append(alt.label)
                        label_locations[alt.label] = (rule, alt)
        
        if len(all_labels) < 2:
            return issues
        
        # Analyze naming patterns
        camel_case_labels = []
        snake_case_labels = []
        pascal_case_labels = []
        
        for label in all_labels:
            if self._is_camel_case(label):
                camel_case_labels.append(label)
            elif self._is_snake_case(label):
                snake_case_labels.append(label)
            elif self._is_pascal_case(label):
                pascal_case_labels.append(label)
        
        # Determine dominant style
        styles = []
        if camel_case_labels:
            styles.append(("camelCase", len(camel_case_labels), camel_case_labels))
        if snake_case_labels:
            styles.append(("snake_case", len(snake_case_labels), snake_case_labels))
        if pascal_case_labels:
            styles.append(("PascalCase", len(pascal_case_labels), pascal_case_labels))
        
        if len(styles) > 1:
            # Find dominant style
            dominant_style = max(styles, key=lambda x: x[1])
            
            # Report inconsistent labels
            for style_name, count, labels in styles:
                if style_name != dominant_style[0]:
                    for label in labels:
                        rule, alt = label_locations[label]
                        suggested_label = self._convert_to_style(label, dominant_style[0])
                        
                        issues.append(Issue(
                            rule_id=self.rule_id,
                            severity=config.severity,
                            message=f"Label '{label}' doesn't follow dominant {dominant_style[0]} convention",
                            file_path=grammar.file_path,
                            range=alt.range if alt.range else rule.range,
                            suggestions=[
                                FixSuggestion(
                                    description=f"Rename to '{suggested_label}'",
                                    fix=f"Change #{label} to #{suggested_label}"
                                )
                            ]
                        ))
        
        return issues
    
    def _is_camel_case(self, name: str) -> bool:
        """Check if name follows camelCase convention."""
        if not name or not name[0].islower():
            return False
        return not '_' in name and any(c.isupper() for c in name[1:])
    
    def _is_snake_case(self, name: str) -> bool:
        """Check if name follows snake_case convention."""
        return '_' in name and name.islower()
    
    def _is_pascal_case(self, name: str) -> bool:
        """Check if name follows PascalCase convention."""
        if not name or not name[0].isupper():
            return False
        return not '_' in name
    
    def _convert_to_style(self, name: str, target_style: str) -> str:
        """Convert name to target naming style."""
        if target_style == "camelCase":
            if '_' in name:
                parts = name.split('_')
                return parts[0].lower() + ''.join(word.capitalize() for word in parts[1:])
            return name[0].lower() + name[1:] if name else name
        elif target_style == "snake_case":
            import re
            result = re.sub('([A-Z])', r'_\1', name).lower()
            return result.lstrip('_')
        elif target_style == "PascalCase":
            if '_' in name:
                parts = name.split('_')
                return ''.join(word.capitalize() for word in parts)
            return name[0].upper() + name[1:] if name else name
        return name


class DuplicateLabelsRule(LintRule):
    """L003: Duplicate label names within the same rule."""
    
    def __init__(self):
        super().__init__(
            rule_id="L003",
            name="Duplicate Labels",
            description="Labels within the same rule must be unique"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        for rule in grammar.rules:
            if not rule.is_lexer_rule:
                # Track labels within this rule
                seen_labels: Dict[str, List] = {}
                
                for idx, alt in enumerate(rule.alternatives):
                    if alt.label:
                        if alt.label not in seen_labels:
                            seen_labels[alt.label] = []
                        seen_labels[alt.label].append((idx, alt))
                
                # Check for duplicates
                for label, occurrences in seen_labels.items():
                    if len(occurrences) > 1:
                        for idx, alt in occurrences:
                            issues.append(Issue(
                                rule_id=self.rule_id,
                                severity=config.severity,
                                message=f"Duplicate label '{label}' in rule '{rule.name}' (alternative {idx + 1})",
                                file_path=grammar.file_path,
                                range=alt.range if alt.range else rule.range,
                                suggestions=[
                                    FixSuggestion(
                                        description="Use unique label",
                                        fix=f"Change to #{label}_{idx + 1} or another unique name"
                                    )
                                ]
                            ))
        
        return issues