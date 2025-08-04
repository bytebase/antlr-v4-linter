/*
 * Test Grammar with Block Comments
 * This is a multi-line block comment
 * that should be handled correctly
 */
grammar TestComments;

/* This is another block comment before a rule */
program: statement* EOF;

/*
 * Statement rule with block comment
 * Can be assignment or expression
 */
statement
    : assignment  /* inline comment */
    | expression
    ;

/* Assignment rule */
assignment: ID '=' expression ';';

expression
    : expression '+' expression  /* addition */
    | expression '-' expression  /* subtraction */
    | ID
    | NUMBER
    ;

/* Lexer rules with comments */
ID: [a-zA-Z_][a-zA-Z0-9_]*;

/*
 * Number token
 * Matches integers
 */
NUMBER: [0-9]+;

/* Skip whitespace */
WS: [ \t\r\n]+ -> skip;

// This is a line comment
COMMENT: '//' .*? '\n' -> skip;