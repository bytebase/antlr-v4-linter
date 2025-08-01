grammar ANTLRGrammar;

// Main grammar entry point
grammarSpec
    : grammarDecl prequelConstruct* rules_ EOF
    ;

grammarDecl
    : grammarType id SEMI
    ;

grammarType
    : LEXER GRAMMAR
    | PARSER GRAMMAR  
    | GRAMMAR
    ;

prequelConstruct
    : optionsSpec
    | delegateGrammars
    | tokensSpec
    | channelsSpec
    | action_
    ;

optionsSpec
    : OPTIONS (option SEMI)* RBRACE
    ;

option
    : id ASSIGN optionValue
    ;

optionValue
    : id (DOT id)*
    | STRING_LITERAL
    | actionBlock
    | INT
    ;

delegateGrammars
    : IMPORT delegateGrammar (COMMA delegateGrammar)* SEMI
    ;

delegateGrammar
    : id ASSIGN id
    | id
    ;

tokensSpec
    : TOKENS id (COMMA id)* RBRACE
    ;

channelsSpec
    : CHANNELS id (COMMA id)* RBRACE
    ;

action_
    : AT (actionScopeName COLONCOLON)? id actionBlock
    ;

actionScopeName
    : id
    | LEXER
    | PARSER
    ;

actionBlock
    : LBRACE .*? RBRACE
    ;

rules_
    : ruleSpec*
    ;

ruleSpec
    : parserRuleSpec
    | lexerRuleSpec
    ;

parserRuleSpec
    : ruleModifiers? RULE_REF argActionBlock? ruleReturns? throwsSpec? localsSpec? rulePrequel* COLON ruleAltList SEMI exceptionGroup*
    ;

lexerRuleSpec
    : FRAGMENT? TOKEN_REF COLON lexerRuleBlock SEMI
    ;

ruleModifiers
    : ruleModifier+
    ;

ruleModifier
    : PUBLIC
    | PRIVATE
    | PROTECTED
    | FRAGMENT
    ;

ruleReturns
    : RETURNS argActionBlock
    ;

throwsSpec
    : THROWS id (COMMA id)*
    ;

localsSpec
    : LOCALS argActionBlock
    ;

rulePrequel
    : optionsSpec
    | ruleAction
    ;

ruleAction
    : AT id actionBlock
    ;

ruleAltList
    : labeledAlt (OR labeledAlt)*
    ;

labeledAlt
    : alternative (POUND id)?
    ;

alternative
    : elementOptions? element*
    ;

element
    : labeledElement (ebnfSuffix |)
    | atom (ebnfSuffix |)
    | ebnf
    | actionBlock (QUESTION predicateOptions?)?
    ;

labeledElement
    : id (ASSIGN | PLUS_ASSIGN) (atom | block)
    ;

ebnf
    : block blockSuffix?
    ;

blockSuffix
    : ebnfSuffix
    ;

ebnfSuffix
    : QUESTION QUESTION?
    | STAR QUESTION?
    | PLUS QUESTION?
    ;

lexerRuleBlock
    : lexerAltList
    ;

lexerAltList
    : lexerAlt (OR lexerAlt)*
    ;

lexerAlt
    : lexerElements lexerCommands?
    ;

lexerElements
    : lexerElement*
    ;

lexerElement
    : labeledLexerElement ebnfSuffix?
    | lexerAtom ebnfSuffix?
    | lexerBlock ebnfSuffix?
    | actionBlock QUESTION?
    ;

labeledLexerElement
    : id (ASSIGN | PLUS_ASSIGN) (lexerAtom | lexerBlock)
    ;

lexerBlock
    : LPAREN lexerAltList RPAREN
    ;

lexerCommands
    : RARROW lexerCommand (COMMA lexerCommand)*
    ;

lexerCommand
    : lexerCommandName LPAREN lexerCommandExpr RPAREN
    | lexerCommandName
    ;

lexerCommandName
    : id
    | MODE
    ;

lexerCommandExpr
    : id
    | INT
    ;

atom
    : terminal
    | ruleref
    | notSet
    | DOT elementOptions?
    ;

lexerAtom
    : terminal
    | notSet
    | lexerCharSet
    | DOT elementOptions?
    ;

notSet
    : NOT setElement
    | NOT blockSet
    ;

blockSet
    : LPAREN setElement (OR setElement)* RPAREN
    ;

setElement
    : TOKEN_REF elementOptions?
    | STRING_LITERAL elementOptions?
    | range
    | lexerCharSet
    ;

lexerCharSet
    : LBRACKET lexerCharSetBody RBRACKET
    ;

lexerCharSetBody
    : lexerCharSetRange*
    ;

lexerCharSetRange
    : lexerCharInSet
    | lexerCharInSet RANGE lexerCharInSet
    ;

lexerCharInSet
    : STRING_LITERAL
    | TOKEN_REF
    ;

range
    : STRING_LITERAL RANGE STRING_LITERAL
    ;

terminal
    : TOKEN_REF elementOptions?
    | STRING_LITERAL elementOptions?
    ;

ruleref
    : RULE_REF argActionBlock? elementOptions?
    ;

elementOptions
    : LT elementOption (COMMA elementOption)* GT
    ;

elementOption
    : id
    | id ASSIGN (id | STRING_LITERAL)
    ;

id
    : RULE_REF
    | TOKEN_REF
    ;

// Lexer Rules
fragment
LETTER : [a-zA-Z$_]
       | ~[\u0000-\u007F\uD800-\uDBFF] 
       | [\uD800-\uDBFF] [\uDC00-\uDFFF]
       ;

fragment
DIGIT : [0-9] ;

RULE_REF : [a-z] (LETTER | DIGIT)*;
TOKEN_REF : [A-Z] (LETTER | DIGIT)*;

INT : DIGIT+ ;

STRING_LITERAL
    : '\'' (ESCAPE_SEQUENCE | ~[\\'\r\n])* '\''
    ;

fragment
ESCAPE_SEQUENCE
    : '\\' ['"\\bnrtfav]
    | '\\' [0-3] [0-7] [0-7]
    | '\\' [0-7] [0-7]
    | '\\' [0-7]
    | '\\' 'u' HEX_DIGIT HEX_DIGIT HEX_DIGIT HEX_DIGIT
    ;

fragment
HEX_DIGIT : [0-9a-fA-F] ;

// Keywords
GRAMMAR : 'grammar';
LEXER : 'lexer';
PARSER : 'parser';
OPTIONS : 'options' -> pushMode(OPTIONS_MODE);
TOKENS : 'tokens' -> pushMode(TOKENS_MODE);
CHANNELS : 'channels' -> pushMode(CHANNELS_MODE);
IMPORT : 'import';
FRAGMENT : 'fragment';
PUBLIC : 'public';
PRIVATE : 'private';
PROTECTED : 'protected';
RETURNS : 'returns';
LOCALS : 'locals';
THROWS : 'throws';
CATCH : 'catch';
FINALLY : 'finally';
MODE : 'mode';

// Operators and punctuation
COLON : ':';
COLONCOLON : '::';
COMMA : ',';
SEMI : ';';
LPAREN : '(';
RPAREN : ')';
LBRACE : '{';
RBRACE : '}';
LBRACKET : '[';
RBRACKET : ']';
RARROW : '->';
LT : '<';
GT : '>';
ASSIGN : '=';
QUESTION : '?';
STAR : '*';
PLUS : '+';
PLUS_ASSIGN : '+=';
OR : '|';
DOLLAR : '$';
RANGE : '..';
DOT : '.';
AT : '@';
POUND : '#';
NOT : '~';

// Comments and whitespace
DOC_COMMENT : '/**' .*? '*/' -> channel(HIDDEN);
BLOCK_COMMENT : '/*' .*? '*/' -> channel(HIDDEN);
LINE_COMMENT : '//' ~[\n\r]* -> channel(HIDDEN);
WS : [ \t\n\r\f]+ -> skip;

// Modes
mode OPTIONS_MODE;
OPT_DOT : '.';
OPT_ASSIGN : '=';
OPT_STRING_LITERAL : STRING_LITERAL;
OPT_INT : INT;
OPT_STAR : '*';
OPT_RBRACE : '}' -> popMode;
OPT_ID : RULE_REF | TOKEN_REF;
OPT_WS : WS -> skip;

mode TOKENS_MODE;
TOK_COMMA : ',';
TOK_RBRACE : '}' -> popMode;
TOK_ID : RULE_REF | TOKEN_REF;
TOK_WS : WS -> skip;

mode CHANNELS_MODE;
CHN_COMMA : ',';
CHN_RBRACE : '}' -> popMode;
CHN_ID : RULE_REF | TOKEN_REF;
CHN_WS : WS -> skip;