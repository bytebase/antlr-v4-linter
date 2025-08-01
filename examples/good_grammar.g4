grammar GoodGrammar;

// Main parser rule with EOF
program: statement* EOF;

// Well-named parser rules (lowercase)
statement
    : assignment #assignmentStmt
    | expression #expressionStmt
    ;

assignment: ID ASSIGN expression;

expression
    : expression MULT expression #multiplication
    | expression PLUS expression #addition
    | ID #identifier
    | NUMBER #number
    ;

// Well-named lexer rules (uppercase)
ID: [a-zA-Z_][a-zA-Z0-9_]*;
NUMBER: [0-9]+;

// String literals used only once
ASSIGN: '=';
PLUS: '+';
MULT: '*';

// Proper whitespace handling
WS: [ \t\n\r\f]+ -> skip;

// Catch-all rule at the end
ANY: .;