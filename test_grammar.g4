grammar TestGrammar;

// Parser rules
Program: statement* EOF;  // Should trigger N001 - uppercase start

statement
    : assignment
    | ifStatement
    | whileStatement
    | expression
    ;

assignment: ID '=' expression ';';

ifStatement: 'if' '(' expression ')' statement ('else' statement)?;

whileStatement: 'while' '(' expression ')' statement;

// Complex rule that should trigger C001
expression
    : expression '*' expression
    | expression '/' expression  
    | expression '+' expression
    | expression '-' expression
    | expression '>' expression
    | expression '<' expression
    | expression '==' expression
    | expression '!=' expression
    | expression '&&' expression
    | expression '||' expression
    | '(' expression ')'
    | ID
    | NUMBER
    | STRING
    ;

// Lexer rules
id: [a-z]+;  // Should trigger N002 - lowercase start

ID: [a-zA-Z_][a-zA-Z0-9_]*;
NUMBER: [0-9]+;
STRING: '"' .*? '"';

// Overlapping tokens - should trigger T001
KEYWORD: 'if' | 'else' | 'while';

// Whitespace
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' .*? '\n' -> skip;

// Unused token - should trigger T003
UNUSED_TOKEN: 'unused';