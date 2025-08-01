"""Tests for the grammar parser."""

import pytest
from antlr_v4_linter.core.parser import SimpleGrammarParser
from antlr_v4_linter.core.models import GrammarType


class TestSimpleGrammarParser:
    """Test cases for SimpleGrammarParser."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.parser = SimpleGrammarParser()
    
    def test_parse_combined_grammar(self):
        """Test parsing a combined grammar."""
        content = """
        grammar TestGrammar;
        
        program: statement* EOF;
        statement: ID ASSIGN expression;
        
        ID: [a-zA-Z_][a-zA-Z0-9_]*;
        ASSIGN: '=';
        """
        
        ast = self.parser.parse_content(content, "test.g4")
        
        assert ast.file_path == "test.g4"
        assert ast.declaration.name == "TestGrammar"
        assert ast.declaration.grammar_type == GrammarType.COMBINED
        assert len(ast.rules) >= 4  # program, statement, ID, ASSIGN
    
    def test_parse_lexer_grammar(self):
        """Test parsing a lexer grammar."""
        content = """
        lexer grammar TestLexer;
        
        ID: [a-zA-Z_][a-zA-Z0-9_]*;
        NUMBER: [0-9]+;
        """
        
        ast = self.parser.parse_content(content, "TestLexer.g4")
        
        assert ast.declaration.name == "TestLexer"
        assert ast.declaration.grammar_type == GrammarType.LEXER
    
    def test_parse_parser_grammar(self):
        """Test parsing a parser grammar."""
        content = """
        parser grammar TestParser;
        
        program: statement* EOF;
        statement: ID ASSIGN expression;
        """
        
        ast = self.parser.parse_content(content, "TestParser.g4")
        
        assert ast.declaration.name == "TestParser"
        assert ast.declaration.grammar_type == GrammarType.PARSER
    
    def test_identify_lexer_rules(self):
        """Test identification of lexer vs parser rules."""
        content = """
        grammar TestGrammar;
        
        program: statement;
        
        ID: [a-zA-Z]+;
        """
        
        ast = self.parser.parse_content(content, "test.g4")
        
        program_rule = next(rule for rule in ast.rules if rule.name == "program")
        id_rule = next(rule for rule in ast.rules if rule.name == "ID")
        
        assert not program_rule.is_lexer_rule
        assert id_rule.is_lexer_rule
    
    def test_parse_rule_alternatives(self):
        """Test parsing of rule alternatives."""
        content = """
        grammar TestGrammar;
        
        expression
            : expression '+' expression #addition
            | expression '*' expression #multiplication
            | ID #identifier
            ;
        
        ID: [a-zA-Z]+;
        """
        
        ast = self.parser.parse_content(content, "test.g4")
        
        expr_rule = next(rule for rule in ast.rules if rule.name == "expression")
        assert len(expr_rule.alternatives) == 3
        
        # Check labels
        labels = [alt.label for alt in expr_rule.alternatives if alt.label]
        assert "addition" in labels
        assert "multiplication" in labels
        assert "identifier" in labels
    
    def test_parse_options(self):
        """Test parsing of grammar options."""
        content = """
        grammar TestGrammar;
        
        options {
            superClass = MyBaseParser;
            tokenVocab = MyLexer;
        }
        
        program: ID;
        ID: [a-zA-Z]+;
        """
        
        ast = self.parser.parse_content(content, "test.g4")
        
        assert "superClass" in ast.options
        assert ast.options["superClass"] == "MyBaseParser"
        assert "tokenVocab" in ast.options
        assert ast.options["tokenVocab"] == "MyLexer"