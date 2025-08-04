"""ANTLR v4 linting rules."""

from .syntax_rules import *
from .naming_rules import *
from .labeling_rules import *
from .complexity_rules import *
from .token_rules import *
from .error_handling_rules import *
from .performance_rules import *
from .documentation_rules import *

__all__ = [
    # Syntax rules (S001-S003)
    "MissingEOFRule",
    "IncompleteInputParsingRule", 
    "AmbiguousStringLiteralsRule",
    
    # Naming rules (N001-N003)
    "ParserRuleNamingRule",
    "LexerRuleNamingRule",
    "InconsistentNamingRule",
    
    # Labeling rules (L001-L003)
    "MissingAlternativeLabelsRule",
    "InconsistentLabelNamingRule",
    "DuplicateLabelsRule",
    
    # Complexity rules (C001-C003)
    "ExcessiveComplexityRule",
    "DeeplyNestedRuleRule",
    "VeryLongRuleRule",
    
    # Token rules (T001-T003)
    "OverlappingTokensRule",
    "UnreachableTokenRule",
    "UnusedTokenRule",
    
    # Error handling rules (E001-E002)
    "MissingErrorRecoveryRule",
    "PotentialAmbiguityRule",
    
    # Performance rules (P001-P002)
    "BacktrackingRule",
    "InefficientLexerRule",
    
    # Documentation rules (D001-D002)
    "MissingRuleDocumentationRule",
    "MissingGrammarHeaderRule",
]