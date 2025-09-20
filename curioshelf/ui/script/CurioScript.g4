grammar CurioScript;

// Parser rules
program: statement* EOF;

statement: assignment
         | command
         | ifStatement
         | foreachStatement
         | pushStatement
         | popStatement
         | block
         ;

assignment: IDENTIFIER '=' expression;

command: IDENTIFIER '(' argumentList? ')';

ifStatement: 'if' '(' expression ')' statement ('else' statement)?;

foreachStatement: 'foreach' '(' IDENTIFIER 'in' expression ')' statement;

pushStatement: 'push' expression;

popStatement: 'pop' IDENTIFIER?;

block: '{' statement* '}';

argumentList: expression (',' expression)*;

expression: logicalOr;

logicalOr: logicalAnd ('||' logicalAnd)*;

logicalAnd: equality ('&&' equality)*;

equality: comparison (('==' | '!=') comparison)*;

comparison: addition (('<' | '>' | '<=' | '>=') addition)*;

addition: multiplication (('+' | '-') multiplication)*;

multiplication: unary (('*' | '/' | '%') unary)*;

unary: ('!' | '-') unary
     | primary
     ;

primary: literal
       | IDENTIFIER
       | '(' expression ')'
       | functionCall
       ;

functionCall: IDENTIFIER '(' argumentList? ')';

literal: STRING
       | NUMBER
       | BOOLEAN
       ;

// Lexer rules
IDENTIFIER: [a-zA-Z_][a-zA-Z0-9_]*;

STRING: '"' (~["\\] | '\\' .)* '"'
      | '\'' (~['\\] | '\\' .)* '\''
      ;

NUMBER: [0-9]+ ('.' [0-9]+)?;

BOOLEAN: 'true' | 'false';

// Operators
PLUS: '+';
MINUS: '-';
MULTIPLY: '*';
DIVIDE: '/';
MODULO: '%';
EQUAL: '==';
NOT_EQUAL: '!=';
LESS_THAN: '<';
GREATER_THAN: '>';
LESS_EQUAL: '<=';
GREATER_EQUAL: '>=';
AND: '&&';
OR: '||';
NOT: '!';

// Keywords
IF: 'if';
ELSE: 'else';
FOREACH: 'foreach';
IN: 'in';
PUSH: 'push';
POP: 'pop';

// Punctuation
ASSIGN: '=';
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
COMMA: ',';
SEMICOLON: ';';

// Whitespace and comments
WS: [ \t\r\n]+ -> skip;
COMMENT: '//' ~[\r\n]* -> skip;
BLOCK_COMMENT: '/*' .*? '*/' -> skip;
