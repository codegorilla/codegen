from enum import Enum
from typing import List
from collections import deque

from co import ast
from co import types
# from co import st
from co.st import Scope, ConstantSymbol, VariableSymbol, FunctionSymbol

# Purpose:

# Compute type expressions for objects (e.g. constants and variables)
# Compute type expressions for expressions
# Possibly enforce types, but that might be a third pass

# Notes:
#
# 1. In C, global variables must be constants and must be declared
# before use. In C++, they don't need to be constants, but still need
# to be declared before use.
#
# 2. We might be able to create a dependency graph and move global
# variables to a place before they are used. However, this is not
# foolproof and circular dependencies cannot be handled anyways.
# Moreover, this would be a pretty low priority.
#
# 3. Can we just recurse through looking for type nodes and
# expression nodes, or do we need to descend methodically?

# Deprecate, or maybe fill these in upon startup for optimization
BOOL_TYPE   = types.TypeNode('bool')
INT_TYPE    = types.TypeNode('int')
LONG_TYPE   = types.TypeNode('long')
FLOAT_TYPE  = types.TypeNode('float')
FLOAT32_TYPE  = types.TypeNode('float32')
FLOAT64_TYPE  = types.TypeNode('float64')
DOUBLE_TYPE = types.TypeNode('double')

class Pass2:

  def __init__ (self, scope: Scope):
    # Might not need to pass in symbol table if it is attached as
    # attribute to AST. That is probably the right way to handle it
    # because there are pointers only going in one direction.
    # However, since declarations only occur at top level, it is ok
    # to pass it in for now, and build upon it during pass 2.
    self.current_scope = scope

  def result_type (self, t1: types.TypeNode, t2: types.TypeNode) -> types.TypeNode:
    pass

  def arith_op (self, t1: types.TypeNode, t2: types.TypeNode) -> types.TypeNode:
    pass

  # Used for type checking - might move to another pass
  def compare_types (self, t1: types.TypeNode, t2: types.TypeNode) -> bool:
    # Need to walk the tree and compare types
    if t1.kind != t2.kind:
      return False
    if t1.child_count() != t2.child_count():
      return False
    for i in range(t1.child_count()):
      if self.compare_types(t1.child(i), t2.child(i)) == False:
        return False
    return True

  def translationUnit (self, node: ast.AstNode):
    node.set_attribute('scope', self.current_scope)
    # Do translation units only contain declarations at the top level?
    for declarationNode in node.children:
      self.declaration(declarationNode)

  def declaration (self, node: ast.AstNode):
    match node.kind:
      case 'ClassDeclaration':
        pass
      case 'FunctionDeclaration':
        self.functionDeclaration(node)
        pass
      case 'StructureDeclaration':
        pass
      case 'UnionDeclaration':
        pass
      case 'ConstantDeclaration':
        self.constantDeclaration(node)
      case 'VariableDeclaration':
        self.variableDeclaration(node)
      case _:
        print("error: invalid declaration")

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

  def constantDeclaration (self, node: ast.AstNode):
    nameNode = node.child(0)
    # Add symbol to symbol table
    val_symbol = ConstantSymbol(nameNode.token.lexeme)
    self.current_scope.define(val_symbol)
    typeNode = node.child(1)
    # Might be a good idea to have a root type node so we don't have
    # to check for so many different types here. Or we can just test
    # for a delta type.
    kindSet = ['IntType', 'FloatType', 'ArrayType', 'PointerType']
    if typeNode.kind in kindSet:
      self.type(typeNode)
      val_symbol.set_type(typeNode.attribute('type'))
    # Initializers are not optional for constants
    initNode = node.child(2)
    self.expression(initNode)

  def variableDeclaration (self, node: ast.AstNode):
    name_node = node.child(0)
    # To do: We need to determine if a symbol already exists in the
    # current scope. If so, this is a duplicate and results in an
    # error.
    var_symbol = VariableSymbol(name_node.token.lexeme)
    self.current_scope.define(var_symbol)
    type_node = node.child(1)
    # Might be a good idea to have a root type node so we don't have
    # to check for so many different types here. Or we can just test
    # for a delta type.
    kind_set = ['IntType', 'FloatType', 'ArrayType', 'PointerType']
    if type_node.kind in kind_set:
      self.type(type_node)
      var_symbol.set_type(type_node.attribute('type'))
      # Initializer is optional because type was specified
      if node.child_count() == 3:
        init_node = node.child(2)
        self.expression(init_node)
    else:
      # Initializer is required because type was not specified
      init_node = node.child(2)
      self.expression(init_node)

  # Might need to add functions to symbol table in pass 1 to allow
  # forward references
  def functionDeclaration (self, node: ast.AstNode):
    name_node = node.child(0)
    fun_symbol = FunctionSymbol(name_node.token.lexeme)
    self.current_scope.define(fun_symbol)
    # Push new scope
    scope = Scope()
    scope.set_enclosing_scope(self.current_scope)
    self.current_scope = scope
    node.set_attribute('scope', self.current_scope)
    self.parameterList(node.child(1))
    # Do we need to process return type now? It might be needed if we
    # Need to compute the type of the function.
    self.functionBody(node.child(3))
    # Pop scope
    self.current_scope = self.current_scope.enclosing_scope

  def parameterList (self, node: ast.AstNode):
    for child_node in node.children:
      self.parameter(child_node)

  def parameter (self, node: ast.AstNode):
    name_node = node.child(0)
    # We need to check if this parameter is a duplicate and print an
    # error message if it is.
    param_symbol = VariableSymbol(name_node.token.lexeme)
    self.current_scope.define(param_symbol)
    type_node = node.child(1)
    # We probably don't need to check if the type is in these
    # specific kinds. We should just be able to descend into type
    kind_set = ['IntType', 'FloatType', 'ArrayType', 'PointerType']
    if type_node.kind in kind_set:
      self.type(type_node)
      param_symbol.set_type(type_node.attribute('type'))

  def functionBody (self, node: ast.AstNode):
    self.topBlock(node.child())

  # A top block is identical to a block, except that it doesn't
  # create a new scope. It simply uses the scope created by its
  # function.

  def topBlock (self, node: ast.AstNode):
    for child_node in node.children:
      match child_node.kind:
        case 'ConstantDeclaration':
          self.constantDeclaration(child_node)
        case 'VariableDeclaration':
          self.variableDeclaration(child_node)
        case _:
          print(child_node.kind)

  def block (self, node: ast.AstNode):
    # Push new scope
    scope = Scope()
    scope.set_enclosing_scope(self.current_scope)
    self.current_scope = scope
    node.set_attribute('scope', self.current_scope)
    for child_node in node.children:
      match child_node.kind:
        case 'ConstantDeclaration':
          self.constantDeclaration(child_node)
        case 'VariableDeclaration':
          self.variableDeclaration(child_node)
        case _:
          print(child_node.kind)
    # Pop scope
    self.current_scope = self.current_scope.enclosing_scope

  # EXPRESSIONS

  def expression (self, node: ast.AstNode):
    # Need to put a match here to compute expression node types
    match node.kind:
      case 'UnaryExpression':
        self.unaryExpression(node)
      case 'BinaryExpression':
        self.binaryExpression(node)
      case 'IntegerLiteral':
        node.set_attribute('type', INT_TYPE)
      case 'FloatLiteral':
        node.set_attribute('type', FLOAT32_TYPE)
      case 'Float32Literal':
        node.set_attribute('type', FLOAT32_TYPE)
      case 'Float64Literal':
        node.set_attribute('type', FLOAT64_TYPE)
      case 'Name':
        self.name(node)
      case _:
        print("error: did not match node kind on pass 2")
        print(node.kind)

  def unaryExpression (self, node: ast.AstNode):
    operator = node.token.kind
    exprNode = node.child()
    self.expression(exprNode)
    if operator == 'ASTERISK':
      # The type should be the referenced type (i.e. bare type with
      # pointer node stripped from it.)
      t: types.TypeNode = exprNode.attribute('type')
      node.set_attribute('type', t.child())
    elif operator == 'MINUS':
      t = exprNode.attribute('type')
      node.set_attribute('type', t)
    elif operator == 'EXCLAMATION':
      node.set_attribute('type', BOOL_TYPE)

  def binaryExpression (self, node: ast.AstNode):
    operator = node.token.kind
    leftNode = node.child(0)
    rightNode = node.child(1)
    self.expression(leftNode)
    self.expression(rightNode)
    arithmeticOperatorSet = ['PLUS', 'MINUS', 'ASTERISK', 'SLASH']
    relationalOperatorSet = ['GREATER', 'LESS', 'GREATER_EQUAL', 'LESS_EQUAL']
    equalityOperatorSet   = ['EQUAL_EQUAL', 'EXCLAMATION_EQUAL']
    if operator in arithmeticOperatorSet:
      # Assuming left and right have the same type, we arbitrarily
      # set the type to the same type as the left node. This might
      # change in the future once we incorporate type promotion.
      t = leftNode.attribute('type')
      node.set_attribute('type', t)
    elif operator in relationalOperatorSet:
      node.set_attribute('type', BOOL_TYPE)
    elif operator in equalityOperatorSet:
      node.set_attribute('type', BOOL_TYPE)

  def name (self, node: ast.AstNode):
    # Look up name in symbol table
    name = node.token.lexeme
    s = self.current_scope.lookup(name)
    if s == None:
      print(f"error: name {name} not declared.")
    elif s.type == None:
      print(f"error: name {name} has unknown type.")
    else:
      node.set_attribute('type', s.type)

  # TYPES

  def type (self, node: ast.AstNode):
    match node.kind:
      case 'FloatType':
        self.floatType(node)
      case 'IntType':
        self.intType(node)
      case 'ArrayType':
        self.arrayType(node)
      case 'PointerType':
        self.pointerType(node)
      case _:
        print("No matching type")

  def arrayType (self, node: ast.AstNode):
    # The size might not matter as far as the type goes.
    # We would still need to check the size to make sure it is a
    # compile-time integral constant, however.
    # sizeNode = node.get_child(0)
    refNode = node.child(1)
    self.type(refNode)
    t = types.TypeNode('array')
    t.add_child(refNode.attribute('type'))
    node.set_attribute('type', t)

  def pointerType (self, node: ast.AstNode):
    refNode = node.child()
    self.type(refNode)
    t = types.TypeNode('pointer')
    t.add_child(refNode.attribute('type'))
    node.set_attribute('type', t)

  def intType (self, node: ast.AstNode):
    # Maybe we can just look this up in global or built-in scope since
    # We don't allow local type declarations
    # Need to use resolve, not lookup
    # Or have a way to shunt to built-in types
    symbol = self.current_scope.resolve('int')
    node.set_attribute('type', symbol.type)

  def floatType (self, node: ast.AstNode):
    symbol = self.current_scope.resolve('float')
    node.set_attribute('type', symbol.type)
