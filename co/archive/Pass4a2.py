from enum import Enum
from typing import List
from collections import deque

from co.ast import AstNode
from co.types import TypeNode, ArrayTypeNode, PointerTypeNode
from co.st import Scope, FunctionSymbol, VariableSymbol, TypeSymbol
from co.st import ClassSymbol, PrimitiveSymbol, StructureSymbol, UnionSymbol
from co.reader import PrimitiveType

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

B   = PrimitiveType.BOOL.value
U8  = PrimitiveType.UINT8.value
U16 = PrimitiveType.UINT16.value
U32 = PrimitiveType.UINT32.value
U64 = PrimitiveType.UINT64.value
I8  = PrimitiveType.INT8.value
I16 = PrimitiveType.INT16.value
I32 = PrimitiveType.INT32.value
I64 = PrimitiveType.INT64.value
F32 = PrimitiveType.FLOAT32.value
F64 = PrimitiveType.FLOAT64.value
X   = None

class Pass4a:

  def __init__ (self, root_node: AstNode):
    self.root_node = root_node
    self.integral_types = [
      PrimitiveType.UINT8.value,
      PrimitiveType.UINT16.value,
      PrimitiveType.UINT32.value,
      PrimitiveType.UINT64.value,
      PrimitiveType.INT8.value,
      PrimitiveType.INT16.value,
      PrimitiveType.INT32.value,
      PrimitiveType.INT64.value,
    ]
    self.numeric_types = self.integral_types + [
      PrimitiveType.FLOAT32.value,
      PrimitiveType.FLOAT64.value
    ]
    self.index_lookup = {}
    for index, item in enumerate(self.numeric_types):
      self.index_lookup[item] = index

  def process (self):
    # Search for expression roots
    self.search(self.root_node)

  # BEGIN

  def search (self, node: AstNode):
    if node.kind == 'ExpressionRoot':
      self.expressionRoot(node)
    else:
      for child_node in node.children:
        if child_node == None:
          print("FOUND NONE!")
        self.search(child_node)

  def expressionRoot (self, node: AstNode):
    print("Expr root!")
    expr_node = node.child()
    self.expression(expr_node)
    # result = expr_node.attribute('is_constant')
    # node.set_attribute('is_constant', result)

  # EXPRESSIONS

  def expression (self, node: AstNode):
    # Dispatch method
    match node.kind:
      case 'BinaryExpression':
        self.binaryExpression(node)
      case 'UnaryExpression':
        self.unaryExpression(node)
      case 'Name':
        self.name(node)
      case 'BooleanLiteral':
        self.booleanLiteral(node)
      case 'FloatingPointLiteral':
        self.floatingPointLiteral(node)
      case 'IntegerLiteral':
        self.integerLiteral(node)
      case 'NullLiteral':
        self.nullLiteral(node)

  def binaryExpression (self, node: AstNode):
    # Dispatch method
    operator = node.token.kind
    if operator in ['PLUS', 'MINUS', 'ASTERISK', 'SLASH']:
      # Operands must be of numeric type
      # Note: C++ calls these arithmetic types, but that includes
      # booleans, which we don't consider to be numeric.
      self.arithmeticExpression(node)
    elif operator in ['GREATER', 'LESS', 'GREATER_EQUAL', 'LESS_EQUAL']:
      # Same as arithmetic, but result is boolean
      self.relationalExpression(node)
    elif operator in ['EQUAL_EQUAL', 'EXCLAMATION_EQUAL']:
      # Same as arithmetic, but result is boolean? How is this
      # different from relational?
      self.equalityExpression(node)
    elif operator in ['BAR', 'CARET', 'AMPERSAND']:
      # Same as arithmetic, but must be integral
      # Should this include shifting?
      self.bitwiseExpression(node)

  # Given two numeric types, are they compatible?
  # Given two compatible numeric types, which one is the widest?
  # Given two numeric types, which one needs to be converted?

  def arithmeticExpression (self, node: AstNode):
    left_node  = node.child(0)
    right_node = node.child(1)
    self.expression(left_node)
    self.expression(right_node)
    left_type  = left_node.attribute('type')
    right_type = right_node.attribute('type')
    print(f"{left_type} + {right_type}")
    # Only process numeric types. If not numeric then this is either
    # an illegal operation, or operator overloading is being used. It
    # is also possible that this is pointer arithmetic.
    # For now, just make sure the types are numeric.
    if left_type in self.numeric_types and right_type in self.numeric_types:
      # This table answers: Given two types, are they compatible?
      F = False
      T = True
      compat_table = [
        #  U8, U16, U32, U64,  I8, I16, I32, I64, F32, F64
        [   T,   T,   T,   T,   F,   T,   T,   T,   T,   T ], # U8
        [   T,   T,   T,   T,   F,   F,   T,   T,   T,   T ], # U16
        [   T,   T,   T,   T,   F,   F,   F,   T,   T,   T ], # U32
        [   T,   T,   T,   T,   F,   F,   F,   F,   T,   T ], # U64
        [   F,   F,   F,   F,   T,   T,   T,   T,   T,   T ], # I8
        [   T,   F,   F,   F,   T,   T,   T,   T,   T,   T ], # I16
        [   T,   T,   F,   F,   T,   T,   T,   T,   T,   T ], # I32
        [   T,   T,   T,   F,   T,   T,   T,   T,   T,   T ], # I64
        [   T,   T,   T,   T,   T,   T,   T,   T,   T,   T ], # F32
        [   T,   T,   T,   T,   T,   T,   T,   T,   T,   T ]  # F64
      ]
      # Map operand types to indices in compatibility type table. Row
      # is left index, column is right index.
      left_index  = self.index_lookup[left_type]
      right_index = self.index_lookup[right_type]
      is_compat = compat_table[left_index][right_index]
      if is_compat:
        if right_index < left_index:
          self.widenRightExpression(node)
        elif left_index < right_index:
          self.widenLeftExpression(node)
        operator = node.token.kind
        if operator in ['PLUS', 'MINUS', 'ASTERISK', 'SLASH']:
          # For arithmetic operations, the result type is the same as
          # the operand types. Due to the widening coercion, both
          # operand types are guaranteed to be the same, and we can
          # choose either one arbitrarily.
          result_type = left_type
          node.set_attribute('type', result_type)
        elif operator in ['GREATER', 'LESS', 'GREATER_EQUAL', 'LESS_EQUAL']:
          # For relational operations, the result type is boolean.
          result_type = PrimitiveType.BOOL.value
          node.set_attribute('type', result_type)
      else:
        # Types are numeric, but not compatible. Manual cast is
        # required. This is an error condition.
        is_compat = False
    else:
      # Types are not numeric. This is usually an error condition,
      # but might be operator overloading or pointer arithmetic is
      # being used.
      pass
    print(is_compat)

  def relationalExpression (self, node: AstNode):
    # This should be the same as arithmetic expression, but the
    # result type is bool instead of the operand type.
    self.arithmeticExpression(node)

  def equalityExpression (self, node: AstNode):
    pass

  def bitwiseExpression (self, node: AstNode):
    left_node  = node.child(0)
    right_node = node.child(1)
    self.expression(left_node)
    self.expression(right_node)
    left_type  = left_node.attribute('type')
    right_type = right_node.attribute('type')
    print(f"{left_type} + {right_type}")
    # Only process integral types
    if left_type in self.integral_types and right_type in self.integral_types:
      # This table answers: Given two types, are they compatible?
      F = False
      T = True
      compat_table = [
        #  U8, U16, U32, U64,  I8, I16, I32, I64
        [   T,   T,   T,   T,   F,   T,   T,   T ], # U8
        [   T,   T,   T,   T,   F,   F,   T,   T ], # U16
        [   T,   T,   T,   T,   F,   F,   F,   T ], # U32
        [   T,   T,   T,   T,   F,   F,   F,   F ], # U64
        [   F,   F,   F,   F,   T,   T,   T,   T ], # I8
        [   T,   F,   F,   F,   T,   T,   T,   T ], # I16
        [   T,   T,   F,   F,   T,   T,   T,   T ], # I32
        [   T,   T,   T,   F,   T,   T,   T,   T ]  # I64
      ]
      # Map operand types to indices in compatibility type table. Row
      # is left index, column is right index.
      left_index  = self.index_lookup[left_type]
      right_index = self.index_lookup[right_type]
      is_compat = compat_table[left_index][right_index]
      if is_compat:
        if right_index < left_index:
          self.widenRightExpression(node)
        elif left_index < right_index:
          self.widenLeftExpression(node)
        # For bitwise operations, the result type is the same as
        # the operand types. Due to the widening coercion, both
        # operand types are guaranteed to be the same, and we can
        # choose either one arbitrarily.
        result_type = left_type
        node.set_attribute('type', result_type)
      else:
        # Types are integral, but not compatible. Manual cast is
        # required. This is an error condition.
        is_compat = False
    else:
      # Types are not integral. This is usually an error condition,
      # but might be operator overloading or pointer arithmetic is
      # being used.
      pass

  def widenRightExpression (self, node: AstNode):
    print("Widen right")
    # Widen right operand type to match left operand type
    right_node = node.child(0)
    left_node  = node.child(1)
    cast_node = AstNode('WidenCast')
    cast_node.add_child(right_node)
    cast_node.set_attribute('type', left_node.attribute('type'))
    node.set_child(1, cast_node)

  def widenLeftExpression (self, node: AstNode):
    print("Widen left")
    # Widen left operand type to match right operand type
    right_node = node.child(0)
    left_node  = node.child(1)
    cast_node = AstNode('WidenCast')
    cast_node.add_child(left_node)
    cast_node.set_attribute('type', right_node.attribute('type'))
    node.set_child(0, cast_node)

  def booleanLiteral (self, node: AstNode):
    type = PrimitiveType.BOOL.value
    node.set_attribute('type', type)

  def floatingPointLiteral (self, node: AstNode):
    # Note: A value of type float64 can never be implicitly narrowed to type float32
    type_lookup = {
      'FLOAT32_LITERAL': PrimitiveType.FLOAT32.value,
      'FLOAT64_LITERAL': PrimitiveType.FLOAT64.value,
    }
    # Map literal value's token kind to its corresponding primitive type
    type = type_lookup[node.token.kind]
    node.set_attribute('type', type)

  def integerLiteral (self, node: AstNode):
    # https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/numeric-conversions
    # A value of a constant expression of type int (for example, a value represented by an integer literal) can be implicitly converted to...
    # So an integer literal (without suffix) will always be an int32. However, during semantic
    # analysis, we may narrow it if the value is within the range of the destination.
    type_lookup = {
      'INT32_LITERAL':  PrimitiveType.INT32.value,
      'INT64_LITERAL':  PrimitiveType.INT64.value,
      'UINT32_LITERAL': PrimitiveType.UINT32.value,
      'UINT64_LITERAL': PrimitiveType.UINT64.value,
    }
    # Map literal value's token kind to its corresponding primitive type
    type = type_lookup[node.token.kind]
    node.set_attribute('type', type)

  def nullLiteral (self, node: AstNode):
    type = PrimitiveType.NULL_T.value
    node.set_attribute('type', type)

  # def unaryExpression (self, node: AstNode):
  #   # We might need some checks to make sure these operators are
  #   # operating on a valid operands (e.g. can you negate a string?)
  #   operator = node.token.kind
  #   child_node = node.child()
  #   self.expression(child_node)
  #   if operator == 'ASTERISK':
  #     # The type should be the referenced type (i.e. bare type with
  #     # pointer node stripped from it.)
  #     t: TypeNode = child_node.attribute('type')
  #     node.set_attribute('type', t.child())
  #   elif operator == 'MINUS':
  #     t: TypeNode = child_node.attribute('type')
  #     node.set_attribute('type', t)
  #   elif operator == 'EXCLAMATION':
  #     t: TypeNode = self.builtin_scope.resolve('bool')
  #     node.set_attribute('type', t)

  # def result_type (self, t1: TypeNode, t2: TypeNode, mode: str):
  #   type_map = {
  #        'int8': 0,
  #       'int16': 1,
  #       'int32': 2,
  #       'int64': 3,
  #       'uint8': 4,
  #      'uint16': 5,
  #      'uint32': 6,
  #      'uint64': 7,
  #     'float32': 8,
  #     'float64': 9
  #   }
  #   I8  = 'int8'
  #   I16 = 'int16'
  #   I32 = 'int32'
  #   I64 = 'int64'
  #   U8  = 'uint8'
  #   U16 = 'uint16'
  #   U32 = 'uint32'
  #   U64 = 'uint64'
  #   F32 = 'float32'
  #   F64 = 'float64'
  #   if mode == 'arithmetic':
  #     type_table = [
  #       #   I8,  I16,  I32,  I64,   U8,  U16,  U32,  U64,  F32,  F64
  #       [   I8,  I16,  I32,  I64, None, None, None, None,  F32,  F64 ], # I8
  #       [  I16,  I16,  I32,  I64,  I16, None, None, None,  F32,  F64 ], # I16
  #       [  I32,  I32,  I32,  I64,  I32,  I32, None, None,  F32,  F64 ], # I32
  #       [  I64,  I64,  I64,  I64,  I64,  I64,  I64, None,  F32,  F64 ], # I64
  #       [ None,  I16,  I32,  I64,   U8,  U16,  U32,  U64,  F32,  F64 ], # U8
  #       [ None, None,  I32,  I64,  U16,  U16,  U32,  U64,  F32,  F64 ], # U16
  #       [ None, None, None,  I64,  U32,  U32,  U32,  U64,  F32,  F64 ], # U32
  #       [ None, None, None, None,  U64,  U64,  U64,  U64,  F32,  F64 ], # U64
  #       [  F32,  F32,  F32,  F32,  F32,  F32,  F32,  F32,  F32,  F64 ], # F32
  #       [  F64,  F64,  F64,  F64,  F64,  F64,  F64,  F64,  F64,  F64 ]  # F64
  #     ]
  #   numeric_types = list(type_map.keys())
  #   if t1.kind in numeric_types and t2.kind in numeric_types:
  #     t1_index = type_map[t1.kind]
  #     t2_index = type_map[t2.kind]
  #     symbol: PrimitiveSymbol = self.builtin_scope.resolve(type_table[t1_index][t2_index])
  #     return symbol.type
  #   else:
  #     return None

  # def is_promoted (self, source_type: TypeNode, dest_type: TypeNode):
  #   type_map = {
  #        'int8': 0,
  #       'int16': 1,
  #       'int32': 2,
  #       'int64': 3,
  #       'uint8': 4,
  #      'uint16': 5,
  #      'uint32': 6,
  #      'uint64': 7,
  #     'float32': 8,
  #     'float64': 9
  #   }
  #   promotion_table = [
  #     #    I8,   I16,   I32,   I64,    U8,   U16,   U32,   U64,   F32,   F64
  #     [ False,  True,  True,  True, False, False, False, False,  True,  True  ], # I8
  #     [ False, False,  True,  True, False, False, False, False,  True,  True  ], # I16
  #     [ False, False, False,  True, False, False, False, False,  True,  True  ], # I32
  #     [ False, False, False, False, False, False, False, False,  True,  True  ], # I64
  #     [ False,  True,  True,  True, False, True,   True,  True,  True,  True  ], # U8
  #     [ False, False,  True,  True, False, False,  True,  True,  True,  True  ], # U16
  #     [ False, False, False,  True, False, False, False,  True,  True,  True  ], # U32
  #     [ False, False, False, False, False, False, False, False,  True,  True  ], # U64
  #     [ False, False, False, False, False, False, False, False, False,  True  ], # F32
  #     [ False, False, False, False, False, False, False, False, False, False  ]  # F64
  #   ]
  #   # Do we need to check for numeric types?
  #   st_index = type_map[source_type.kind]
  #   dt_index = type_map[dest_type.kind]
  #   result = promotion_table[st_index][dt_index]
  #   return result


  # def name (self, node: AstNode):
  #   # Look up name in symbol table
  #   name = node.token.lexeme
  #   s = self.current_scope.lookup(name)
  #   if s == None:
  #     print(f"error: name {name} not declared.")
  #   elif s.type == None:
  #     print(f"error: name {name} has unknown type.")
  #   else:
  #     node.set_attribute('type', s.type)

  # # TYPES

  # def type (self, node: AstNode):
  #   match node.kind:
  #     case 'ArrayType':
  #       self.arrayType(node)
  #     case 'NominalType':
  #       self.nominalType(node)
  #     case 'PointerType':
  #       self.pointerType(node)
  #     case 'PrimitiveType':
  #       self.primitiveType(node)
  #     case _:
  #       print(f"No matching type {node.kind}")

  # def arrayType (self, node: AstNode):
  #   # We still need to check the size to make sure it is a compile-
  #   # time integral constant.
  #   size_node = node.child(0)
  #   base_type_node = node.child(1)
  #   # This should really be a compile-time constant expression. But
  #   # we need to determine if it is a valid compile-time constant
  #   # (that is also an integer) by semantic analysis.
  #   size = size_node.token.lexeme
  #   self.type(base_type_node)
  #   type = ArrayTypeNode(size, base_type_node.attribute('type'))
  #   node.set_attribute('type', type)

  # def nominalType (self, node: AstNode):
  #   type_name = node.token.lexeme
  #   symbol: TypeSymbol = self.current_scope.resolve(type_name)
  #   type = symbol.type
  #   node.set_attribute('type', type)

  # def pointerType (self, node: AstNode):
  #   base_type_node = node.child()
  #   self.type(base_type_node)
  #   type = PointerTypeNode(base_type_node.attribute('type'))
  #   node.set_attribute('type', type)

  # def primitiveType (self, node: AstNode):
  #   type_name = node.token.lexeme
  #   symbol: TypeSymbol = self.builtin_scope.resolve(type_name)
  #   type = symbol.type
  #   node.set_attribute('type', type)
