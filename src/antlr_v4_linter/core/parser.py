import re
from pathlib import Path
from typing import List, Optional

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


class SimpleGrammarParser:
    """
    A simplified parser for ANTLR v4 grammars that extracts essential information
    for linting without requiring the full ANTLR runtime.
    """
    
    def __init__(self):
        self.lines: List[str] = []
        self.current_line = 0
    
    def _remove_block_comments(self, content: str) -> str:
        """Remove /* */ block comments while preserving line numbers."""
        result = []
        in_block_comment = False
        i = 0
        
        while i < len(content):
            # Check for start of block comment
            if not in_block_comment and i < len(content) - 1 and content[i:i+2] == '/*':
                in_block_comment = True
                # Replace with spaces to preserve positions
                result.append(' ')
                result.append(' ')
                i += 2
                continue
            
            # Check for end of block comment
            if in_block_comment and i < len(content) - 1 and content[i:i+2] == '*/':
                in_block_comment = False
                result.append(' ')
                result.append(' ')
                i += 2
                continue
            
            # If in block comment, replace with space (preserving newlines)
            if in_block_comment:
                if content[i] == '\n':
                    result.append('\n')
                else:
                    result.append(' ')
            else:
                result.append(content[i])
            
            i += 1
        
        return ''.join(result)
    
    def parse_file(self, file_path: str) -> GrammarAST:
        """Parse a .g4 grammar file and return the AST."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Grammar file not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return self.parse_content(content, file_path)
    
    def parse_content(self, content: str, file_path: str) -> GrammarAST:
        """Parse grammar content and return the AST."""
        # Remove block comments while preserving line numbers
        content = self._remove_block_comments(content)
        
        self.lines = content.splitlines()
        self.current_line = 0
        
        # Parse grammar declaration
        declaration = self._parse_grammar_declaration()
        
        # Parse rules
        rules = self._parse_rules()
        
        # Extract basic information
        options = self._extract_options(content)
        imports = self._extract_imports(content)
        tokens = self._extract_tokens(content)
        channels = self._extract_channels(content)
        
        return GrammarAST(
            file_path=file_path,
            declaration=declaration,
            rules=rules,
            options=options,
            imports=imports,
            tokens=tokens,
            channels=channels
        )
    
    def _parse_grammar_declaration(self) -> GrammarDeclaration:
        """Parse the grammar declaration line."""
        for i, line in enumerate(self.lines):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            # Match grammar declaration patterns
            patterns = [
                r'^\s*(lexer\s+)?grammar\s+(\w+)\s*;',
                r'^\s*(parser\s+)?grammar\s+(\w+)\s*;',
                r'^\s*grammar\s+(\w+)\s*;'
            ]
            
            for pattern in patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    if 'lexer' in line.lower():
                        grammar_type = GrammarType.LEXER
                        name = match.group(2)
                    elif 'parser' in line.lower():
                        grammar_type = GrammarType.PARSER
                        name = match.group(2)
                    else:
                        grammar_type = GrammarType.COMBINED
                        name = match.group(1) if len(match.groups()) == 1 else match.group(2)
                    
                    return GrammarDeclaration(
                        grammar_type=grammar_type,
                        name=name,
                        range=Range(
                            start=Position(line=i + 1, column=1),
                            end=Position(line=i + 1, column=len(line))
                        )
                    )
        
        # Default fallback
        return GrammarDeclaration(
            grammar_type=GrammarType.COMBINED,
            name="Unknown",
            range=Range(start=Position(1, 1), end=Position(1, 1))
        )
    
    def _parse_rules(self) -> List[Rule]:
        """Parse all rules in the grammar."""
        rules = []
        current_mode = None
        
        for i, line in enumerate(self.lines):
            line = line.strip()
            if not line or line.startswith('//'):
                continue
            
            # Check for mode declarations
            mode_match = re.match(r'^\s*mode\s+(\w+)\s*;', line)
            if mode_match:
                current_mode = mode_match.group(1)
                continue
            
            # Skip non-rule lines
            if any(keyword in line.lower() for keyword in 
                   ['grammar', 'options', 'tokens', 'channels', 'import']):
                continue
            
            # Look for rule definitions
            rule_match = re.match(r'^\s*(fragment\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*:', line)
            if rule_match:
                is_fragment = bool(rule_match.group(1))
                rule_name = rule_match.group(2)
                is_lexer_rule = rule_name[0].isupper()
                
                # Find the end of the rule (next rule or end of file)
                rule_content = self._extract_rule_content(i)
                alternatives = self._parse_alternatives(rule_content)
                
                rule = Rule(
                    name=rule_name,
                    is_lexer_rule=is_lexer_rule,
                    is_fragment=is_fragment,
                    range=Range(
                        start=Position(line=i + 1, column=1),
                        end=Position(line=i + len(rule_content.split('\n')), column=1)
                    ),
                    alternatives=alternatives,
                    mode=current_mode  # Track which mode this rule belongs to
                )
                rules.append(rule)
        
        return rules
    
    def _extract_rule_content(self, start_line: int) -> str:
        """Extract the complete content of a rule."""
        content_lines = []
        brace_count = 0
        paren_count = 0
        bracket_count = 0
        in_string = False
        string_char = None
        in_rule = False
        
        for i in range(start_line, len(self.lines)):
            line = self.lines[i]
            original_line = line
            line = line.strip()
            
            # Skip empty lines and comments
            if not line or line.startswith('//'):
                if in_rule:
                    content_lines.append(line)
                continue
            
            # Start of rule
            if ':' in line and not in_rule:
                in_rule = True
            
            if in_rule:
                content_lines.append(line)
                
                # Track nesting depth properly
                j = 0
                while j < len(line):
                    char = line[j]
                    
                    # Handle string literals
                    if not in_string and (char == "'" or char == '"'):
                        in_string = True
                        string_char = char
                    elif in_string and char == string_char:
                        # Check if it's escaped
                        if j > 0 and line[j-1] != '\\':
                            in_string = False
                            string_char = None
                    elif not in_string:
                        # Count nesting outside of strings
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                        elif char == '(':
                            paren_count += 1
                        elif char == ')':
                            paren_count -= 1
                        elif char == '[':
                            bracket_count += 1
                        elif char == ']':
                            bracket_count -= 1
                        elif char == ';':
                            # Rule ends with semicolon when all nesting is closed
                            if brace_count == 0 and paren_count == 0 and bracket_count == 0:
                                return '\n'.join(content_lines)
                    
                    j += 1
                
                # Check if we've found the start of a new rule (which means current rule ended without semicolon)
                if i > start_line:
                    next_rule_match = re.match(r'^\s*(fragment\s+)?([a-zA-Z_][a-zA-Z0-9_]*)\s*:', line)
                    if next_rule_match:
                        # Remove the incorrectly added line and return
                        content_lines.pop()
                        return '\n'.join(content_lines)
        
        return '\n'.join(content_lines)
    
    def _parse_alternatives(self, rule_content: str) -> List[Alternative]:
        """Parse alternatives from rule content."""
        alternatives = []
        
        # Remove the rule name and colon
        content = re.sub(r'^[^:]*:', '', rule_content, flags=re.MULTILINE)
        content = content.replace(';', '').strip()
        
        # Split by | but not inside parentheses or brackets
        alt_parts = self._split_alternatives(content)
        
        for alt_text in alt_parts:
            alt_text = alt_text.strip()
            if not alt_text:
                continue
            
            # Check for alternative label
            label = None
            if '#' in alt_text:
                parts = alt_text.rsplit('#', 1)
                if len(parts) == 2:
                    alt_text = parts[0].strip()
                    label = parts[1].strip()
            
            # Parse elements (simplified)
            elements = self._parse_elements(alt_text)
            
            alternatives.append(Alternative(
                elements=elements,
                label=label
            ))
        
        return alternatives
    
    def _split_alternatives(self, content: str) -> List[str]:
        """Split alternatives by | while respecting nesting."""
        alternatives = []
        current = ""
        paren_depth = 0
        bracket_depth = 0
        
        i = 0
        while i < len(content):
            char = content[i]
            
            if char == '(':
                paren_depth += 1
            elif char == ')':
                paren_depth -= 1
            elif char == '[':
                bracket_depth += 1
            elif char == ']':
                bracket_depth -= 1
            elif char == '|' and paren_depth == 0 and bracket_depth == 0:
                alternatives.append(current.strip())
                current = ""
                i += 1
                continue
            
            current += char
            i += 1
        
        if current.strip():
            alternatives.append(current.strip())
        
        return alternatives
    
    def _parse_elements(self, alt_text: str) -> List[Element]:
        """Parse elements from alternative text (simplified)."""
        elements = []
        
        # Remove lexer commands (-> skip, -> channel(...), etc.)
        alt_text = re.sub(r'->\s*\w+(\([^)]*\))?', '', alt_text)
        
        # Remove mode commands
        alt_text = re.sub(r'->\s*(mode|pushMode|popMode)\s*\([^)]*\)', '', alt_text)
        
        # Handle character ranges in brackets properly
        # Replace [a-z] style patterns with a placeholder to avoid splitting issues
        bracket_patterns = re.findall(r'\[[^\]]+\]', alt_text)
        for i, pattern in enumerate(bracket_patterns):
            placeholder = f"__BRACKET_{i}__"
            alt_text = alt_text.replace(pattern, placeholder)
        
        # Simple tokenization - split by whitespace but preserve quoted strings
        tokens = re.findall(r"'[^']*'|\"[^\"]*\"|\S+", alt_text)
        
        # Restore bracket patterns
        for i, pattern in enumerate(bracket_patterns):
            placeholder = f"__BRACKET_{i}__"
            tokens = [pattern if t == placeholder else t for t in tokens]
        
        for token in tokens:
            if not token:
                continue
            
            element_type = "unknown"
            if token.startswith("'") or token.startswith('"'):
                element_type = "terminal"
            elif token.startswith('[') and token.endswith(']'):
                element_type = "char_set"
            elif token[0].isupper():
                element_type = "token_ref"
            elif token[0].islower():
                element_type = "rule_ref"
            elif token in ['?', '*', '+']:
                element_type = "suffix"
            
            elements.append(Element(
                text=token,
                range=Range(Position(1, 1), Position(1, len(token))),
                element_type=element_type
            ))
        
        return elements
    
    def _extract_options(self, content: str) -> dict:
        """Extract options from grammar content."""
        options = {}
        
        # Simple regex to find options block
        options_match = re.search(r'options\s*\{([^}]*)\}', content, re.DOTALL)
        if options_match:
            options_content = options_match.group(1)
            
            # Parse individual options
            for line in options_content.split('\n'):
                line = line.strip()
                if '=' in line and not line.startswith('//'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().rstrip(';').strip('"\'')
                    options[key] = value
        
        return options
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements."""
        imports = []
        
        for line in content.split('\n'):
            line = line.strip()
            if line.startswith('import '):
                import_match = re.match(r'import\s+([^;]+);', line)
                if import_match:
                    imports.extend([imp.strip() for imp in import_match.group(1).split(',')])
        
        return imports
    
    def _extract_tokens(self, content: str) -> List[str]:
        """Extract tokens declarations."""
        tokens = []
        
        tokens_match = re.search(r'tokens\s*\{([^}]*)\}', content, re.DOTALL)
        if tokens_match:
            tokens_content = tokens_match.group(1)
            for line in tokens_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('//'):
                    tokens.extend([token.strip() for token in line.split(',') if token.strip()])
        
        return tokens
    
    def _extract_channels(self, content: str) -> List[str]:
        """Extract channels declarations."""
        channels = []
        
        channels_match = re.search(r'channels\s*\{([^}]*)\}', content, re.DOTALL)
        if channels_match:
            channels_content = channels_match.group(1)
            for line in channels_content.split('\n'):
                line = line.strip()
                if line and not line.startswith('//'):
                    channels.extend([channel.strip() for channel in line.split(',') if channel.strip()])
        
        return channels