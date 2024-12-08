from enum import Enum
from typing import List
from collections import deque

# from co import ast
# from co import types

from co.ast import AstNode
from co.types import TypeNode, ArrayTypeNode, PointerTypeNode
from co.st import Scope, FunctionSymbol, VariableSymbol, TypeSymbol
from co.st import ClassSymbol, PrimitiveSymbol, StructureSymbol, UnionSymbol


# Purpose:

# Determine if expressions are compile-time constants

# Literal values or constants


# Notes:
#
# Note sure if we need to pass in scope information. Actually, we do
# because we need to know if it is a constant or not.
#
# Does each kind of thing get its own symbol type? If not, then
# object symbols can be marked as constant or not.

class Pass3:

  def __init__ (self, root_node: AstNode, builtin_scope: Scope):
    self.root_node = root_node
    self.builtin_scope: Scope = builtin_scope
    self.current_scope: Scope = builtin_scope

  def result_type (self, t1: TypeNode, t2: TypeNode) -> TypeNode:
    pass

  def arith_op (self, t1: TypeNode, t2: TypeNode) -> TypeNode:
    pass

  # Used for type checking - might move to another pass
  def compare_types (self, t1: TypeNode, t2: TypeNode) -> bool:
    # Need to walk the tree and compare types
    if t1.kind != t2.kind:
      return False
    if t1.child_count() != t2.child_count():
      return False
    for i in range(t1.child_count()):
      if self.compare_types(t1.child(i), t2.child(i)) == False:
        return False
    return True

  def resultType (self, op: str, t1: TypeNode, t2: TypeNode) -> TypeNode:
    pass

  def process (self):
    # Search for expression roots
    self.search(self.root_node)
    # self.traverse(self.root_node)

  # BEGIN

  # Once we find expression root, we can methodically descend from
  # there.

  def search (self, node: AstNode):
    if node.kind == 'ExpressionRoot':
      self.expressionRoot(node)
    else:
      for child_node in node.children:
        self.search(child_node)

  def expressionRoot (self, node: AstNode):
    expr_node = node.child()
    self.expression(expr_node)
    result = expr_node.attribute('is_constant')
    node.set_attribute('is_constant', result)

  def expression (self, node: AstNode):
    # Dispatch method
    match node.kind:
      case 'BinaryExpression':
        self.binaryExpression(node)
      case 'UnaryExpression':
        self.unaryExpression(node)
      case 'Name':
        self.name(node)
      case kind if kind in [
        'BooleanLiteral',
        'FloatingPointLiteral',
        'IntegerLiteral'
      ]:
        self.literal(node)

  def binaryExpression (self, node: AstNode):
    left_node  = node.child(0)
    right_node = node.child(1)
    self.expression(left_node)
    self.expression(right_node)
    result = left_node.attribute('is_constant') and right_node.attribute('is_constant')
    node.set_attribute('is_constant', result)

  def name (self, node: AstNode):
    scope: Scope = node.attribute('scope')
    symbol: VariableSymbol = scope.resolve(node.token.lexeme)
    result = symbol.constant_flag
    node.set_attribute('is_constant', result)

  def literal (self, node: AstNode):
    result = True
    node.set_attribute('is_constant', result)

  def unaryExpression (self, node: AstNode):
    child_node = node.child()
    self.expression(child_node)
    result = child_node.attribute('is_constant')
    node.set_attribute('is_constant', result)



  # DECLARATIONS


  def declaration (self, node: AstNode):
    match node.kind:
      case 'ClassDeclaration':
        pass
      case 'FunctionDeclaration':
        # self.functionDeclaration(node)
        pass
      case 'StructureDeclaration':
        pass
      case 'TypealiasDeclaration':
        pass
      case 'UnionDeclaration':
        pass
      case 'VariableDeclaration':
        self.variableDeclaration(node)
      case _:
        raise Exception(f"error: invalid node kind '{node.kind}' in declaration")

  def classDeclaration (self) -> AstNode:
    n = AstNode('ClassDeclaration')
    self.match('CLASS')
    n.add_child(self.name())
    self.match('L_BRACE')
    while self.lookahead.kind != 'R_BRACE':
      n.add_child(self.classMember())
    self.match('R_BRACE')
    return n

  def classMember (self) -> AstNode:
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

  # Might need to change concept of constant to mean final because it
  # conflicts with compile-time const-ness.
  # def constantDeclaration (self, node: AstNode):
  #   name_node = node.child(0)
  #   # spec_node = node.child(1)
  #   init_node = node.child(2)
  #   self.expression(init_node)
  #   # Type specifier is optional
  #   is_constant: bool = init_node.attribute('is_constant')
  #   # Update consant's symbol table entry with constness information.
  #   symbol: VariableSymbol = name_node.attribute('symbol')
  #   symbol.set_is_constant(is_constant)

  def functionDeclaration (self, node: AstNode):
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

  def parameterList (self, node: AstNode):
    for child_node in node.children:
      self.parameter(child_node)

  def parameter (self, node: AstNode):
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

  def functionBody (self, node: AstNode):
    self.topBlock(node.child())

  # A top block is identical to a block, except that it doesn't
  # create a new scope. It simply uses the scope created by its
  # function.

  def topBlock (self, node: AstNode):
    for child_node in node.children:
      match child_node.kind:
        case 'ConstantDeclaration':
          self.constantDeclaration(child_node)
        case 'VariableDeclaration':
          self.variableDeclaration(child_node)
        case _:
          print(child_node.kind)

  def block (self, node: AstNode):
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

  # Unless the variable is declared constant, we can't really do
  # anything useful if the expression is determined to be constant.
  # But for now we will make the determination anyways in case it is
  # useful in the future. For example, a global final variable is
  # essentially constant, so maybe we'd want to allow it to be
  # treated as such in the future. Also, we need to descend into
  # expressions that are part of array bounds to determine if they
  # are constant, so just going into any expression seems to be the
  # simplest way to do that for now.

  def variableDeclaration (self, node: AstNode):
    name_node = node.child(0)
    spec_node = node.child(1)
    init_node = node.child(2)
    if init_node:
      self.expression(init_node)
    is_constant: bool = init_node.attribute('is_constant')
    # Update variable's symbol table entry with const-ness information
    symbol: VariableSymbol = name_node.attribute('symbol')
    symbol.set_is_constant(is_constant)

  # EXPRESSIONS

  # def expression (self, node: AstNode):
  #   match node.kind:
  #     case 'BinaryExpression':
  #       self.binaryExpression(node)
  #     case 'UnaryExpression':
  #       self.unaryExpression(node)
  #     case 'BooleanLiteral':
  #       self.booleanLiteral(node)
  #     case 'FloatingPointLiteral':
  #       self.floatingPointLiteral(node)
  #     case 'IntegerLiteral':
  #       self.integerLiteral(node)
  #     case 'NullLiteral':
  #       self.nullLiteral(node)
  #     case 'Name':
  #       self.name(node)
  #     case _:
  #       print(f"error: did not match node kind on pass 2 {node.kind}")

  def booleanLiteral (self, node: AstNode):
    node.set_attribute('is_constant', True)

  def floatingPointLiteral (self, node: AstNode):
    node.set_attribute('is_constant', True)

  def integerLiteral (self, node: AstNode):
    node.set_attribute('is_constant', True)

  def nullLiteral (self, node: AstNode):
    node.set_attribute('is_constant', True)

  def unaryExpression (self, node: AstNode):
    # We might need some checks to make sure these operators are
    # operating on a valid operands (e.g. can you negate a string?)
    operator = node.token.kind
    child_node = node.child()
    self.expression(child_node)
    if operator == 'ASTERISK':
      # The type should be the referenced type (i.e. bare type with
      # pointer node stripped from it.)
      t: TypeNode = child_node.attribute('type')
      node.set_attribute('type', t.child())
    elif operator == 'MINUS':
      t: TypeNode = child_node.attribute('type')
      node.set_attribute('type', t)
    elif operator == 'EXCLAMATION':
      t: TypeNode = self.builtin_scope.resolve('bool')
      node.set_attribute('type', t)

  def result_type (self, t1: TypeNode, t2: TypeNode, mode: str):
    type_map = {
         'int8': 0,
        'int16': 1,
        'int32': 2,
        'int64': 3,
        'uint8': 4,
       'uint16': 5,
       'uint32': 6,
       'uint64': 7,
      'float32': 8,
      'float64': 9
    }
    I8  = 'int8'
    I16 = 'int16'
    I32 = 'int32'
    I64 = 'int64'
    U8  = 'uint8'
    U16 = 'uint16'
    U32 = 'uint32'
    U64 = 'uint64'
    F32 = 'float32'
    F64 = 'float64'
    if mode == 'arithmetic':
      type_table = [
        #   I8,  I16,  I32,  I64,   U8,  U16,  U32,  U64,  F32,  F64
        [   I8,  I16,  I32,  I64, None, None, None, None,  F32,  F64 ], # I8
        [  I16,  I16,  I32,  I64,  I16, None, None, None,  F32,  F64 ], # I16
        [  I32,  I32,  I32,  I64,  I32,  I32, None, None,  F32,  F64 ], # I32
        [  I64,  I64,  I64,  I64,  I64,  I64,  I64, None,  F32,  F64 ], # I64
        [ None,  I16,  I32,  I64,   U8,  U16,  U32,  U64,  F32,  F64 ], # U8
        [ None, None,  I32,  I64,  U16,  U16,  U32,  U64,  F32,  F64 ], # U16
        [ None, None, None,  I64,  U32,  U32,  U32,  U64,  F32,  F64 ], # U32
        [ None, None, None, None,  U64,  U64,  U64,  U64,  F32,  F64 ], # U64
        [  F32,  F32,  F32,  F32,  F32,  F32,  F32,  F32,  F32,  F64 ], # F32
        [  F64,  F64,  F64,  F64,  F64,  F64,  F64,  F64,  F64,  F64 ]  # F64
      ]
    numeric_types = list(type_map.keys())
    if t1.kind in numeric_types and t2.kind in numeric_types:
      t1_index = type_map[t1.kind]
      t2_index = type_map[t2.kind]
      symbol: PrimitiveSymbol = self.builtin_scope.resolve(type_table[t1_index][t2_index])
      return symbol.type
    else:
      return None

  def is_promoted (self, source_type: TypeNode, dest_type: TypeNode):
    type_map = {
         'int8': 0,
        'int16': 1,
        'int32': 2,
        'int64': 3,
        'uint8': 4,
       'uint16': 5,
       'uint32': 6,
       'uint64': 7,
      'float32': 8,
      'float64': 9
    }
    promotion_table = [
      #    I8,   I16,   I32,   I64,    U8,   U16,   U32,   U64,   F32,   F64
      [ False,  True,  True,  True, False, False, False, False,  True,  True  ], # I8
      [ False, False,  True,  True, False, False, False, False,  True,  True  ], # I16
      [ False, False, False,  True, False, False, False, False,  True,  True  ], # I32
      [ False, False, False, False, False, False, False, False,  True,  True  ], # I64
      [ False,  True,  True,  True, False, True,   True,  True,  True,  True  ], # U8
      [ False, False,  True,  True, False, False,  True,  True,  True,  True  ], # U16
      [ False, False, False,  True, False, False, False,  True,  True,  True  ], # U32
      [ False, False, False, False, False, False, False, False,  True,  True  ], # U64
      [ False, False, False, False, False, False, False, False, False,  True  ], # F32
      [ False, False, False, False, False, False, False, False, False, False  ]  # F64
    ]
    # Do we need to check for numeric types?
    st_index = type_map[source_type.kind]
    dt_index = type_map[dest_type.kind]
    result = promotion_table[st_index][dt_index]
    return result

  def binaryExpression (self, node: AstNode):
    operator = node.token.kind
    left_node  = node.child(0)
    right_node = node.child(1)
    self.expression(left_node)
    self.expression(right_node)
    arithmeticOperatorSet = ['PLUS', 'MINUS', 'ASTERISK', 'SLASH']
    relationalOperatorSet = ['GREATER', 'LESS', 'GREATER_EQUAL', 'LESS_EQUAL']
    equalityOperatorSet   = ['EQUAL_EQUAL', 'EXCLAMATION_EQUAL']
    if operator in (arithmeticOperatorSet + relationalOperatorSet + equalityOperatorSet):
      # Determine result type
      left_type  = left_node.attribute('type')
      right_type = right_node.attribute('type')
      if operator in arithmeticOperatorSet:
        result_type = self.result_type(left_type, right_type, 'arithmetic')
        print(result_type)
      elif operator in relationalOperatorSet:
        result_type = self.result_type(left_type, right_type, 'relational')
      elif operator in equalityOperatorSet:
        result_type = self.result_type(left_type, right_type, 'equality')
      else:
        # Can this happen?
        result_type = None
        print("Not any of the designated operators")
      if result_type == None:
        print(f"error: invalid operand types '{left_type.kind}' and '{right_type.kind}' for binary operator '{node.token.lexeme}'")
      else:
        node.set_attribute('type', result_type)
      # Determine which operand to promote
      left_promote  = self.is_promoted(left_type, result_type)
      right_promote = self.is_promoted(right_type, result_type)
      # Create type promotion node
      if left_promote:
        # Promote is similar to a cast, but not explicitly in code
        promote_node = AstNode('Promotion')
        promote_node.set_attribute('type', result_type)
        node.set_child(0, promote_node)
        promote_node.add_child(left_node)
      elif right_promote:
        promote_node = AstNode('Promotion')
        promote_node.set_attribute('type', result_type)
        node.set_child(1, promote_node)
        promote_node.add_child(right_node)

  def name (self, node: AstNode):
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

  def type (self, node: AstNode):
    match node.kind:
      case 'ArrayType':
        self.arrayType(node)
      case 'NominalType':
        self.nominalType(node)
      case 'PointerType':
        self.pointerType(node)
      case 'PrimitiveType':
        self.primitiveType(node)
      case _:
        print(f"No matching type {node.kind}")

  def arrayType (self, node: AstNode):
    # We still need to check the size to make sure it is a compile-
    # time integral constant.
    size_node = node.child(0)
    base_type_node = node.child(1)
    # This should really be a compile-time constant expression. But
    # we need to determine if it is a valid compile-time constant
    # (that is also an integer) by semantic analysis.
    size = size_node.token.lexeme
    self.type(base_type_node)
    type = ArrayTypeNode(size, base_type_node.attribute('type'))
    node.set_attribute('type', type)

  def nominalType (self, node: AstNode):
    type_name = node.token.lexeme
    symbol: TypeSymbol = self.current_scope.resolve(type_name)
    type = symbol.type
    node.set_attribute('type', type)

  def pointerType (self, node: AstNode):
    base_type_node = node.child()
    self.type(base_type_node)
    type = PointerTypeNode(base_type_node.attribute('type'))
    node.set_attribute('type', type)

  def primitiveType (self, node: AstNode):
    type_name = node.token.lexeme
    symbol: TypeSymbol = self.builtin_scope.resolve(type_name)
    type = symbol.type
    node.set_attribute('type', type)
