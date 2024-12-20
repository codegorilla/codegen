from enum import Enum
from typing import List
from collections import deque

from graphlib import TopologicalSorter

from co.ast import AstNode
from co.types import TypeNode, ArrayTypeNode, PointerTypeNode, PrimitiveTypeNode
from co.st import Scope, FunctionSymbol, VariableSymbol, TypeSymbol
from co.st import ClassSymbol, PrimitiveSymbol, StructureSymbol, UnionSymbol
from co.reader import Logger, Message
from co.reader import PrimitiveType

# Purpose:

# This pass isn't run directly. It serves as a parent class that
# contains shared methods that are called by child classes.

# Compute type expressions for objects (e.g. constants and variables)
# Compute type expressions for expressions
# Possibly enforce types, but that might be a third pass

# Notes:
#
# 1. In C, global variables must be constants and must be declared
# before use. In C++, they don't need to be constants, but still need
# to be declared before use.

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

NULL_T  = PrimitiveType.NULL_T.value
BOOL    = PrimitiveType.BOOL.value
UINT8   = PrimitiveType.UINT8.value
UINT16  = PrimitiveType.UINT16.value
UINT32  = PrimitiveType.UINT32.value
UINT64  = PrimitiveType.UINT64.value
INT8    = PrimitiveType.INT8.value
INT16   = PrimitiveType.INT16.value
INT32   = PrimitiveType.INT32.value
INT64   = PrimitiveType.INT64.value
FLOAT32 = PrimitiveType.FLOAT32.value
FLOAT64 = PrimitiveType.FLOAT64.value

class Pass5:

  def __init__ (self, root_node: AstNode):
    self.root_node: AstNode = root_node
    self.logger = Logger()
    self.unsigned_types = [
      PrimitiveType.UINT8.value,
      PrimitiveType.UINT16.value,
      PrimitiveType.UINT32.value,
      PrimitiveType.UINT64.value,
    ]
    self.signed_types = [
      PrimitiveType.INT8.value,
      PrimitiveType.INT16.value,
      PrimitiveType.INT32.value,
      PrimitiveType.INT64.value,
    ]
    self.float_types = [
      PrimitiveType.FLOAT32.value,
      PrimitiveType.FLOAT64.value
    ]
    self.integral_types = self.unsigned_types + self.signed_types
    self.numeric_types  = self.integral_types + self.float_types
    self.rank_lookup = {}
    for rank, item in enumerate(self.integral_types):
      self.rank_lookup[item] = rank

  # EXPRESSIONS

  def expressionRoot (self, node: AstNode):
    print("Expr root!")
    expr_node = node.child()
    self.expression(expr_node)
    node.set_attribute('type', expr_node.attribute('type'))

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

  # BINARY EXPRESSION

  def binaryExpression (self, node: AstNode):
    # Compute left and right sub-expression types
    left_node  = node.child(0)
    right_node = node.child(1)
    self.expression(left_node)
    self.expression(right_node)
    self.usual_binary_conversions(node)
    match node.token.kind:
      case kind if kind in ['ASTERISK', 'SLASH', 'PERCENT']:
        self.multiplicativeExpression(node)
      case kind if kind in ['PLUS', 'MINUS']:
        self.additiveExpression(node)
      case kind if kind in ['LESS_LESS', 'GREATER_GREATER']:
        self.shiftExpression(node)
      case kind if kind in ['GREATER', 'LESS', 'GREATER_EQUAL', 'LESS_EQUAL']:
        self.relationalExpression(node)
      case kind if kind in ['EQUAL_EQUAL', 'EXCLAMATION_EQUAL']:
        self.equalityExpression(node)
      case kind if kind in ['AMPERSAND', 'CARET', 'BAR']:
        self.bitwiseExpression(node)

  def usual_binary_conversions (self, node: AstNode):
    left_node  = node.child(0)
    right_node = node.child(1)
    left_type  = left_node.attribute('type')
    right_type = right_node.attribute('type')
    # Rule 1: If either operand is of type float64 and the other is
    # of type float32 or integral type, then promote the other to
    # float64.
    if left_type == F64:
      if right_type == F32 or right_type in self.integral_types:
        n = self.promoteExpression(right_node, left_type)
        node.set_child(1, n)
      return
    if right_type == F64:
      if left_type == F32 or left_type in self.integral_types:
        n = self.promoteExpression(left_node, right_type)
        node.set_child(0, n)
      return
    # Rule 2: If either operand is of type float32 and the other is
    # of integral type, then promote the other to float32.
    if left_type == F32:
      if right_type in self.integral_types:
        n = self.promoteExpression(right_node, left_type)
        node.set_child(1, n)
      return
    if right_type == F32:
      if left_type in self.integral_types:
        n = self.promoteExpression(left_node, right_type)
        node.set_child(0, n)
      return
    # According to https://stackoverflow.com/questions/46073295/implicit-type-promotion-rules
    # at this point, integral promotions are performed. This needs to
    # be looked up because it can short circuit char and short
    # conversions.
    # Rule 3: If either operand is of unsigned integral type and the
    # other is also of unsigned integral type, then promote the one
    # whose type is of lesser rank to the one whose type is of higher
    # rank.
    if left_type in self.unsigned_types and right_type in self.unsigned_types:
      left_rank  = self.rank_lookup[left_type]
      right_rank = self.rank_lookup[right_type]
      if left_rank < right_rank:
        n = self.promoteExpression(left_node, right_type)
        node.set_child(0, n)
      elif left_rank > right_rank:
        n = self.promoteExpression(right_node, left_type)
        node.set_child(1, n)
      return
    # Rule 4: If either operand is of signed integral type and the
    # other is also of signed integral type, then promote the one
    # whose type is of lesser rank to the one whose type is of higher
    # rank.
    if left_type in self.signed_types and right_type in self.signed_types:
      left_rank  = self.rank_lookup[left_type]
      right_rank = self.rank_lookup[right_type]
      if left_rank < right_rank:
        n = self.promoteExpression(left_node, right_type)
        node.set_child(0, n)
      elif left_rank > right_rank:
        n = self.promoteExpression(right_node, left_type)
        node.set_child(1, n)
      return
    # Rule 5: If either operand is of unsigned integral type and the
    # other is of signed integral type, then report error because
    # this requires explicit conversion.
    if left_type in self.unsigned_types and right_type in self.signed_types:
      message = Message('error', "Incompatible operand types in expression")
      message.set_line(node.token.line)
      self.logger.add_message(message)
      return
    if right_type in self.unsigned_types and left_type in self.signed_types:
      message = Message('error', "Incompatible operand types in expression")
      message.set_line(node.token.line)
      self.logger.add_message(message)
      return

  def multiplicativeExpression (self, node: AstNode):
    left_node = node.child(0)
    result_type  = left_node.attribute('type')
    operator = node.token.kind
    if operator == 'ASTERISK' or operator == 'SLASH':
      # Operands must be of numeric type
      # Note: C++ calls these arithmetic types, but that includes
      # booleans, which we don't consider to be numeric.
      if result_type in self.numeric_types:
        node.set_attribute('type', result_type)
      else:
        message = Message('error', "Invalid operand type, must be numeric")
        message.set_line(node.token.line)
        self.logger.add_message(message)
    elif operator == 'PERCENT':
      # Modulo division requires operands to be of integral type
      if result_type in self.integral_types:
        node.set_attribute('type', result_type)
      else:
        message = Message('error', "Invalid operand type, must be integral")
        message.set_line(node.token.line)
        self.logger.add_message(message)
    else:
      # Exception
      pass

  def additiveExpression (self, node: AstNode):
    left_node = node.child(0)
    result_type  = left_node.attribute('type')
    operator = node.token.kind
    if operator == 'PLUS':
      if result_type in self.numeric_types:
        node.set_attribute('type', result_type)
      else:
        # To do: Could also be pointer + integer
        message = Message('error', "Invalid operand type, must be numeric")
        message.set_line(node.token.line)
        self.logger.add_message(message)
    elif operator == 'MINUS':
      if result_type in self.numeric_types:
        node.set_attribute('type', result_type)
      else:
        # To do: Could also be pointer - integer or pointer - pointer
        # Do we want to allow pointer arithmetic? Perhaps we should
        # only allow it inside of a block marked 'unsafe'.
        message = Message('error', "Invalid operand type, must be numeric")
        message.set_line(node.token.line)
        self.logger.add_message(message)
    else:
      # Exception
      pass

  def shiftExpression (self, node: AstNode):
    left_node = node.child(0)
    left_type = left_node.attribute('type')
    if left_type in self.integral_types:
      result_type = left_type
      node.set_attribute('type', result_type)
    else:
      message = Message('error', "Invalid operand type, must be integer")
      message.set_line(node.token.line)
      self.logger.add_message(message)

  def relationalExpression (self, node: AstNode):
    left_node  = node.child(0)
    right_node = node.child(1)
    left_type  = left_node.attribute('type')
    right_type = right_node.attribute('type')
    # To do: Need to allow for pointers too
    if left_type in self.numeric_types and right_type in self.numeric_types:
      result_type = PrimitiveType.BOOL.value
      node.set_attribute('type', result_type)
    else:
      message = Message('error', "Invalid operand type, must be numeric")
      message.set_line(node.token.line)
      self.logger.add_message(message)

  def equalityExpression (self, node: AstNode):
    left_node  = node.child(0)
    right_node = node.child(1)
    left_type  = left_node.attribute('type')
    right_type = right_node.attribute('type')
    # To do: Need to allow for pointers too
    left_cond  = left_type  in self.numeric_types or left_type  == PrimitiveType.BOOL.value
    right_cond = right_type in self.numeric_types or right_type == PrimitiveType.BOOL.value
    if left_cond and right_cond:
      result_type = PrimitiveType.BOOL.value
      node.set_attribute('type', result_type)
    else:
      message = Message('error', "Invalid operand type, must be numeric or boolean")
      message.set_line(node.token.line)
      self.logger.add_message(message)

  def bitwiseExpression (self, node: AstNode):
    left_node = node.child(0)
    left_type = left_node.attribute('type')
    if left_type in self.integral_types:
      result_type = left_type
      node.set_attribute('type', result_type)
    else:
      message = Message('error', "Invalid operand type, must be integer")
      message.set_line(node.token.line)
      self.logger.add_message(message)

  # UNARY EXPRESSION

  def unaryExpression (self, node: AstNode):
    # Compute sub-expression type
    operand_node  = node.child()
    self.expression(operand_node)
    self.usual_unary_conversions(node)
    match node.token.kind:
      case 'TILDE':
        self.bitwiseNegationExpression(node)
      case 'NOT':
        self.logicalNegationExpression(node)
      case 'MINUS':
        self.unaryMinusExpression(node)
      case 'PLUS':
        self.unaryPlusExpression(node)

  def usual_unary_conversions (self, node: AstNode):
    child_node  = node.child()
    child_type  = child_node.attribute('type')
    # Rule 1: If operand is of signed integral type with rank less
    # than int32, then promote it to type int32.
    if child_type in [ INT8, INT16 ]:
      n = self.promoteExpression(child_node, INT32)
      node.set_child(0, n)
      return
    # Rule 2: If operand is of unsigned integral type with rank less
    # than int32, then promote it to type int32 (not uint32)
    if child_type in [ UINT8, UINT16 ]:
      n = self.promoteExpression(child_node, INT32)
      node.set_child(0, n)

  def bitwiseNegationExpression (self, node: AstNode):
    operand_node = node.child()
    operand_type = operand_node.attribute('type')
    if operand_type in self.integral_types:
      result_type = operand_type
      node.set_attribute('type', result_type)
    else:
      message = Message('error', "Invalid operand type, must be integral")
      message.set_line(node.token.line)
      self.logger.add_message(message)

  def logicalNegationExpression (self, node: AstNode):
    operand_node = node.child()
    operand_type = operand_node.attribute('type')
    match operand_type:
      case PrimitiveTypeNode():
        if operand_type in (self.numeric_types + [ NULL_T, BOOL ]):
          result_type = PrimitiveType.BOOL.value
          node.set_attribute('type', result_type)
        else:
          message = Message('error', "Invalid operand type, must be boolean, numeric, or pointer")
          message.set_line(node.token.line)
          self.logger.add_message(message)
      case PointerTypeNode():
          result_type = PrimitiveType.BOOL.value
          node.set_attribute('type', result_type)
      case _:
        message = Message('error', "Invalid operand type, must be boolean, numeric, or pointer")
        message.set_line(node.token.line)
        self.logger.add_message(message)

  def unaryMinusExpression (self, node: AstNode):
    child_node = node.child()
    child_type = child_node.attribute('type')
    if child_type in self.numeric_types:
      result_type = child_type
      node.set_attribute('type', result_type)
    else:
      message = Message('error', "Invalid operand type, must be numeric")
      message.set_line(node.token.line)
      self.logger.add_message(message)

  def unaryPlusExpression (self, node: AstNode):
    child_node = node.child()
    child_type = child_node.attribute('type')
    if child_type in self.numeric_types:
      result_type = child_type
      node.set_attribute('type', result_type)
    else:
      message = Message('error', "Invalid operand type, must be numeric")
      message.set_line(node.token.line)
      self.logger.add_message(message)

  def promoteExpression (self, node: AstNode, dest_type: TypeNode) -> AstNode:
    cast_node = AstNode('PromoteCast')
    cast_node.add_child(node)
    cast_node.set_attribute('type', dest_type)
    return cast_node

  # def widenRightExpression (self, node: AstNode):
  #   # Widen right operand type to match left operand type
  #   right_node = node.child(0)
  #   left_node  = node.child(1)
  #   cast_node = AstNode('WidenCast')
  #   cast_node.add_child(right_node)
  #   cast_node.set_attribute('type', left_node.attribute('type'))
  #   node.set_child(1, cast_node)

  # def widenLeftExpression (self, node: AstNode):
  #   # Widen left operand type to match right operand type
  #   right_node = node.child(0)
  #   left_node  = node.child(1)
  #   cast_node = AstNode('WidenCast')
  #   cast_node.add_child(left_node)
  #   cast_node.set_attribute('type', right_node.attribute('type'))
  #   node.set_child(0, cast_node)

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

  def name (self, node: AstNode):
    # Look up name in symbol table
    name = node.token.lexeme
    scope: Scope = node.attribute('scope')
    symbol: VariableSymbol = scope.resolve(name)
    if symbol:
      node.set_attribute('type', symbol.type)
    else:
      print(f"error: name {name} not declared.")
