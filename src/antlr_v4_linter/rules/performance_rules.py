"""Performance linting rules (P001-P002)."""

from typing import List, Set

from ..core.models import FixSuggestion, GrammarAST, Issue, RuleConfig
from ..core.rule_engine import LintRule


class BacktrackingRule(LintRule):
    """P001: Grammar may cause excessive backtracking."""
    
    def __init__(self):
        super().__init__(
            rule_id="P001",
            name="Excessive Backtracking",
            description="Grammar patterns that may cause performance issues due to backtracking"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        for rule in grammar.rules:
            # Check for patterns that cause backtracking
            backtrack_patterns = self._find_backtracking_patterns(rule)
            
            if backtrack_patterns:
                for pattern, reason in backtrack_patterns:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        severity=config.severity,
                        message=f"Rule '{rule.name}' may cause excessive backtracking: {reason}",
                        file_path=grammar.file_path,
                        range=rule.range,
                        suggestions=[
                            FixSuggestion(
                                description="Optimize to reduce backtracking",
                                fix=pattern
                            )
                        ]
                    ))
        
        return issues
    
    def _find_backtracking_patterns(self, rule) -> List:
        """Find patterns that may cause excessive backtracking."""
        patterns = []
        
        # Check for common prefix in alternatives (key backtracking cause)
        if len(rule.alternatives) > 1:
            for i, alt1 in enumerate(rule.alternatives):
                for alt2 in rule.alternatives[i+1:]:
                    if self._alternatives_have_common_prefix(alt1, alt2):
                        patterns.append((
                            "Factor out common prefix or reorder alternatives",
                            "alternatives with common prefix require backtracking"
                        ))
                        break
                    # Check for optional prefix conflicts
                    if self._has_optional_prefix_conflict(alt1, alt2):
                        patterns.append((
                            "Optional prefix conflicts with another alternative",
                            "optional prefix may cause backtracking"
                        ))
                        break
        
        for alt in rule.alternatives:
            # Check for (x)* (y)* patterns
            has_consecutive_star = False
            prev_was_star = False
            
            for element in alt.elements:
                text = element.text
                if '*' in text:
                    if prev_was_star:
                        has_consecutive_star = True
                        patterns.append((
                            "Use (x | y)* instead of (x)* (y)*",
                            "consecutive optional repetitions"
                        ))
                        break
                    prev_was_star = True
                else:
                    prev_was_star = False
            
            # Check for overlapping alternatives with repetition
            if '+' in str(alt.elements) or '*' in str(alt.elements):
                for other_alt in rule.alternatives:
                    if alt != other_alt and self._alternatives_overlap(alt, other_alt):
                        patterns.append((
                            "Reorder alternatives or use predicates",
                            "overlapping alternatives with repetition"
                        ))
                        break
        
        # Check for deeply nested optional groups
        for alt in rule.alternatives:
            nested_level = self._count_nested_optionals(alt)
            if nested_level > 2:
                patterns.append((
                    "Flatten nested optional groups",
                    f"deeply nested optional groups (level {nested_level})"
                ))
        
        return patterns
    
    def _alternatives_have_common_prefix(self, alt1, alt2) -> bool:
        """Check if two alternatives share a common prefix."""
        if not alt1.elements or not alt2.elements:
            return False
        
        # Check if first elements match
        return alt1.elements[0].text == alt2.elements[0].text
    
    def _has_optional_prefix_conflict(self, alt1, alt2) -> bool:
        """Check if one alternative has optional prefix that conflicts with another."""
        if not alt1.elements or not alt2.elements:
            return False
        
        # Check if alt1 starts with optional group
        first_elem = alt1.elements[0].text
        if '?' in first_elem and ('(' in first_elem or ')' in first_elem):
            # Extract the optional content
            optional_content = first_elem.strip('()?')
            # Check if alt2 starts with the same content
            if alt2.elements[0].text.strip("'\"") == optional_content.strip("'\""):
                return True
        
        # Check reverse case
        first_elem = alt2.elements[0].text
        if '?' in first_elem and ('(' in first_elem or ')' in first_elem):
            optional_content = first_elem.strip('()?')
            if alt1.elements[0].text.strip("'\"") == optional_content.strip("'\""):
                return True
        
        return False
    
    def _alternatives_overlap(self, alt1, alt2) -> bool:
        """Check if two alternatives might overlap."""
        if not alt1.elements or not alt2.elements:
            return False
        
        # Simple check: same first element
        return alt1.elements[0].text == alt2.elements[0].text
    
    def _count_nested_optionals(self, alternative) -> int:
        """Count nesting level of optional groups."""
        max_level = 0
        current_level = 0
        
        for element in alternative.elements:
            text = element.text
            for char in text:
                if char == '(':
                    current_level += 1
                elif char == ')':
                    if '?' in text:
                        max_level = max(max_level, current_level)
                    current_level = max(0, current_level - 1)
        
        return max_level


class InefficientLexerRule(LintRule):
    """P002: Inefficient lexer patterns."""
    
    def __init__(self):
        super().__init__(
            rule_id="P002",
            name="Inefficient Lexer Pattern",
            description="Lexer patterns that may impact performance"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        lexer_rules = [rule for rule in grammar.rules if rule.is_lexer_rule]
        
        for rule in lexer_rules:
            inefficiencies = self._find_inefficient_patterns(rule)
            
            for pattern, suggestion in inefficiencies:
                issues.append(Issue(
                    rule_id=self.rule_id,
                    severity=config.severity,
                    message=f"Lexer rule '{rule.name}' has inefficient pattern: {pattern}",
                    file_path=grammar.file_path,
                    range=rule.range,
                    suggestions=[
                        FixSuggestion(
                            description="Optimize pattern",
                            fix=suggestion
                        )
                    ]
                ))
        
        return issues
    
    def _find_inefficient_patterns(self, rule) -> List:
        """Find inefficient patterns in lexer rules."""
        inefficiencies = []
        
        for alt in rule.alternatives:
            for element in alt.elements:
                text = element.text
                
                # Check for catastrophic backtracking patterns like (.*)* or (.*)+
                if '(.*)*' in text or '(.*)+' in text:
                    inefficiencies.append((
                        "catastrophic backtracking pattern",
                        "Remove nested quantifiers or use atomic groups"
                    ))
                
                # Check for nested quantifiers like (a+)+ or (\w*)*
                import re
                nested_pattern = r'\([^)]*[+*]\)[+*]'
                if re.search(nested_pattern, text):
                    inefficiencies.append((
                        "nested quantifiers can cause exponential backtracking",
                        "Flatten nested quantifiers or use possessive quantifiers"
                    ))
                
                # Check for .* at the beginning
                if text.startswith('.*'):
                    inefficiencies.append((
                        ".* at beginning of pattern",
                        "Move .* to the end or use more specific pattern"
                    ))
                
                # Check for multiple .* in same rule
                if text.count('.*') > 1:
                    inefficiencies.append((
                        "multiple .* in pattern",
                        "Use single .* or more specific patterns"
                    ))
                
                # Check for complex character classes that could be simplified
                if '[' in text and ']' in text:
                    char_class = text[text.find('['):text.find(']')+1]
                    if len(char_class) > 20:
                        # Check if it could be simplified
                        if self._can_simplify_char_class(char_class):
                            inefficiencies.append((
                                "complex character class",
                                "Simplify character class using ranges or complement"
                            ))
                
                # Check for unnecessary alternation in lexer
                if '|' in text and text.count('|') > 5:
                    # Check if it's single character alternation that could be a character class
                    parts = text.split('|')
                    if all(len(p.strip("()")) == 1 or (p.startswith("'") and p.endswith("'") and len(p) == 3) for p in parts):
                        inefficiencies.append((
                            "inefficient alternation pattern",
                            "Use character class [a-h] instead of (a|b|c|d|e|f|g|h)"
                        ))
        
        return inefficiencies
    
    def _can_simplify_char_class(self, char_class: str) -> bool:
        """Check if character class can be simplified."""
        # Simple heuristic: consecutive characters that could be a range
        chars = char_class[1:-1]  # Remove [ and ]
        
        # Check for consecutive ASCII characters
        if len(chars) > 5:
            consecutive_count = 0
            for i in range(len(chars) - 1):
                if ord(chars[i+1]) == ord(chars[i]) + 1:
                    consecutive_count += 1
            
            # If more than half are consecutive, it can be simplified
            return consecutive_count > len(chars) / 2
        
        return False