grammar TestGrammar;

// Main entry point - should trigger S001
program: statement* ;

// Helper rules - should NOT trigger S001
statement: assignment | expression ;
assignment: ID '=' expression ;
expression: term ('+' term)* ;
term: ID | NUMBER ;

// Another potential entry point
compilationUnit: importDecl* classDecl* ;
importDecl: 'import' ID ;
classDecl: 'class' ID '{' '}' ;

// Lexer rules
ID: [a-zA-Z]+ ;
NUMBER: [0-9]+ ;
WS: [ \t\r\n]+ -> skip ;
EOF < /dev/null