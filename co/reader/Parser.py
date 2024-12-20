from enum import Enum
from typing import List
from collections import deque

from co import ast
from co.reader import Token
from co.reader import Lexer
from co import st

class Parser:

  def __init__ (self, input: Lexer):
    self.input: Lexer = input
    self.k: int = 3
    self.p: int = 0
    # Create and prime lookahead buffer for LL(k) parser
    # To do: We are assuming there is at least k tokens available.
    # What if that is not the case?
    self.buffer: list[Token] = []
    for i in range(self.k):
      t = self.input.getToken()
      self.buffer.append(t)
    self.lookahead = self.peekahead(0)
    # Old, remove once predictive parser works
    # self.lookahead: Token = self.input.getToken()

  def match (self, kind: str):
    if self.lookahead.kind == kind:
      self.consume()
    else:
      msg = f"Invalid token. Expected {kind}, got {self.lookahead.kind}."
      # Should this really be an exception, or should we do sync recovery?
      raise Exception(msg)

  def consume (self):
    self.buffer[self.p] = self.input.getToken()
    self.p = (self.p + 1) % self.k
    self.lookahead = self.peekahead(0)
    # Old, remove once predictive parser works
    # self.lookahead = self.input.getToken()

  def peekahead (self, index: int):
    return self.buffer[(self.p + index) % self.k]

  def process (self):
    n = self.translationUnit()
    return n

  # BEGIN

  def translationUnit (self) -> ast.AstNode:
    n = ast.AstNode('TranslationUnit')
    # For now the package clause is optional. If not specified then
    # it is assumed to be the name of the directory that the source
    # file is located in. The exception to that might be the main
    # package because it might not be in a directory named 'main'.
    # UPDATE: Intentions are to remove the package declaration if
    # possible. A package will just be a directory full of source
    # files. The name of the package is the directory name in which
    # the source file(s) are located.
    if self.lookahead.kind == 'PACKAGE':
      n.add_child(self.packageClause())
    while self.lookahead.kind != 'EOF':
      n.add_child(self.declaration())
    return n

  def packageClause (self) -> ast.AstNode:
    n = ast.AstNode('PackageClause')
    self.match('PACKAGE')
    # For now, ignore any package name nesting
    n.add_child(self.name())
    self.match('SEMICOLON')
    return n

  # DECLARATIONS

  # We might need to break declarations into global, local, inner,
  # etc. We already have declarations vs. declaration statements, but
  # not very sophisticated.

  def declaration (self) -> ast.AstNode:
    # To do: Need to pass modifiers in or append, possibly use k lookahead
    # if self.lookahead.kind in [ 'PRIVATE', 'PUBLIC', 'STATIC' ]:
    #   p = self.modifierList()
    match self.lookahead.kind:
      case 'CLASS':
        n = self.classDeclaration()
      case 'CONST':
        n = self.constantDeclaration()
      case 'DEF':
        n = self.functionDeclaration()
      case 'STRUCT':
        n = self.structureDeclaration()
      case 'TYPEALIAS':
        n = self.typealiasDeclaration()
      case 'UNION':
        n = self.unionDeclaration()
      case 'VAL':
        n = self.variableDeclarationFinal()
        n.set_attribute('is_global', True)
      case 'VAR':
        n = self.variableDeclaration()
        n.set_attribute('is_global', True)
      case _:
        # Replace with exception
        print("error: invalid declaration" + self.lookahead.kind)
    return n

  # def modifierList (self) -> ast.AstNode:
  #   n = ast.AstNode('ModifierList')
  #   while self.lookahead.kind in [ 'PRIVATE', 'PUBLIC', 'STATIC' ]:
  #     n.add_child(self.modifier())

  def classDeclaration (self) -> ast.AstNode:
    n = ast.AstNode('ClassDeclaration')
    self.match('CLASS')
    n.add_child(self.name())
    self.match('L_BRACE')
    while self.lookahead.kind != 'R_BRACE':
      n.add_child(self.classMember())
    self.match('R_BRACE')
    return n

  def classMember (self) -> ast.AstNode:
    pass
    # match self.lookahead.kind:
    #   case 'DEF':
    #     n = self.methodDeclaration()
    #   case 'VAL':
    #     n = self.memberVariableDeclaration()
    #   case 'VAR':
    #     n = self.memberConstantDeclaration()
    #   case _:
    #     pass
    # return n

  def constantDeclaration (self) -> ast.AstNode:
    self.match('CONST')
    match self.lookahead.kind:
      case 'DEF':
        n = self.functionDeclarationConstant()
      case 'VAL':
        n = self.variableDeclarationConstant()
      case 'VAR':
        n = self.variableDeclarationConstant()
      case _:
        # How to handle this... create error node? Enter panic mode
        # and look for synchronizing token?
        print("error: No match in constant declaration")
        n = None
    return n

  def variableDeclarationConstant (self) -> ast.AstNode:
    n = ast.AstNode('VariableDeclaration')
    # Do we need to set tokens on every node?
    # n.set_token(self.lookahead)
    # We might only allow constant objects to be vals in the future.
    # For now, allow val or var.
    if self.lookahead.kind == 'VAL':
      self.match('VAL')
    else:
      self.match('VAR')
    n.set_attribute('is_constant', True)
    n.add_child(self.name())
    # Optional type specifier
    # In rust, const declaration requires the type specifier.
    if self.lookahead.kind == 'COLON':
      self.match('COLON')
      n.add_child(self.type())
    else:
      n.add_child(self.alphaType())
    # Required initializer
    if self.lookahead.kind == 'EQUAL':
      self.match('EQUAL')
      n.add_child(self.expressionRoot())
    else:
      print("Error - missing initializer in constant variable definition")
    self.match('SEMICOLON')
    return n

  # Unlike java, final variables must be initialized at the time of
  # declaration.

  def variableDeclarationFinal (self) -> ast.AstNode:
    n = ast.AstNode('VariableDeclaration')
    self.match('VAL')
    n.set_attribute('is_final', True)
    if self.lookahead.kind == 'IDENTIFIER':
      n.add_child(self.name())
    else:
      self.error('IDENTIFIER')
    # Optional type specifier
    if self.lookahead.kind == 'COLON':
      self.match('COLON')
      n.add_child(self.type())
    else:
      n.add_child(self.alphaType())
    # Required initializer
    if self.lookahead.kind == 'EQUAL':
      self.match('EQUAL')
      n.add_child(self.expressionRoot())
    else:
      print("Error - missing initializer in final variable definition")
    self.match('SEMICOLON')
    return n

  def variableDeclaration (self) -> ast.AstNode:
    n = ast.AstNode('VariableDeclaration')
    self.match('VAR')
    n.set_attribute('is_constant', False)
    n.set_attribute('is_final', False)
    if self.lookahead.kind == 'IDENTIFIER':
      n.add_child(self.name())
    else:
      self.error('IDENTIFIER')
    # Optional type specifier
    if self.lookahead.kind == 'COLON':
      self.match('COLON')
      n.add_child(self.type())
    else:
      n.add_child(self.alphaType())
    # Optional initializer
    if self.lookahead.kind == 'EQUAL':
      self.match('EQUAL')
      n.add_child(self.expressionRoot())
    self.match('SEMICOLON')
    return n

  def alphaType (self):
    # Used for type inference on variable declarations
    n = ast.AstNode('AlphaType')
    return n

  def functionDeclaration (self) -> ast.AstNode:
    n = ast.AstNode('FunctionDeclaration')
    self.match('DEF')
    if self.lookahead.kind == 'IDENTIFIER':
      n.add_child(self.name())
    else:
      self.error('ID')
    n.add_child(self.parameterList())
    if self.lookahead.kind == 'MINUS_GREATER':
      self.match('MINUS_GREATER')
      n.add_child(self.type())
    else:
      p = ast.AstNode('VoidType')
      n.add_child(p)
    n.add_child(self.functionBody())
    return n

  def parameterList (self) -> ast.AstNode:
    n = ast.AstNode('ParameterList')
    self.match('L_PARENTHESIS')
    if self.lookahead.kind != 'R_PARENTHESIS':
      n.add_child(self.parameter())
      while self.lookahead.kind == 'COMMA':
        self.match('COMMA')
        n.add_child(self.parameter())
    self.match('R_PARENTHESIS')
    return n

  def parameter (self) -> ast.AstNode:
    n = ast.AstNode('Parameter')
    n.add_child(self.name())
    self.match('COLON')
    n.add_child(self.type())
    return n

  def functionBody (self) -> ast.AstNode:
    n = ast.AstNode('FunctionBody')
    if self.lookahead.kind == 'SEMICOLON':
      self.match('SEMICOLON')
    else:
      n.add_child(self.topBlock())
    return n

  # A top block is a special kind of block that does not create its
  # own scope. It simply uses the scope created by the function, and
  # is the same as a block in every other way.

  def topBlock (self) -> ast.AstNode:
    n = ast.AstNode('TopBlock')
    self.match('L_BRACE')
    while self.lookahead.kind != 'R_BRACE':
      # Blocks only contain statements? If so, then we can get rid of
      # blockElement
      n.add_child(self.blockElement())
    self.match('R_BRACE')
    return n

  def block (self) -> ast.AstNode:
    n = ast.AstNode('Block')
    self.match('L_BRACE')
    while self.lookahead.kind != 'R_BRACE':
      # Blocks only contain statements? If so, then we can get rid of
      # blockElement
      n.add_child(self.blockElement())
    self.match('R_BRACE')
    return n

  def blockElement (self) -> ast.AstNode:
    n = self.statement()
    return n

  # Todo: Should we have one that is used in declaration context and
  # another for use context? Declaration context needs to create a
  # symbol table entry. Or do we just handle that in another pass?
  def name (self) -> ast.AstNode:
    n = ast.AstNode('Name')
    n.set_token(self.lookahead)
    self.match('IDENTIFIER')
    return n

  def structureDeclaration (self) -> ast.AstNode:
    n = ast.AstNode('StructureDeclaration')
    self.match('STRUCT')
    n.add_child(self.name())
    n.add_child(self.structureBody())
    return n

  def structureBody (self) -> ast.AstNode:
    n = ast.AstNode('StructureBody')
    self.match('L_BRACE')
    while self.lookahead.kind != 'R_BRACE':
      n.add_child(self.structureMember())
    self.match('R_BRACE')
    return n

  def structureMember (self) -> ast.AstNode:
    n = ast.AstNode('StructureMember')
    n.add_child(self.name())
    self.match('COLON')
    n.add_child(self.type())
    self.match('SEMICOLON')
    return n

  def typealiasDeclaration (self) -> ast.AstNode:
    n = ast.AstNode('TypealiasDeclaration')
    self.match('TYPEALIAS')
    n.add_child(self.name())
    self.match('EQUAL')
    n.add_child(self.type())
    self.match('SEMICOLON')
    return n

  def unionDeclaration (self) -> ast.AstNode:
    n = ast.AstNode('UnionDeclaration')
    self.match('UNION')
    n.add_child(self.name())
    n.add_child(self.unionBody())
    return n

  def unionBody (self) -> ast.AstNode:
    n = ast.AstNode('UnionBody')
    self.match('L_BRACE')
    while self.lookahead.kind != 'R_BRACE':
      n.add_child(self.unionMember())
    self.match('R_BRACE')
    return n

  def unionMember (self) -> ast.AstNode:
    n = ast.AstNode('UnionMember')
    n.add_child(self.name())
    self.match('COLON')
    n.add_child(self.type())
    self.match('SEMICOLON')
    return n

  # STATEMENTS

  def statement (self) -> ast.AstNode:
    n: ast.AstNode = None
    # Lookahead set for expression statements
    expressionFirstSet = [
      'IDENTIFIER',
      'NULL',
      'FALSE',
      'THIS',
      'TRUE',
      'INT32_LITERAL',
      'INT64_LITERAL',
      'UINT32_LITERAL',
      'UINT64_LITERAL',
      'FLOAT32_LITERAL',
      'FLOAT64_LITERAL'
    ]
    match self.lookahead.kind:
      case 'BREAK':
        n = self.breakStatement()
      case 'CONTINUE':
        n = self.continueStatement()
      case 'DO':
        n = self.doStatement()
      case 'FOR':
        n = self.forStatement()
      case 'IF':
        n = self.ifStatement()
      case 'LOOP':
        n = self.loopStatement()
      case 'RETURN':
        n = self.returnStatement()
      case 'WHILE':
        n = self.whileStatement()
      case 'SEMICOLON':
        n = self.nullStatement()
      case item if item in [ 'VAL', 'VAR' ]:
        n = self.declarationStatement()
      case item if item in expressionFirstSet:
        n = self.expressionStatement()
      case _:
        print("ERROR - INVALID STATEMENT")
    return n

  def breakStatement (self) -> ast.AstNode:
    n = ast.AstNode('BreakStatement')
    self.match('BREAK')
    self.match('SEMICOLON')
    return n

  def continueStatement (self) -> ast.AstNode:
    n = ast.AstNode('ContinueStatement')
    self.match('CONTINUE')
    self.match('SEMICOLON')
    return n

  def doStatement (self) -> ast.AstNode:
    n = ast.AstNode('DoStatement')
    self.match('DO')
    self.match('WHILE')
    self.match('L_PARENTHESIS')
    n.add_child(self.expression())
    self.match('R_PARENTHESIS')
    if self.lookahead.kind == 'L_BRACE':
      n.add_child(self.block())
    else:
      n.add_child(self.blockElement())
    return n

  def declarationStatement (self) -> ast.AstNode:
    n = ast.AstNode('DeclarationStatement')
    if self.lookahead.kind == 'VAL':
      n.add_child(self.constantDeclaration())
    elif self.lookahead.kind == 'VAR':
      n.add_child(self.variableDeclaration())
    return n

  def expressionStatement (self) -> ast.AstNode:
    n = ast.AstNode('ExpressionStatement')
    n.add_child(self.expressionRoot())
    self.match('SEMICOLON')
    return n

  def forStatement (self) -> ast.AstNode:
    n = ast.AstNode('ForStatement')
    self.match('FOR')
    self.match('L_PARENTHESIS')
    n.add_child(self.name())
    self.match('IN')
    n.add_child(self.expressionRoot())
    self.match('R_PARENTHESIS')
    if self.lookahead.kind == 'L_BRACE':
      n.add_child(self.block())
    else:
      n.add_child(self.blockElement())
    return n

  def ifStatement (self) -> ast.AstNode:
    n = ast.AstNode('IfStatement')
    self.match('IF')
    self.match('L_PARENTHESIS')
    n.add_child(self.expressionRoot())
    self.match('R_PARENTHESIS')
    if self.lookahead.kind == 'L_BRACE':
      n.add_child(self.block())
    else:
      n.add_child(self.blockElement())
    return n

  def loopStatement (self) -> ast.AstNode:
    n = ast.AstNode('LoopStatement')
    self.match('LOOP')
    if self.lookahead.kind == 'L_PARENTHESIS':
      self.match('L_PARENTHESIS')
      # Init expression
      n.add_child(self.expressionRoot())
      self.match('SEMICOLON')
      # Cond expression
      n.add_child(self.expressionRoot())
      self.match('SEMICOLON')
      # Loop expression
      n.add_child(self.expressionRoot())
      self.match('R_PARENTHESIS')
    if self.lookahead.kind == 'L_BRACE':
      n.add_child(self.block())
    else:
      n.add_child(self.blockElement())
    return n

  def nullStatement (self) -> ast.AstNode:
    # This is known as an "empty" statement in Java
    n = ast.AstNode('NullStatement')
    self.match('SEMICOLON')
    return n

  def returnStatement (self) -> ast.AstNode:
    n = ast.AstNode('ReturnStatement')
    self.match('RETURN')
    n.add_child(self.expressionRoot())
    self.match('SEMICOLON')
    return n

  def whileStatement (self) -> ast.AstNode:
    n = ast.AstNode('WhileStatement')
    self.match('WHILE')
    self.match('L_PARENTHESIS')
    n.add_child(self.expressionRoot())
    self.match('R_PARENTHESIS')
    if self.lookahead.kind == 'L_BRACE':
      n.add_child(self.block())
    else:
      n.add_child(self.blockElement())
    return n
  
  # EXPRESSIONS

  def expressionRoot (self) -> ast.AstNode:
    # Create Expression root node here
    n = ast.AstNode('ExpressionRoot')
    n.add_child(self.expression())
    return n

  def expression (self) -> ast.AstNode:
    n = self.assignmentExpression()
    return n

  def assignmentExpression (self) -> ast.AstNode:
    n = self.logicalOrExpression()
    firstSet = [
      'EQUAL',
      'ASTERISK_EQUAL',
      'SLASH_EQUAL',
      'PERCENT_EQUAL',
      'PLUS_EQUAL',
      'MINUS_EQUAL',
      'LESS_LESS_EQUAL',
      'GREATER_GREATER_EQUAL',
      'AMPERSAND_EQUAL',
      'CARET_EQUAL',
      'BAR_EQUAL'
    ]
    while self.lookahead.kind in firstSet:
      p = n
      n = ast.AstNode('BinaryExpression')
      n.set_token(self.lookahead)
      n.add_child(p)
      self.match(self.lookahead.kind)
      p = self.logicalOrExpression()
      n.add_child(p)
    return n

  def logicalOrExpression (self) -> ast.AstNode:
    n = self.logicalAndExpression()
    while self.lookahead.kind == 'OR':
      p = n
      n = ast.AstNode('BinaryExpression')
      n.set_token(self.lookahead)
      n.add_child(p)
      self.match('OR')
      n.add_child(self.logicalAndExpression())
    return n

  def logicalAndExpression (self) -> ast.AstNode:
    n = self.inclusiveOrExpression()
    while self.lookahead.kind == 'AND':
      p = n
      n = ast.AstNode('BinaryExpression')
      n.set_token(self.lookahead)
      n.add_child(p)
      self.match('AND')
      n.add_child(self.inclusiveOrExpression())
    return n
  
  def inclusiveOrExpression (self) -> ast.AstNode:
    n = self.exclusiveOrExpression()
    while self.lookahead.kind == 'BAR':
      p = n
      n = ast.AstNode('BinaryExpression')
      n.set_token(self.lookahead)
      n.add_child(p)
      self.match('BAR')
      n.add_child(self.exclusiveOrExpression())
    return n

  def exclusiveOrExpression (self) -> ast.AstNode:
    n = self.andExpression()
    while self.lookahead.kind == 'CARET':
      p = n
      n = ast.AstNode('BinaryExpression')
      n.set_token(self.lookahead)
      n.add_child(p)
      self.match('CARET')
      n.add_child(self.andExpression())
    return n
  
  def andExpression (self) -> ast.AstNode:
    n = self.equalityExpression()
    while self.lookahead.kind == 'AMPERSAND':
      p = n
      n = ast.AstNode('BinaryExpression')
      n.set_token(self.lookahead)
      n.add_child(p)
      self.match('AMPERSAND')
      n.add_child(self.equalityExpression())
    return n

  def equalityExpression (self) -> ast.AstNode:
    n = self.relationalExpression()
    firstSet = ['EQUAL_EQUAL', 'EXCLAMATION_EQUAL']
    while self.lookahead.kind in firstSet:
      p = n
      n = ast.AstNode('BinaryExpression')
      n.set_token(self.lookahead)
      n.add_child(p)
      self.match(self.lookahead.kind)
      n.add_child(self.relationalExpression())
    return n

  def relationalExpression (self) -> ast.AstNode:
    n = self.shiftExpression()
    firstSet = ['GREATER', 'LESS', 'GREATER_EQUAL', 'LESS_EQUAL']
    while self.lookahead.kind in firstSet:
      p = n
      n = ast.AstNode('BinaryExpression')
      n.set_token(self.lookahead)
      n.add_child(p)
      self.match(self.lookahead.kind)
      n.add_child(self.shiftExpression())
    return n

  def shiftExpression (self) -> ast.AstNode:
    n = self.additiveExpression()
    firstSet = ['GREATER_GREATER', 'LESS_LESS']
    while self.lookahead.kind in firstSet:
      p = n
      n = ast.AstNode('BinaryExpression')
      n.set_token(self.lookahead)
      n.add_child(p)
      self.match(self.lookahead.kind)
      n.add_child(self.additiveExpression())
    return n

  def additiveExpression (self) -> ast.AstNode:
    n = self.multiplicativeExpression()
    firstSet = ['PLUS', 'MINUS']
    while self.lookahead.kind in firstSet:
      p = n
      n = ast.AstNode('BinaryExpression')
      n.set_token(self.lookahead)
      n.add_child(p)
      self.match(self.lookahead.kind)
      n.add_child(self.multiplicativeExpression())
    return n

  def multiplicativeExpression (self) -> ast.AstNode:
    n = self.unaryExpression()
    firstSet = ['ASTERISK', 'SLASH', 'PERCENT']
    while self.lookahead.kind in firstSet:
      p = n
      n = ast.AstNode('BinaryExpression')
      n.set_token(self.lookahead)
      n.add_child(p)
      self.match(self.lookahead.kind)
      n.add_child(self.unaryExpression())
    return n
  
  def unaryExpression (self) -> ast.AstNode:
    # Need to add tilde
    firstSet = ['ASTERISK', 'MINUS', 'PLUS', 'EXCLAMATION']
    if self.lookahead.kind in firstSet:
      n = ast.AstNode('UnaryExpression')
      n.set_token(self.lookahead)
      self.match(self.lookahead.kind)
      n.add_child(self.unaryExpression())
    else:
      n = self.primaryExpression()
    return n

  def primaryExpression (self) -> ast.AstNode:
    firstSet = [
      'NULL',
      'THIS',
      'FALSE',
      'TRUE',
      'FLOAT32_LITERAL',
      'FLOAT64_LITERAL',
      'INT32_LITERAL',
      'INT64_LITERAL',
      'UINT32_LITERAL',
      'UINT64_LITERAL',
      'STRING_LITERAL'
    ]
    match self.lookahead.kind:
      case 'IDENTIFIER':
        n = self.nameExpression()
      case 'IF':
        n = self.ifExpression()
      case 'L_PARENTHESIS':
        n = self.parenthesizedExpression()
      case item if item in firstSet:
        n = self.literal()
      case _:
        print("ERROR - INVALID PRIMARY EXPRESSION")
    return n

  def nameExpression (self) -> ast.AstNode:
    # We need to distinguish between identifiers used when defining
    # program elements and identifiers used when referencing program
    # elements. An alternative is to use a form of tree pattern
    # matching.
    n = self.name()
    firstSet = ['L_PARENTHESIS', 'L_BRACKET', 'MINUS_GREATER', 'PERIOD']
    while self.lookahead.kind in firstSet:
      p = n
      match self.lookahead.kind:
        case 'L_PARENTHESIS':
          n = self.functionCall(p)
        case 'L_BRACKET':
          n = self.arrayAccess(p)
        case 'MINUS_GREATER':
          n = self.derefAccess(p)
        case 'PERIOD':
          n = self.fieldAccess(p)
    return n

  # def identifier (self) -> ast.AstNode:
  #   n = ast.AstNode('Identifier')
  #   n.set_token(self.lookahead)
  #   self.match('IDENTIFIER')
  #   return n
  
  def functionCall (self, p: ast.AstNode) -> ast.AstNode:
    n = ast.AstNode('FunctionCall')
    n.add_child(p)
    n.add_child(self.argumentList())
    return n

  def argumentList (self) -> ast.AstNode:
    n = ast.AstNode('ArgumentList')
    self.match('L_PARENTHESIS')
    if self.lookahead.kind != 'R_PARENTHESIS':
      n.add_child(self.expression())
      while self.lookahead.kind == 'COMMA':
        self.match('COMMA')
        n.add_child(self.expression())
    self.match('R_PARENTHESIS')
    return n

  def arrayAccess (self, p: ast.AstNode) -> ast.AstNode:
    n = ast.AstNode('ArrayAccess')
    n.add_child(p)
    self.match('L_BRACKET')
    n.add_child(self.expression())
    self.match('R_BRACKET')
    return n

  def derefAccess (self, p: ast.AstNode) -> ast.AstNode:
    n = ast.AstNode('FieldAccess')
    n.add_child(p)
    self.match('MINUS_GREATER')
    n.add_child(self.name())
    return n

  def fieldAccess (self, p: ast.AstNode) -> ast.AstNode:
    n = ast.AstNode('FieldAccess')
    n.add_child(p)
    self.match('PERIOD')
    n.add_child(self.name())
    return n

  def ifExpression (self) -> ast.AstNode:
    n = ast.AstNode('IfExpression')
    self.match('IF')
    if self.lookahead.kind == 'L_PARENTHESIS':
      self.match('L_PARENTHESIS')
      n.add_child(self.expression())
      self.match('R_PARENTHESIS')
    else:
      n.add_child(self.expression())
      self.match('THEN')
    n.add_child(self.expression())
    self.match('ELSE')
    n.add_child(self.expression())
    return n

  def parenthesizedExpression (self) -> ast.AstNode:
    self.match('L_PARENTHESIS')
    n = self.expression()
    self.match('R_PARENTHESIS')
    firstSet = ['L_PARENTHESIS', 'L_BRACKET', 'MINUS_GREATER', 'PERIOD']
    while self.lookahead.kind in firstSet:
      p = n
      match self.lookahead.kind:
        case 'L_PARENTHESIS':
          n = self.functionCall(p)
        case 'L_BRACKET':
          n = self.arrayAccess(p)
        case 'MINUS_GREATER':
          n = self.derefAccess(p)
        case 'PERIOD':
          n = self.fieldAccess(p)
    return n

  def literal (self) -> ast.AstNode:
    match self.lookahead.kind:
      case 'NULL':
        n = ast.AstNode('NullLiteral')
        n.set_token(self.lookahead)
        self.match('NULL')
      case 'FALSE':
        n = ast.AstNode('BooleanLiteral')
        n.set_token(self.lookahead)
        self.match('FALSE')
      case 'TRUE':
        n = ast.AstNode('BooleanLiteral')
        n.set_token(self.lookahead)
        self.match('TRUE')
      case 'FLOAT32_LITERAL':
        n = ast.AstNode('FloatingPointLiteral')
        n.set_token(self.lookahead)
        self.match('FLOAT32_LITERAL')
      case 'FLOAT64_LITERAL':
        n = ast.AstNode('FloatingPointLiteral')
        n.set_token(self.lookahead)
        self.match('FLOAT64_LITERAL')
      case 'INT32_LITERAL':
        n = ast.AstNode('IntegerLiteral')
        n.set_token(self.lookahead)
        self.match('INT32_LITERAL')
      case 'INT64_LITERAL':
        n = ast.AstNode('IntegerLiteral')
        n.set_token(self.lookahead)
        self.match('INT64_LITERAL')
      case 'UINT32_LITERAL':
        n = ast.AstNode('IntegerLiteral')
        n.set_token(self.lookahead)
        self.match('UINT32_LITERAL')
      case 'UINT64_LITERAL':
        n = ast.AstNode('IntegerLiteral')
        n.set_token(self.lookahead)
        self.match('UINT64_LITERAL')
      case 'STRING_LITERAL':
        n = ast.AstNode('StringLiteral')
        n.set_token(self.lookahead)
        self.match('STRING_LITERAL')
      case _:
        print("ERROR NO LITERAL MATCH")
    return n

  # TYPES

  def type (self) -> ast.AstNode:
    combined: deque[ast.AstNode] = self.directType()
    # Pop base type node
    n = combined.popleft()
    # Pop each type node from deque, constructing chain of pointers
    # and arrays as we go. When done, the deque should be empty.    
    while len(combined) > 0:
      p = combined.pop()
      match p.kind:
        case 'PointerType':
          p.add_child(n)
          n = p
        case 'ArrayType':
          p.add_child(n)
          n = p
    return n

  # For primitives, we could just say primitive type and let later
  # pass figure out actual type from token.

  def directType (self) -> deque:
    # Build left fragment
    left = deque()
    while self.lookahead.kind == 'ASTERISK':
      n = self.pointerType()
      left.appendleft(n)
    # Build center fragment
    center = deque()
    match self.lookahead.kind:
      case 'FN':
        n = self.functionType()
        center.append(n)
      # To do: void might not be a primitive type - verify
      case kind if kind in [
        'NULL_T',
        'BOOL',
        'INT8',
        'INT16',
        'INT32',
        'INT64',
        'UINT8',
        'UINT16',
        'UINT32',
        'UINT64',
        'FLOAT32',
        'FLOAT64',
        'VOID'
      ]:
        n = self.primitiveType()
        center.append(n)
      case 'IDENTIFIER':
        # Nominal type. Need to look up name in symbol table to tell
        # what kind it is (e.g. struct, class). For now assume class.
        # What if we don't want to require a symbol table for
        # parsing? In this case, all we can say is that it is a
        # 'nominal' type.
        n = self.nominalType()
        center.append(n)
      case 'L_PARENTHESIS':
        self.match('L_PARENTHESIS')
        n = self.directType()
        center = n
        self.match('R_PARENTHESIS')
    # Build right fragment
    right = deque()
    while self.lookahead.kind == 'L_BRACKET':
      n = self.arrayType()
      right.append(n)
    # Assemble fragments
    combined = center + right + left
    return combined

  def arrayType (self) -> ast.AstNode:
    n = ast.AstNode('ArrayType')
    # We might want to set the token as '[' so that we can at least
    # get position, line number, column, etc.
    self.match('L_BRACKET')
    # Todo: The value provided inside the brackets must be a constant
    # integer expression that can be evaluated at compile time.
    # Evaluation can occur during semantic analysis phase. For now,
    # just accept a literal.
    n.add_child(self.expressionRoot())
    self.match('R_BRACKET')
    return n

  # def classType (self) -> ast.AstNode:
  #   n = ast.AstNode('ClassType')
  #   if self.lookahead.kind == 'IDENTIFIER':
  #     n.add_child(self.name())
  #   else:
  #     self.error('ID')
  #   # Need to eventually allow for type parameters. (This would
  #   # allow us to know that this was a class type, if that matters.)
  #   # Need to eventually allow for type parameters. (This would allow
  #   # us to know that this was a class type, if that matters.)
  #   return n

  def functionType (self) -> ast.AstNode:
    # Fix parameters
    self.match('FN')
    n = ast.AstNode('FunctionType')
    self.match('L_PARENTHESIS')
    if self.lookahead.kind != 'R_PARENTHESIS':
      # Parameter types
      p = self.type()
      n.add_child(p)
      while self.lookahead.kind == 'COMMA':
        self.match('COMMA')
        p = self.type()
        n.add_child(p)
    self.match('R_PARENTHESIS')
    # Return type
    self.match('ARROW')
    p = self.type()
    n.add_child(p)
    return n

  def nominalType (self) -> ast.AstNode:
    n = ast.AstNode('NominalType')
    # I don't think we want to add a name here, we want to set the
    # token instead, but we can revisit this later.
    # n.add_child(self.name())
    n.set_token(self.lookahead)
    self.match('IDENTIFIER')
    # Need to eventually allow for type parameters. (This would allow
    # us to know that this was a class type, if that matters.)
    return n

  def pointerType (self) -> ast.AstNode:
    n = ast.AstNode('PointerType')
    n.set_token(self.lookahead)
    self.match('ASTERISK')
    return n

  def primitiveType (self) -> ast.AstNode:
    n = ast.AstNode('PrimitiveType')
    n.set_token(self.lookahead)
    self.match(self.lookahead.kind)
    return n
