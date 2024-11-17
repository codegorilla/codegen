from enum import Enum
from typing import List
from collections import deque

from co import ast
from co import reader
from co import st

class Parser:

  def __init__ (self):
    self.primitiveList = ['VOID', 'BOOL', 'CHAR', 'SHORT', 'INT', 'LONG', 'FLOAT','DOUBLE']

  def setInput(self, input: reader.Lexer):
    self.input: reader.Lexer = input
    self.lookahead: reader.Token = self.input.getToken()

  def match (self, kind: str):
    if self.lookahead.kind == kind:
      self.consume()
    else:
      msg = f"Invalid token. Expected {kind}, got {self.lookahead.kind}."
      raise Exception(msg)

  def consume (self):
    self.lookahead = self.input.getToken()

  def translationUnit (self) -> ast.AstNode:
    n = ast.AstNode('TranslationUnit')
    while self.lookahead.kind != 'EOF':
      match self.lookahead.kind:
        case 'CLASS':
          n.add_child(self.classDeclaration())
        case 'DEF':
          n.add_child(self.functionDeclaration())
        case 'STRUCT':
          n.add_child(self.structureDeclaration())
        case 'UNION':
          n.add_child(self.unionDeclaration())
        case 'VAL':
          n.add_child(self.constantDeclaration())
        case 'VAR':
          n.add_child(self.variableDeclaration())
        case _:
          print("error: invalid declaration")
    return n

  # DECLARATIONS

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
    n = ast.AstNode('ConstantDeclaration')
    self.match('VAL')
    if self.lookahead.kind == 'IDENTIFIER':
      n.add_child(self.name())
    else:
      self.error('IDENTIFIER')
    # Optional type specifier
    if self.lookahead.kind == 'COLON':
      self.match('COLON')
      n.add_child(self.type())
    else:
      # Insert a "delta" (don't know) type
      n.add_child(ast.AstNode('DeltaType'))
    # Required initializer
    if self.lookahead.kind == 'EQUAL':
      self.match('EQUAL')
      # Todo: Are there restrictions on what this expression can be?
      # Does it have to be a compile-time constant? (In C it does,
      # but in C++ it doesn't.)
      n.add_child(self.expression())
    else:
      print("Error - missing initializer in constant definition")
    self.match('SEMICOLON')
    return n
  
  def variableDeclaration (self) -> ast.AstNode:
    n = ast.AstNode('VariableDeclaration')
    self.match('VAR')
    if self.lookahead.kind == 'IDENTIFIER':
      n.add_child(self.name())
    else:
      self.error('IDENTIFIER')
    # Optional type specifier
    if self.lookahead.kind == 'COLON':
      self.match('COLON')
      n.add_child(self.type())
    else:
      # Insert a "delta" (don't know) type
      n.add_child(ast.AstNode('DeltaType'))
    # Optional initializer
    if self.lookahead.kind == 'EQUAL':
      self.match('EQUAL')
      n.add_child(self.expression())
    self.match('SEMICOLON')
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
      n.add_child(self.blockElement())
    self.match('R_BRACE')
    return n

  def block (self) -> ast.AstNode:
    n = ast.AstNode('Block')
    self.match('L_BRACE')
    while self.lookahead.kind != 'R_BRACE':
      n.add_child(self.blockElement())
    self.match('R_BRACE')
    return n

  def blockElement (self) -> ast.AstNode:
    n: ast.AstNode = None
    if self.lookahead.kind in ['VAL', 'VAR']:
      n = self.declaration()
    else:
      n = self.statement()
    return n

  def declaration (self) -> ast.AstNode:
    n: ast.AstNode = None
    match self.lookahead.kind:
      case 'VAL':
        n = self.constantDeclaration()
      case 'VAR':
        n = self.variableDeclaration()
      case _:
        print("ERROR - INVALID DECLARATION")
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
      'INT',
      'INT32',
      'FLOATING'
    ]
    declarationFirstSet = [
      'VAL',
      'VAR'
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
      case item if item in declarationFirstSet:
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
    if self.lookahead == 'VAL':
      n.add_child(self.constantDeclaration())
    elif self.lookahead == 'VAR':
      n.add_child(self.variableDeclaration())

  def expressionStatement (self) -> ast.AstNode:
    n = ast.AstNode('ExpressionStatement')
    n.add_child(self.expression())
    self.match('SEMICOLON')
    return n

  def forStatement (self) -> ast.AstNode:
    n = ast.AstNode('ForStatement')
    self.match('FOR')
    self.match('L_PARENTHESIS')
    n.add_child(self.name())
    self.match('IN')
    n.add_child(self.expression())
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
    n.add_child(self.expression())
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
      n.add_child(self.expression())
      self.match('SEMICOLON')
      # Cond expression
      n.add_child(self.expression())
      self.match('SEMICOLON')
      # Loop expression
      n.add_child(self.expression())
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
    n.add_child(self.expression())
    self.match('SEMICOLON')
    return n

  def whileStatement (self) -> ast.AstNode:
    n = ast.AstNode('WhileStatement')
    self.match('WHILE')
    self.match('L_PARENTHESIS')
    n.add_child(self.expression())
    self.match('R_PARENTHESIS')
    if self.lookahead.kind == 'L_BRACE':
      n.add_child(self.block())
    else:
      n.add_child(self.blockElement())
    return n
  
  # EXPRESSIONS

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
    firstSet = ['ASTERISK', 'MINUS', 'EXCLAMATION']
    if self.lookahead.kind in firstSet:
      n = ast.AstNode('UnaryExpression')
      n.set_token(self.lookahead)
      self.match(self.lookahead.kind)
      n.add_child(self.unaryExpression())
    else:
      n = self.primaryExpression()
    return n

  def primaryExpression (self) -> ast.AstNode:
    # Todo: Do we need to distinguish between different integer literal types?
    firstSet = [
      'NULL',
      'THIS',
      'FALSE',
      'TRUE',
      'FLOAT',
      'FLOAT32',
      'FLOAT64',
      'INT',
      'INT32',
      'INT64',
      'STRING_LITERAL'
    ]
    match self.lookahead.kind:
      case 'IDENTIFIER':
        n = self.nameExpression()
      case 'IF':
        n = self.ifExpression()
      case 'L_PARENTHESIS':
        n = self.parenthesizedExpression()
      # Should be integer literals to dis-ambiguate from type names
      case item if item in firstSet:
        n = self.literal()
      case _:
        print("ERROR - INVALID PRIMARY EXPRESSION")
    return n

  def nameExpression (self) -> ast.AstNode:
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
      case 'INT32':
        n = ast.AstNode('IntegerLiteral')
        n.set_token(self.lookahead)
        self.match('INT32')
      case 'FLOAT':
        n = ast.AstNode('FloatLiteral')
        n.set_token(self.lookahead)
        self.match('FLOAT')
      case 'FLOAT32':
        n = ast.AstNode('Float32Literal')
        n.set_token(self.lookahead)
        self.match('FLOAT32')
      case 'FLOAT64':
        n = ast.AstNode('Float64Literal')
        n.set_token(self.lookahead)
        self.match('FLOAT64')
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
      case 'VOID' | 'BOOL' | 'CHAR' | 'INT' | 'INT32' | 'FLOAT' | 'DOUBLE':
        # Primitive type, need to generalize eventually
        n = self.primitiveType()
        center.append(n)
      case 'IDENTIFIER':
        # Nominal type. Need to look up name in symbol table to tell
        # what kind it is (e.g. struct, class). For now assume class.
        n = self.classType()
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
    self.match('L_BRACKET')
    n = ast.AstNode('ArrayType')
    # Todo: The value provided inside the brackets must be a constant
    # integer expression that can be evaluated at compile time.
    # Evaluation can occur during semantic analysis phase. For now,
    # just accept a literal.
    n.add_child(self.literal())
    self.match('R_BRACKET')
    return n

  def classType (self) -> ast.AstNode:
    n = ast.AstNode('ClassType')
    if self.lookahead.kind == 'IDENTIFIER':
      n.add_child(self.name())
    else:
      self.error('ID')
    # Need to eventually allow for type parameters
    return n

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

  def pointerType (self) -> ast.AstNode:
    n = ast.AstNode('PointerType')
    n.set_token(self.lookahead)
    self.match('ASTERISK')
    return n

  def primitiveType (self) -> ast.AstNode:
    match self.lookahead.kind:
      case 'VOID':
        n = self.voidType()
      case 'BOOL':
        n = self.boolType()
      case 'CHAR':
        n = self.charType()
      case 'INT':
        n = self.intType()
      case 'INT32':
        n = self.int32Type()
      case 'FLOAT':
        n = self.floatType()
      case 'DOUBLE':
        n = self.doubleType()
    return n

  def voidType (self) -> ast.AstNode:
    n = ast.AstNode('VoidType')
    n.set_token(self.lookahead)
    self.match('VOID')
    return n

  def boolType (self) -> ast.AstNode:
    n = ast.AstNode('BoolType')
    n.set_token(self.lookahead)
    self.match('BOOL')
    return n

  def charType (self) -> ast.AstNode:
    n = ast.AstNode('CharType')
    n.set_token(self.lookahead)
    self.match('CHAR')
    return n

  def intType (self) -> ast.AstNode:
    n = ast.AstNode('IntType')
    n.set_token(self.lookahead)
    self.match('INT')
    return n

  def int32Type (self) -> ast.AstNode:
    n = ast.AstNode('Int32Type')
    n.set_token(self.lookahead)
    self.match('INT32')
    return n

  def floatType (self) -> ast.AstNode:
    n = ast.AstNode('FloatType')
    n.set_token(self.lookahead)
    self.match('FLOAT')
    return n

  def doubleType (self) -> ast.AstNode:
    n = ast.AstNode('DoubleType')
    n.set_token(self.lookahead)
    self.match('DOUBLE')
    return n
