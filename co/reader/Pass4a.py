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

# I believe this is not needed anymore. We created a topologically
# sorted list of all global variables in pass 3b. That is all we need
# to start determining type information.

# 1. Compute types of global variables that have type specifiers.
# 2. Create list of global variables that do not have type specifiers
# and perform topological sort on it.

# Global variable declarations may occur in any order. We must create
# a dependency graph so that we can perform a topological sort. This
# will allow us to determine (in a later pass) the type of each
# variable when type inference is used.

# To create the dependency graph, we traverse all global variable
# declarations that have initializers. In the intializer expressions,
# we find all references to other nodes and add them as dependencies
# of the current global variable.

class Pass4a:

  def __init__ (self, root_node: AstNode):
    self.root_node = root_node
    self.logger = Logger()
    # Sorter is a dependency graph of variable declarations
    self.sorter = TopologicalSorter()
    self.decl_list: List[AstNode] = None

  def process (self):
    # Build global variable dependency graph
    self.translationUnit(self.root_node)
    # Perform topological sort on dependency graph
    self.decl_list = list(self.sorter.static_order())
    self.logger.print()

  # TRANSLATION UNIT

  def translationUnit (self, node: AstNode):
    for decl_node in node.children:
      self.declaration(decl_node)

  # DECLARATIONS
      
  def declaration (self, node: AstNode):
    # Dispatch method
    match node.kind:
      case 'VariableDeclaration':
        self.variableDeclaration(node)

  def variableDeclaration (self, node: AstNode):
    spec_node = node.child(1)
    # If type specifier exists, then compute the type expression and
    # update the variable's symbol to match. Otherwise, add this
    # declaration node to the dependency graph. We need to pass down
    # the current declaration node so that we can add to its
    # dependency list.
    if spec_node.child_count():
      self.typeRoot(spec_node)
      name_node = node.child(0)
      name_node.set_attribute('type', spec_node.attribute('type'))
      self.variableName(name_node)
    else:
      init_node = node.child(2)
      self.expressionRoot(init_node)
      # Dep list is a list of symbols that this declaration is
      # dependent upon.
      dep_list: List[AstNode] = init_node.attribute('dep_list')
      for dep_node in dep_list:
        self.sorter.add(node, dep_node)

  def variableName (self, node: AstNode):
    # Update symbol
    symbol: VariableSymbol = node.attribute('symbol')
    type = node.attribute('type')
    symbol.set_type(type)

  # We aren't trying to compute the type yet. We just need to build a
  # graph of dependencies so that we can do a topological sort. The
  # dependencies are the declarations that the current declaration
  # depends on.

  # EXPRESSIONS

  def expressionRoot (self, node: AstNode):
    dep_list = self.expression(node.child())
    node.set_attribute('dep_list', dep_list)

  def expression (self, node: AstNode) -> List[AstNode]:
    # Dispatch method
    match node.kind:
      case 'BinaryExpression':
        return self.binaryExpression(node)
      case 'UnaryExpression':
        return self.unaryExpression(node)
      case 'Name':
        return self.name(node)
      case _:
        return []

  def binaryExpression (self, node: AstNode) -> List[AstNode]:
    return self.expression(node.child(0)) + self.expression(node.child(1))

  def unaryExpression (self, node: AstNode) -> List[AstNode]:
    return self.expression(node.child())

  def name (self, node: AstNode) -> List[AstNode]:
    # Look up name in symbol table
    name = node.token.lexeme
    scope: Scope = node.attribute('scope')
    symbol: VariableSymbol = scope.resolve(name)
    if symbol:
      # Add this node as dependency of current declaration node
      return [ symbol.declaration ]
    else:
    # It's possible that the name wasn't declared, which is an error.
    # However, we might just wait until pass4b to actually print this
    # error because that pass handles all name expressions, not just
    # those without type specifiers.
    # print(f"error: name {name} not declared.")
      return []

# TYPES

  def typeRoot (self, node: AstNode):
    type = self.type(node.child())
    node.set_attribute('type', type)

  def type (self, node: AstNode) -> TypeNode:
    match node.kind:
      case 'ArrayType':
        return self.arrayType(node)
      case 'NominalType':
        return self.nominalType(node)
      case 'PointerType':
        return self.pointerType(node)
      case 'PrimitiveType':
        return self.primitiveType(node)
      case _:
        print(f"No matching type {node.kind}")

  def arrayType (self, node: AstNode) -> TypeNode:
    # We still need to check the size to make sure it is a compile-
    # time integral constant.
    size_node = node.child(0)
    # Might be incompletely specified (e.g. int[]), but assume fully
    # specified for now.
    # This should really be a compile-time constant expression. But
    # we need to determine if it is a valid compile-time constant
    # (that is also an integer) by semantic analysis.
    size = size_node.token.lexeme
    base_type = self.type(node.child(1))
    return ArrayTypeNode(size, base_type)

  def nominalType (self, node: AstNode) -> TypeNode:
    type_name = node.token.lexeme
    symbol: TypeSymbol = self.current_scope.resolve(type_name)
    return symbol.type

  def pointerType (self, node: AstNode) -> TypeNode:
    base_type = self.type(node.child())
    return PointerTypeNode(base_type)  

  def primitiveType (self, node: AstNode) -> TypeNode:
    match node.token.kind:
      case 'NULL_T':
        return PrimitiveType.NULL_T.value
      case 'BOOL':
        return PrimitiveType.BOOL.value
      case 'UINT8':
        return PrimitiveType.UINT8.value
      case 'UINT16':
        return PrimitiveType.UINT16.value
      case 'UINT32':
        return PrimitiveType.UINT32.value
      case 'UINT64':
        return PrimitiveType.UINT64.value
      case 'INT8':
        return PrimitiveType.INT8.value
      case 'INT16':
        return PrimitiveType.INT16.value
      case 'INT32':
        return PrimitiveType.INT32.value
      case 'INT64':
        return PrimitiveType.INT64.value
      case 'FLOAT32':
        return PrimitiveType.FLOAT32.value
      case 'FLOAT64':
        return PrimitiveType.FLOAT64.value
      case _:
        print("error: Invalid primitive type")
