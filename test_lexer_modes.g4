lexer grammar TestLexer;

// Default mode tokens
PACKAGE: 'package';
IMPORT: 'import';
CLASS: 'class';
INTERFACE: 'interface';
ENUM: 'enum';
EXTENDS: 'extends';
IMPLEMENTS: 'implements';

// Operators
ASSIGN: '=';
GT: '>';
LT: '<';
BANG: '!';
QUESTION: '?';
COLON: ':';
EQUAL: '==';
LE: '<=';
GE: '>=';
NOTEQUAL: '!=';
AND: '&&';
OR: '||';
INC: '++';
DEC: '--';
ADD: '+';
SUB: '-';
MUL: '*';
DIV: '/';
BITAND: '&';
BITOR: '|';
CARET: '^';
MOD: '%';

// Delimiters
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
LBRACK: '[';
RBRACK: ']';
SEMICOLON: ';';
COMMA: ',';
DOT: '.';
ELLIPSIS: '...';
AT: '@';
COLONCOLON: '::';

// Literals
DECIMAL_LITERAL: ('0' | [1-9] Digits?);
HEX_LITERAL: '0' [xX] HexDigits;
BINARY_LITERAL: '0' [bB] BinaryDigits;

FLOAT_LITERAL: Digits '.' Digits? ExponentPart? FloatTypeSuffix?
    | '.' Digits ExponentPart? FloatTypeSuffix?
    | Digits ExponentPart FloatTypeSuffix?
    | Digits FloatTypeSuffix
    ;

BOOL_LITERAL: 'true' | 'false';
NULL_LITERAL: 'null';

// String literals with different modes
STRING: '"' StringCharacters? '"' -> mode(DEFAULT_MODE);
CHAR: '\'' SingleCharacter '\'' 
    | '\'' EscapeSequence '\''
    ;

// Text block (Java 15+)
TEXT_BLOCK: '"""' .*? '"""';

// Identifiers
IDENTIFIER: Letter LetterOrDigit*;

// Whitespace and comments
WS: [ \t\r\n\u000C]+ -> channel(HIDDEN);
COMMENT: '/*' .*? '*/' -> channel(HIDDEN);
LINE_COMMENT: '//' ~[\r\n]* -> channel(HIDDEN);

// Fragments
fragment Digits: [0-9]+;
fragment HexDigits: HexDigit+;
fragment HexDigit: [0-9a-fA-F];
fragment BinaryDigits: BinaryDigit+;
fragment BinaryDigit: [01];
fragment ExponentPart: [eE] [+-]? Digits;
fragment FloatTypeSuffix: [fFdD];
fragment StringCharacters: StringCharacter+;
fragment StringCharacter: ~["\\\r\n] | EscapeSequence;
fragment SingleCharacter: ~['\\\r\n];
fragment EscapeSequence
    : '\\' [btnfr"'\\]
    | '\\' OctalEscape
    | '\\' 'u' HexDigit HexDigit HexDigit HexDigit
    ;
fragment OctalEscape
    : [0-3] OctalDigit OctalDigit
    | OctalDigit OctalDigit
    | OctalDigit
    ;
fragment OctalDigit: [0-7];
fragment Letter: [a-zA-Z$_];
fragment LetterOrDigit: [a-zA-Z0-9$_];

// Mode for inside strings (example)
mode STRING_MODE;
STRING_TEXT: ~["\\\r\n]+;
STRING_ESCAPE: '\\' .;
STRING_END: '"' -> mode(DEFAULT_MODE);

// Mode for template processing
mode TEMPLATE;
TEMPLATE_TEXT: ~[{]+;
TEMPLATE_OPEN: '{' -> pushMode(DEFAULT_MODE);
TEMPLATE_CLOSE: '}' -> popMode;