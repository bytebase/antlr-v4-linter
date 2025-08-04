from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union


class Severity(enum.Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class GrammarType(enum.Enum):
    COMBINED = "combined"
    LEXER = "lexer"
    PARSER = "parser"


@dataclass
class Position:
    line: int
    column: int


@dataclass
class Range:
    start: Position
    end: Position


@dataclass
class Issue:
    rule_id: str
    severity: Severity
    message: str
    file_path: str
    range: Range
    suggestions: List[FixSuggestion] = field(default_factory=list)


@dataclass
class FixSuggestion:
    description: str
    fix: str


@dataclass
class GrammarDeclaration:
    grammar_type: GrammarType
    name: str
    range: Range


@dataclass
class Rule:
    name: str
    is_lexer_rule: bool
    range: Range
    alternatives: List[Alternative] = field(default_factory=list)
    is_fragment: bool = False
    modifiers: List[str] = field(default_factory=list)
    mode: Optional[str] = None  # Lexer mode this rule belongs to
    
    def __hash__(self) -> int:
        return hash((self.name, self.is_lexer_rule, self.is_fragment))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Rule):
            return False
        return (self.name == other.name and 
                self.is_lexer_rule == other.is_lexer_rule and
                self.is_fragment == other.is_fragment)


@dataclass
class Alternative:
    elements: List[Element] = field(default_factory=list)
    label: Optional[str] = None
    range: Optional[Range] = None


@dataclass
class Element:
    text: str
    range: Range
    label: Optional[str] = None
    element_type: str = "unknown"  # terminal, nonterminal, action, etc.


@dataclass
class GrammarAST:
    file_path: str
    declaration: GrammarDeclaration
    rules: List[Rule] = field(default_factory=list)
    options: Dict[str, Any] = field(default_factory=dict)
    imports: List[str] = field(default_factory=list)
    tokens: List[str] = field(default_factory=list)
    channels: List[str] = field(default_factory=list)


@dataclass
class LintResult:
    file_path: str
    issues: List[Issue] = field(default_factory=list)
    
    @property
    def error_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == Severity.ERROR)
    
    @property
    def warning_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == Severity.WARNING)
    
    @property
    def info_count(self) -> int:
        return sum(1 for issue in self.issues if issue.severity == Severity.INFO)
    
    @property
    def total_issues(self) -> int:
        return len(self.issues)


@dataclass
class RuleConfig:
    enabled: bool = True
    severity: Severity = Severity.WARNING
    thresholds: Dict[str, Union[int, float, str]] = field(default_factory=dict)


@dataclass
class LinterConfig:
    rules: Dict[str, RuleConfig] = field(default_factory=dict)
    exclude_patterns: List[str] = field(default_factory=list)
    output_format: str = "text"
    
    @classmethod
    def default(cls) -> LinterConfig:
        """Create default configuration with all rules enabled."""
        default_rules = {
            # Syntax and Structure
            "S001": RuleConfig(enabled=True, severity=Severity.INFO),
            "S002": RuleConfig(enabled=True, severity=Severity.WARNING),
            "S003": RuleConfig(enabled=True, severity=Severity.ERROR),
            
            # Naming and Convention
            "N001": RuleConfig(enabled=True, severity=Severity.ERROR),
            "N002": RuleConfig(enabled=True, severity=Severity.ERROR),
            "N003": RuleConfig(enabled=True, severity=Severity.WARNING),
            
            # Labeling and Organization
            "L001": RuleConfig(enabled=True, severity=Severity.WARNING),
            "L002": RuleConfig(enabled=True, severity=Severity.INFO),
            "L003": RuleConfig(enabled=True, severity=Severity.WARNING),
            
            # Complexity and Maintainability
            "C001": RuleConfig(
                enabled=True, 
                severity=Severity.WARNING,
                thresholds={
                    "maxAlternatives": 10,
                    "maxNestingDepth": 5,
                    "maxTokens": 50
                }
            ),
            "C002": RuleConfig(enabled=True, severity=Severity.WARNING),
            "C003": RuleConfig(enabled=True, severity=Severity.INFO),
            
            # Token and Lexer
            "T001": RuleConfig(enabled=True, severity=Severity.WARNING),
            "T002": RuleConfig(enabled=True, severity=Severity.WARNING),
            "T003": RuleConfig(enabled=True, severity=Severity.INFO),
            
            # Error Handling
            "E001": RuleConfig(enabled=True, severity=Severity.INFO),
            "E002": RuleConfig(enabled=True, severity=Severity.WARNING),
        }
        
        return cls(rules=default_rules)