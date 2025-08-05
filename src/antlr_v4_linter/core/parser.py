"""ANTLR4 grammar-based parser for accurate AST generation."""

import logging
from pathlib import Path
from typing import List, Optional, Set

from antlr4 import CommonTokenStream, FileStream, InputStream
from antlr4.error.ErrorListener import ErrorListener

from ..grammars.ANTLRv4Lexer import ANTLRv4Lexer
from ..grammars.ANTLRv4Parser import ANTLRv4Parser
from ..grammars.ANTLRv4ParserVisitor import ANTLRv4ParserVisitor
from .models import (
    Alternative,
    Element,
    GrammarAST,
    GrammarDeclaration,
    GrammarType,
    Position,
    Range,
    Rule,
)

logger = logging.getLogger(__name__)


class GrammarErrorListener(ErrorListener):
    """Collect parsing errors."""
    
    def __init__(self):
        self.errors = []
    
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        self.errors.append({
            'line': line,
            'column': column,
            'message': msg
        })


class GrammarASTBuilder(ANTLRv4ParserVisitor):
    """Build our AST from the ANTLR parse tree."""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.rules = []
        self.grammar_type = GrammarType.COMBINED
        self.grammar_name = "Unknown"
        self.options = {}
        self.imports = []
        self.tokens = []
        self.channels = []
    
    def visitGrammarSpec(self, ctx):
        """Visit the root grammar specification."""
        # Visit grammar declaration
        if ctx.grammarDecl():
            self.visitGrammarDecl(ctx.grammarDecl())
        
        # Visit all rules
        if ctx.rules():
            for rule_spec in ctx.rules().ruleSpec():
                self.visitRuleSpec(rule_spec)
        
        return GrammarAST(
            file_path=self.file_path,
            declaration=GrammarDeclaration(
                grammar_type=self.grammar_type,
                name=self.grammar_name,
                range=Range(Position(1, 1), Position(1, 1))
            ),
            rules=self.rules,
            options=self.options,
            imports=self.imports,
            tokens=self.tokens,
            channels=self.channels
        )
    
    def visitGrammarDecl(self, ctx):
        """Visit grammar declaration to get type and name."""
        if ctx.identifier():
            self.grammar_name = ctx.identifier().getText()
        
        if ctx.grammarType():
            grammar_type_text = ctx.grammarType().getText().lower()
            if 'lexer' in grammar_type_text:
                self.grammar_type = GrammarType.LEXER
            elif 'parser' in grammar_type_text:
                self.grammar_type = GrammarType.PARSER
            else:
                self.grammar_type = GrammarType.COMBINED
        else:
            self.grammar_type = GrammarType.COMBINED
    
    def visitRuleSpec(self, ctx):
        """Visit a rule specification."""
        if ctx.parserRuleSpec():
            self.visitParserRuleSpec(ctx.parserRuleSpec())
        elif ctx.lexerRuleSpec():
            self.visitLexerRuleSpec(ctx.lexerRuleSpec())
    
    def visitParserRuleSpec(self, ctx):
        """Visit a parser rule."""
        rule_name = ctx.RULE_REF().getText() if ctx.RULE_REF() else "unknown"
        is_fragment = False  # Parser rules can't be fragments
        
        # Get alternatives
        alternatives = []
        if ctx.ruleBlock() and ctx.ruleBlock().ruleAltList():
            for alt in ctx.ruleBlock().ruleAltList().labeledAlt():
                elements = self._extract_elements_from_alt(alt)
                label = None
                if hasattr(alt, 'identifier') and alt.identifier():
                    label = alt.identifier().getText()
                alternatives.append(Alternative(elements=elements, label=label))
        
        rule = Rule(
            name=rule_name,
            is_lexer_rule=False,
            is_fragment=is_fragment,
            range=self._get_range(ctx),
            alternatives=alternatives,
            mode=None
        )
        self.rules.append(rule)
    
    def visitLexerRuleSpec(self, ctx):
        """Visit a lexer rule."""
        rule_name = ctx.TOKEN_REF().getText() if ctx.TOKEN_REF() else "unknown"
        is_fragment = ctx.FRAGMENT() is not None
        
        # Get alternatives
        alternatives = []
        if ctx.lexerRuleBlock() and ctx.lexerRuleBlock().lexerAltList():
            for alt in ctx.lexerRuleBlock().lexerAltList().lexerAlt():
                elements = self._extract_elements_from_lexer_alt(alt)
                alternatives.append(Alternative(elements=elements, label=None))
        
        rule = Rule(
            name=rule_name,
            is_lexer_rule=True,
            is_fragment=is_fragment,
            range=self._get_range(ctx),
            alternatives=alternatives,
            mode=None
        )
        self.rules.append(rule)
    
    def _extract_elements_from_alt(self, ctx):
        """Extract elements from a parser alternative."""
        elements = []
        
        # Get the alternative content
        if hasattr(ctx, 'alternative') and ctx.alternative():
            alt = ctx.alternative()
            if hasattr(alt, 'element'):
                for elem in alt.element():
                    element_text = elem.getText()
                    element_type = self._determine_element_type(element_text)
                    elements.append(Element(
                        text=element_text,
                        range=self._get_range(elem),
                        element_type=element_type
                    ))
        
        return elements
    
    def _extract_elements_from_lexer_alt(self, ctx):
        """Extract elements from a lexer alternative."""
        elements = []
        
        # Get lexer elements
        if hasattr(ctx, 'lexerElements') and ctx.lexerElements():
            for elem in ctx.lexerElements().lexerElement():
                element_text = elem.getText()
                element_type = self._determine_element_type(element_text)
                elements.append(Element(
                    text=element_text,
                    range=self._get_range(elem),
                    element_type=element_type
                ))
        
        return elements
    
    def _determine_element_type(self, text):
        """Determine the type of an element based on its text."""
        if not text:
            return "unknown"
        
        # String literals
        if text.startswith("'") or text.startswith('"'):
            return "terminal"
        
        # Character sets
        if text.startswith('[') and text.endswith(']'):
            return "char_set"
        
        # Token references (uppercase)
        if text[0].isupper() and text.isalnum():
            return "token_ref"
        
        # Rule references (lowercase)
        if text[0].islower() and text.isalnum():
            return "rule_ref"
        
        # Suffixes
        if text in ['?', '*', '+']:
            return "suffix"
        
        return "unknown"
    
    def _get_range(self, ctx):
        """Get range from context."""
        start_line = ctx.start.line if hasattr(ctx, 'start') and ctx.start else 1
        start_col = ctx.start.column + 1 if hasattr(ctx, 'start') and ctx.start else 1
        end_line = ctx.stop.line if hasattr(ctx, 'stop') and ctx.stop else start_line
        end_col = ctx.stop.column + 1 if hasattr(ctx, 'stop') and ctx.stop else start_col
        
        return Range(
            start=Position(line=start_line, column=start_col),
            end=Position(line=end_line, column=end_col)
        )


class AntlrGrammarParser:
    """Parser using the official ANTLR4 grammar."""
    
    def parse_file(self, file_path: str) -> GrammarAST:
        """Parse a .g4 grammar file and return the AST."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Grammar file not found: {file_path}")
        
        # Create input stream
        input_stream = FileStream(file_path, encoding='utf-8')
        
        # Create lexer and parser
        lexer = ANTLRv4Lexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = ANTLRv4Parser(token_stream)
        
        # Add error listener
        error_listener = GrammarErrorListener()
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)
        
        # Parse the grammar
        tree = parser.grammarSpec()
        
        # Check for errors
        if error_listener.errors:
            logger.warning(f"Parse errors in {file_path}: {error_listener.errors}")
        
        # Build AST
        builder = GrammarASTBuilder(file_path)
        ast = builder.visit(tree)
        
        return ast
    
    def parse_content(self, content: str, file_path: str) -> GrammarAST:
        """Parse grammar content and return the AST."""
        # Create input stream from content
        input_stream = InputStream(content)
        
        # Create lexer and parser
        lexer = ANTLRv4Lexer(input_stream)
        token_stream = CommonTokenStream(lexer)
        parser = ANTLRv4Parser(token_stream)
        
        # Add error listener
        error_listener = GrammarErrorListener()
        parser.removeErrorListeners()
        parser.addErrorListener(error_listener)
        
        # Parse the grammar
        tree = parser.grammarSpec()
        
        # Check for errors
        if error_listener.errors:
            logger.warning(f"Parse errors: {error_listener.errors}")
        
        # Build AST
        builder = GrammarASTBuilder(file_path)
        ast = builder.visit(tree)
        
        return ast