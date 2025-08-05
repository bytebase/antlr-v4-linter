"""Token and lexer linting rules (T001-T003)."""

from typing import Dict, List, Set

from ..core.models import FixSuggestion, GrammarAST, Issue, RuleConfig
from ..core.rule_engine import LintRule


class OverlappingTokensRule(LintRule):
    """T001: Overlapping token definitions."""
    
    def __init__(self):
        super().__init__(
            rule_id="T001",
            name="Overlapping Tokens",
            description="Token rules should not have overlapping patterns"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        lexer_rules = [rule for rule in grammar.rules if rule.is_lexer_rule and not rule.is_fragment]
        
        # Check for potential overlaps
        for i, rule1 in enumerate(lexer_rules):
            for rule2 in lexer_rules[i+1:]:
                overlap = self._check_overlap(rule1, rule2)
                if overlap:
                    issues.append(Issue(
                        rule_id=self.rule_id,
                        severity=config.severity,
                        message=f"Token '{rule1.name}' may overlap with '{rule2.name}': {overlap}",
                        file_path=grammar.file_path,
                        range=rule1.range,
                        suggestions=[
                            FixSuggestion(
                                description="Review token order or make patterns more specific",
                                fix=f"Consider reordering tokens or using more specific patterns"
                            )
                        ]
                    ))
        
        return issues
    
    def _check_overlap(self, rule1, rule2) -> str:
        """Check if two rules might overlap."""
        # Simple heuristic checks for common overlap patterns
        
        # Check for identical string literals
        literals1 = self._extract_literals(rule1)
        literals2 = self._extract_literals(rule2)
        
        common_literals = literals1.intersection(literals2)
        if common_literals:
            return f"both match {', '.join(common_literals)}"
        
        # Check for subset patterns (e.g., ID and keyword)
        pattern1 = self._get_simple_pattern(rule1)
        pattern2 = self._get_simple_pattern(rule2)
        
        # Check if one is a keyword and another is identifier pattern
        if self._is_identifier_pattern(pattern1) and self._is_keyword_like(rule2):
            return f"'{rule2.name}' keyword may be matched by identifier '{rule1.name}'"
        if self._is_identifier_pattern(pattern2) and self._is_keyword_like(rule1):
            return f"'{rule1.name}' keyword may be matched by identifier '{rule2.name}'"
        
        # Check for numeric pattern overlaps
        if self._is_numeric_pattern(rule1) and self._is_numeric_pattern(rule2):
            # Check if patterns could match the same input
            if self._numeric_patterns_overlap(rule1, rule2):
                return f"numeric patterns may overlap"
        
        return ""
    
    def _is_numeric_pattern(self, rule) -> bool:
        """Check if rule is a numeric pattern."""
        # Check if rule name suggests numeric
        if any(name in rule.name.upper() for name in ['NUMBER', 'NUM', 'INT', 'FLOAT', 'DECIMAL', 'DIGIT']):
            return True
        
        # Check if rule contains numeric patterns
        for alt in rule.alternatives:
            for element in alt.elements:
                text = element.text
                # Check for digit patterns
                if any(pattern in text for pattern in ['0-9', '\\d', 'DIGIT', '[0123456789]']):
                    return True
                # Check for explicit numbers
                if text.strip("'\"").isdigit():
                    return True
        
        return False
    
    def _numeric_patterns_overlap(self, rule1, rule2) -> bool:
        """Check if two numeric patterns could match the same input."""
        # Simple heuristic: if both rules can match digits, they might overlap
        # unless one is more specific (e.g., INT vs FLOAT)
        
        # Check if one is integer and other is float
        is_int1 = 'INT' in rule1.name.upper() or 'INTEGER' in rule1.name.upper()
        is_int2 = 'INT' in rule2.name.upper() or 'INTEGER' in rule2.name.upper()
        is_float1 = 'FLOAT' in rule1.name.upper() or 'DECIMAL' in rule1.name.upper()
        is_float2 = 'FLOAT' in rule2.name.upper() or 'DECIMAL' in rule2.name.upper()
        
        # INT and FLOAT typically overlap (FLOAT can match "123")
        if (is_int1 and is_float2) or (is_int2 and is_float1):
            return True
        
        # Both are generic number patterns
        if not (is_int1 or is_int2 or is_float1 or is_float2):
            # If both just match digits, they likely overlap
            return True
        
        # Check for specific patterns
        pattern1 = self._get_numeric_pattern_type(rule1)
        pattern2 = self._get_numeric_pattern_type(rule2)
        
        # If both can match simple integers, they overlap
        if pattern1 == pattern2 == "integer":
            return True
        
        return False
    
    def _get_numeric_pattern_type(self, rule) -> str:
        """Get the type of numeric pattern (integer, float, etc.)."""
        for alt in rule.alternatives:
            has_dot = any('.' in element.text for element in alt.elements)
            has_digits = any(self._has_digit_pattern(element.text) for element in alt.elements)
            
            if has_dot and has_digits:
                return "float"
            elif has_digits:
                return "integer"
        
        return "unknown"
    
    def _has_digit_pattern(self, text: str) -> bool:
        """Check if text contains digit pattern."""
        return any(pattern in text for pattern in ['0-9', '\\d', 'DIGIT', '[0123456789]']) or text.strip("'\"").isdigit()
    
    def _extract_literals(self, rule) -> Set[str]:
        """Extract string literals from a rule."""
        literals = set()
        for alt in rule.alternatives:
            for element in alt.elements:
                if element.element_type == "terminal" and (
                    element.text.startswith("'") or element.text.startswith('"')
                ):
                    literals.add(element.text)
        return literals
    
    def _get_simple_pattern(self, rule) -> str:
        """Get simplified pattern representation."""
        if not rule.alternatives or not rule.alternatives[0].elements:
            return ""
        return rule.alternatives[0].elements[0].text
    
    def _is_identifier_pattern(self, pattern: str) -> bool:
        """Check if pattern looks like an identifier rule."""
        id_patterns = ['[a-zA-Z]', '[A-Z]', '[a-z]', 'Letter', 'LETTER']
        return any(p in pattern for p in id_patterns)
    
    def _is_keyword_like(self, rule) -> bool:
        """Check if rule looks like a keyword."""
        if not rule.alternatives:
            return False
        
        # Check if all alternatives are string literals
        for alt in rule.alternatives:
            if not all(e.element_type == "terminal" and (
                e.text.startswith("'") or e.text.startswith('"')
            ) for e in alt.elements):
                return False
        
        return True


class UnreachableTokenRule(LintRule):
    """T002: Unreachable token rule."""
    
    def __init__(self):
        super().__init__(
            rule_id="T002",
            name="Unreachable Token",
            description="Token rules should be reachable (not shadowed by earlier rules)"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        lexer_rules = [rule for rule in grammar.rules if rule.is_lexer_rule and not rule.is_fragment]
        
        # Check for rules that might be unreachable
        for i, rule in enumerate(lexer_rules):
            # Check if this rule might be shadowed by earlier rules
            shadowing_rules = []
            
            for earlier_rule in lexer_rules[:i]:
                if self._shadows(earlier_rule, rule):
                    shadowing_rules.append(earlier_rule.name)
            
            if shadowing_rules:
                issues.append(Issue(
                    rule_id=self.rule_id,
                    severity=config.severity,
                    message=f"Token '{rule.name}' may be unreachable (shadowed by: {', '.join(shadowing_rules)})",
                    file_path=grammar.file_path,
                    range=rule.range,
                    suggestions=[
                        FixSuggestion(
                            description="Reorder tokens or make patterns more specific",
                            fix=f"Move '{rule.name}' before shadowing rules or use more specific pattern"
                        )
                    ]
                ))
        
        return issues
    
    def _shadows(self, earlier_rule, later_rule) -> bool:
        """Check if earlier_rule might shadow later_rule."""
        # Simple heuristic: check if earlier rule is more general
        
        # Check if rules have identical patterns
        if self._have_identical_patterns(earlier_rule, later_rule):
            return True
        
        # If earlier rule has a catch-all pattern
        for alt in earlier_rule.alternatives:
            for element in alt.elements:
                if element.text in ['.', '.*', '.+']:
                    return True
        
        # Check if later rule is a specific keyword shadowed by ID pattern
        if self._is_identifier_like(earlier_rule) and self._is_specific_keyword(later_rule):
            return True
        
        return False
    
    def _have_identical_patterns(self, rule1, rule2) -> bool:
        """Check if two rules have identical patterns."""
        # Get all patterns from both rules
        patterns1 = set()
        for alt in rule1.alternatives:
            pattern = ' '.join(elem.text for elem in alt.elements)
            patterns1.add(pattern)
        
        patterns2 = set()
        for alt in rule2.alternatives:
            pattern = ' '.join(elem.text for elem in alt.elements)
            patterns2.add(pattern)
        
        # If they have the same patterns, they're identical
        return patterns1 == patterns2
    
    def _is_identifier_like(self, rule) -> bool:
        """Check if rule matches identifier-like patterns."""
        patterns = ['[a-zA-Z]', '[A-Z]', '[a-z]', 'Letter']
        for alt in rule.alternatives:
            for element in alt.elements:
                if any(p in element.text for p in patterns):
                    return True
        return False
    
    def _is_specific_keyword(self, rule) -> bool:
        """Check if rule is a specific keyword."""
        # Check if all alternatives are string literals with alphabetic content
        for alt in rule.alternatives:
            if not alt.elements:
                return False
            for element in alt.elements:
                if element.element_type == "terminal":
                    text = element.text.strip("'\"")
                    if text.isalpha():
                        return True
        return False


class UnusedTokenRule(LintRule):
    """T003: Token defined but never used."""
    
    def __init__(self):
        super().__init__(
            rule_id="T003",
            name="Unused Token",
            description="Tokens should be used in parser rules"
        )
    
    def check(self, grammar: GrammarAST, config: RuleConfig) -> List[Issue]:
        issues = []
        
        # Skip if this is a lexer-only grammar
        if grammar.declaration.grammar_type.value == "lexer":
            return issues
        
        # Collect all lexer rules (tokens)
        lexer_rules = [rule for rule in grammar.rules if rule.is_lexer_rule and not rule.is_fragment]
        parser_rules = [rule for rule in grammar.rules if not rule.is_lexer_rule]
        
        # Collect all token references from parser rules
        used_tokens = set()
        for rule in parser_rules:
            for alt in rule.alternatives:
                for element in alt.elements:
                    # Check if element references a token (uppercase name)
                    if element.text and element.text[0].isupper() and element.text.isalnum():
                        used_tokens.add(element.text)
        
        # Check for unused tokens
        for token_rule in lexer_rules:
            if token_rule.name not in used_tokens:
                # Skip common special tokens
                if token_rule.name in ['WS', 'COMMENT', 'LINE_COMMENT', 'BLOCK_COMMENT', 
                                       'NEWLINE', 'WHITESPACE', 'SKIP', 'HIDDEN']:
                    continue
                
                issues.append(Issue(
                    rule_id=self.rule_id,
                    severity=config.severity,
                    message=f"Token '{token_rule.name}' is defined but never used in parser rules",
                    file_path=grammar.file_path,
                    range=token_rule.range,
                    suggestions=[
                        FixSuggestion(
                            description="Remove unused token or use it in parser rules",
                            fix=f"Either remove '{token_rule.name}' or reference it in a parser rule"
                        )
                    ]
                ))
        
        return issues