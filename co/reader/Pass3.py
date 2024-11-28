from enum import Enum
from typing import List
from collections import deque

# from co import ast
# from co import types

from co.ast import AstNode
from co.types import TypeNode
from co.st import Scope, ConstantSymbol, FunctionSymbol, VariableSymbol
from co.st import ClassSymbol, PrimitiveSymbol, StructureSymbol, UnionSymbol


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

class Pass3:

  def __init__ (self, builtin_scope: Scope):
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

  # BEGIN

  def translationUnit (self, node: AstNode):
    self.current_scope = node.attribute('scope')
    for decl_node in node.children:
      self.declaration(decl_node)

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
      case 'ConstantDeclaration':
        self.constantDeclaration(node)
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

  def constantDeclaration (self, node: AstNode):
    name_node = node.child(0)
    spec_node = node.child(1)
    init_node = node.child(2)
    self.expression(init_node)
    # Type specifier is optional
    if spec_node:
      self.type(spec_node)
      type = spec_node.attribute('type')
    else:
      type = init_node.attribute('type')
    # Update consant's symbol table entry with type information. If
    # type was not specified, infer it from expression's computed
    # type.
    symbol: VariableSymbol = name_node.attribute('symbol')
    symbol.set_type(type)

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

  def variableDeclaration (self, node: AstNode):
    name_node = node.child(0)
    spec_node = node.child(1)
    init_node = node.child(2)
    # Type specifier is optional
    if spec_node:
      self.type(spec_node)
      type = spec_node.attribute('type')
      # Initializer is optional when type was specified
      if init_node:
        self.expression(init_node)
    else:
      # Initializer is required when type was not specified
      self.expression(init_node)
      type = init_node.attribute('type')
    # Update variable's symbol table entry with type information. If
    # type was not specified, infer it from expression's computed
    # type.
    symbol: VariableSymbol = name_node.attribute('symbol')
    symbol.set_type(type)

  # EXPRESSIONS

  def expression (self, node: AstNode):
    match node.kind:
      case 'BinaryExpression':
        self.binaryExpression(node)
      case 'UnaryExpression':
        self.unaryExpression(node)
      case 'BooleanLiteral':
        self.booleanLiteral(node)
      case 'FloatingPointLiteral':
        self.floatingPointLiteral(node)
      case 'IntegerLiteral':
        self.integerLiteral(node)
      case 'NullLiteral':
        self.nullLiteral(node)
      case 'Name':
        self.name(node)
      case _:
        print(f"error: did not match node kind on pass 2 {node.kind}")

  def booleanLiteral (self, node: AstNode):
    symbol: PrimitiveSymbol = self.builtin_scope.resolve('bool')
    node.set_attribute('type', symbol.type)

  def floatingPointLiteral (self, node: AstNode):
    # Note: A value of type float64 can never be implicitly narrowed to type float32
    type_name_lookup = {
      'FLOAT32': 'float32',
      'FLOAT64': 'float64'
    }
    # Map literal value's token kind to its corresponding primitive type name
    type_name = type_name_lookup[node.token.kind]
    symbol: PrimitiveSymbol = self.builtin_scope.resolve(type_name)
    node.set_attribute('type', symbol.type)

  def integerLiteral (self, node: AstNode):
    # https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/numeric-conversions
    # A value of a constant expression of type int (for example, a value represented by an integer literal) can be implicitly converted to...
    # So an integer literal (without suffix) will always be an int32. However, during semantic
    # analysis, we may narrow it if the value is within the range of the destination.
    type_name_lookup = {
      'INT32_LITERAL':  'int32',
      'INT64_LITERAL':  'int64',
      'UINT32_LITERAL': 'uint32',
      'UINT64_LITERAL': 'uint64',
    }
    # Map literal value's token kind to its corresponding primitive type name
    type_name = type_name_lookup[node.token.kind]
    symbol: PrimitiveSymbol = self.builtin_scope.resolve(type_name)
    node.set_attribute('type', symbol.type)

  def nullLiteral (self, node: AstNode):
    # The null type is a special type, not really a primitive type,
    # so this can be revisited. To do: We need to make sure that even
    # though the null literal's type is the null type, it is not
    # possible to declare a variable to have the null type. It must
    # also not be possible to infer that a variable's type is the
    # null type.
    symbol: PrimitiveSymbol = self.builtin_scope.resolve('null')
    node.set_attribute('type', symbol.type)

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
      case 'PointerType':
        self.pointerType(node)
      case 'PrimitiveType':
        self.primitiveType(node)
      case _:
        print(f"No matching type {node.kind}")

  def arrayType (self, node: AstNode):
    # The size might not matter as far as the type goes.
    # We would still need to check the size to make sure it is a
    # compile-time integral constant, however.
    # sizeNode = node.get_child(0)
    ref_node = node.child()
    self.type(ref_node)
    t = TypeNode('array')
    t.add_child(ref_node.attribute('type'))
    node.set_attribute('type', t)

  def pointerType (self, node: AstNode):
    ref_node = node.child()
    self.type(ref_node)
    t = TypeNode('pointer')
    t.add_child(ref_node.attribute('type'))
    node.set_attribute('type', t)

  def primitiveType (self, node: AstNode):
    symbol = self.builtin_scope.resolve(node.token.lexeme)
    node.set_attribute('type', symbol.type)
