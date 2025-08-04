// Sample ANTLR4 grammar with advanced features
parser grammar TestParser;

options {
    tokenVocab = TestLexer;
    superClass = BaseParser;
}

@header {
    package com.example;
    import java.util.*;
}

@members {
    private boolean isType() {
        return true;
    }
}

// Parser rules
compilationUnit
    : packageDeclaration? importDeclaration* typeDeclaration* EOF
    ;

packageDeclaration
    : PACKAGE qualifiedName SEMICOLON
    ;

importDeclaration
    : IMPORT STATIC? qualifiedName (DOT STAR)? SEMICOLON
    ;

typeDeclaration
    : classDeclaration
    | interfaceDeclaration
    | enumDeclaration
    | ';'
    ;

classDeclaration
    : CLASS IDENTIFIER typeParameters?
      (EXTENDS type)?
      (IMPLEMENTS typeList)?
      classBody
    ;

// Rules with semantic predicates
expression
    : {isType()}? type
    | primary
    ;

// Rules with arguments and returns
methodDeclaration[boolean isAbstract] returns [Type returnType]
    : type IDENTIFIER formalParameters
      (THROWS qualifiedNameList)?
      methodBody?
    ;

// Rules with local variables
statement
    locals [int count = 0]
    : block
    | IF parExpression statement (ELSE statement)?
    | FOR LPAREN forControl RPAREN statement
    | WHILE parExpression statement
    | DO statement WHILE parExpression SEMICOLON
    | TRY block (catchClause+ finallyBlock? | finallyBlock)
    | SWITCH parExpression LBRACE switchBlockStatementGroup* switchLabel* RBRACE
    | SYNCHRONIZED parExpression block
    | RETURN expression? SEMICOLON
    | THROW expression SEMICOLON
    | BREAK IDENTIFIER? SEMICOLON
    | CONTINUE IDENTIFIER? SEMICOLON
    | SEMICOLON
    | statementExpression SEMICOLON
    | IDENTIFIER COLON statement
    ;

// Rules with labels
primary
    : literal                                   # primaryLiteral
    | IDENTIFIER                               # primaryIdentifier
    | THIS                                     # primaryThis
    | SUPER                                    # primarySuper
    | LPAREN expression RPAREN                 # primaryParens
    | NEW creator                              # primaryNew
    | fieldAccess                              # primaryFieldAccess
    | arrayAccess                              # primaryArrayAccess
    | methodCall                               # primaryMethodCall
    ;

// Catch block for error handling
catchClause
    : CATCH LPAREN catchType IDENTIFIER RPAREN block
    ;

// Fragment-like parser rule (though fragments are lexer-only)
qualifiedName
    : IDENTIFIER (DOT IDENTIFIER)*
    ;

type
    : primitiveType (LBRACK RBRACK)*
    | classType (LBRACK RBRACK)*
    ;

primitiveType
    : BOOLEAN
    | BYTE
    | SHORT
    | INT
    | LONG
    | FLOAT
    | DOUBLE
    | CHAR
    ;

classType
    : IDENTIFIER typeArguments? (DOT IDENTIFIER typeArguments?)*
    ;

typeArguments
    : LT typeArgument (COMMA typeArgument)* GT
    ;

typeArgument
    : type
    | QUESTION ((EXTENDS | SUPER) type)?
    ;

typeParameters
    : LT typeParameter (COMMA typeParameter)* GT
    ;

typeParameter
    : IDENTIFIER (EXTENDS typeBound)?
    ;

typeBound
    : type (AMPERSAND type)*
    ;

typeList
    : type (COMMA type)*
    ;

qualifiedNameList
    : qualifiedName (COMMA qualifiedName)*
    ;

formalParameters
    : LPAREN formalParameterList? RPAREN
    ;

formalParameterList
    : formalParameter (COMMA formalParameter)* (COMMA lastFormalParameter)?
    | lastFormalParameter
    ;

formalParameter
    : variableModifier* type variableDeclaratorId
    ;

lastFormalParameter
    : variableModifier* type ELLIPSIS variableDeclaratorId
    ;

variableModifier
    : FINAL
    | annotation
    ;

annotation
    : AT qualifiedName (LPAREN (elementValuePairs | elementValue)? RPAREN)?
    ;

elementValuePairs
    : elementValuePair (COMMA elementValuePair)*
    ;

elementValuePair
    : IDENTIFIER ASSIGN elementValue
    ;

elementValue
    : expression
    | annotation
    | elementValueArrayInitializer
    ;

elementValueArrayInitializer
    : LBRACE (elementValue (COMMA elementValue)*)? COMMA? RBRACE
    ;

variableDeclaratorId
    : IDENTIFIER (LBRACK RBRACK)*
    ;

block
    : LBRACE blockStatement* RBRACE
    ;

blockStatement
    : localVariableDeclaration SEMICOLON
    | statement
    | typeDeclaration
    ;

localVariableDeclaration
    : variableModifier* type variableDeclarators
    ;

variableDeclarators
    : variableDeclarator (COMMA variableDeclarator)*
    ;

variableDeclarator
    : variableDeclaratorId (ASSIGN variableInitializer)?
    ;

variableInitializer
    : arrayInitializer
    | expression
    ;

arrayInitializer
    : LBRACE (variableInitializer (COMMA variableInitializer)* COMMA?)? RBRACE
    ;

classBody
    : LBRACE classBodyDeclaration* RBRACE
    ;

classBodyDeclaration
    : SEMICOLON
    | STATIC? block
    | modifier* memberDeclaration
    ;

memberDeclaration
    : methodDeclaration[false]
    | fieldDeclaration
    | constructorDeclaration
    | interfaceDeclaration
    | classDeclaration
    | enumDeclaration
    ;

methodBody
    : block
    ;

constructorDeclaration
    : IDENTIFIER formalParameters (THROWS qualifiedNameList)? constructorBody
    ;

constructorBody
    : block
    ;

fieldDeclaration
    : type variableDeclarators SEMICOLON
    ;

interfaceDeclaration
    : INTERFACE IDENTIFIER typeParameters? (EXTENDS typeList)? interfaceBody
    ;

interfaceBody
    : LBRACE interfaceBodyDeclaration* RBRACE
    ;

interfaceBodyDeclaration
    : modifier* interfaceMemberDeclaration
    | SEMICOLON
    ;

interfaceMemberDeclaration
    : constDeclaration
    | interfaceMethodDeclaration
    | interfaceDeclaration
    | classDeclaration
    ;

constDeclaration
    : type constantDeclarator (COMMA constantDeclarator)* SEMICOLON
    ;

constantDeclarator
    : IDENTIFIER (LBRACK RBRACK)* ASSIGN variableInitializer
    ;

interfaceMethodDeclaration
    : type IDENTIFIER formalParameters (LBRACK RBRACK)* (THROWS qualifiedNameList)? SEMICOLON
    ;

enumDeclaration
    : ENUM IDENTIFIER (IMPLEMENTS typeList)? enumBody
    ;

enumBody
    : LBRACE enumConstants? COMMA? enumBodyDeclarations? RBRACE
    ;

enumConstants
    : enumConstant (COMMA enumConstant)*
    ;

enumConstant
    : annotation* IDENTIFIER arguments? classBody?
    ;

enumBodyDeclarations
    : SEMICOLON classBodyDeclaration*
    ;

arguments
    : LPAREN expressionList? RPAREN
    ;

expressionList
    : expression (COMMA expression)*
    ;

parExpression
    : LPAREN expression RPAREN
    ;

forControl
    : forInit? SEMICOLON expression? SEMICOLON forUpdate?
    ;

forInit
    : localVariableDeclaration
    | expressionList
    ;

forUpdate
    : expressionList
    ;

switchBlockStatementGroup
    : switchLabel+ blockStatement+
    ;

switchLabel
    : CASE constantExpression COLON
    | CASE enumConstantName COLON
    | DEFAULT COLON
    ;

constantExpression
    : expression
    ;

enumConstantName
    : IDENTIFIER
    ;

finallyBlock
    : FINALLY block
    ;

catchType
    : qualifiedName (PIPE qualifiedName)*
    ;

creator
    : nonWildcardTypeArguments? createdName classCreatorRest
    | nonWildcardTypeArguments? createdName arrayCreatorRest
    ;

createdName
    : IDENTIFIER typeArgumentsOrDiamond? (DOT IDENTIFIER typeArgumentsOrDiamond?)*
    | primitiveType
    ;

classCreatorRest
    : arguments classBody?
    ;

arrayCreatorRest
    : LBRACK (RBRACK (LBRACK RBRACK)* arrayInitializer | expression RBRACK (LBRACK expression RBRACK)* (LBRACK RBRACK)*)
    ;

nonWildcardTypeArguments
    : LT typeList GT
    ;

typeArgumentsOrDiamond
    : LT GT
    | typeArguments
    ;

fieldAccess
    : primary DOT IDENTIFIER
    | SUPER DOT IDENTIFIER
    ;

arrayAccess
    : (primary | IDENTIFIER) (LBRACK expression RBRACK)+
    ;

methodCall
    : IDENTIFIER arguments
    | primary DOT IDENTIFIER arguments
    | SUPER DOT IDENTIFIER arguments
    ;

statementExpression
    : expression
    ;

literal
    : IntegerLiteral
    | FloatingPointLiteral
    | CharacterLiteral
    | StringLiteral
    | BooleanLiteral
    | NULL
    ;

modifier
    : PUBLIC
    | PROTECTED
    | PRIVATE
    | STATIC
    | ABSTRACT
    | FINAL
    | NATIVE
    | SYNCHRONIZED
    | TRANSIENT
    | VOLATILE
    ;