grammar BadGrammar;

// Missing EOF token
program: statement*;

// Parser rule starts with uppercase (N001)
Statement: assignment | expression;

// Lexer rule starts with lowercase (N002)
id: [a-zA-Z_][a-zA-Z0-9_]*;

assignment: id ASSIGN expression;

expression: expression '+' expression | id | NUMBER;

// Mixed naming conventions (N003)
snake_case_rule: ID;
camelCaseRule: NUMBER;

// Lexer rules with inconsistent naming
NUMBER: [0-9]+;

// Ambiguous string literals (S003)
PLUS: '+';
ADD: '+';  // Same literal as PLUS

// Missing whitespace skip rule
// Missing ANY rule at end