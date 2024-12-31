from enum import Enum
from typing import List
from collections import deque

import graphlib
from graphlib import TopologicalSorter

from co.ast import AstNode
from co.types import TypeNode, ArrayTypeNode, PointerTypeNode, PrimitiveTypeNode
from co.st import Scope, FunctionSymbol, VariableSymbol, TypeSymbol
from co.st import ClassSymbol, PrimitiveSymbol, StructureSymbol, UnionSymbol
from co.reader import Logger, Message
from co.reader import PrimitiveType

# Purpose:

# Look for circular references in global variable definitions.

# Non-existent variable references was taken care of in Pass 3a for
# global variables. Should it be taken care of here instead?

# Global variable declarations may occur in any order. We must create
# a dependency graph so that we can perform a topological sort. If
# the sort fails, then at least one circular reference exists.

# To create the dependency graph, we traverse all global variable
# declarations that have initializers. In the intializer expressions,
# we find all references to other nodes and add them as dependencies
# of the current global variable.

class Pass3b:

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
    try:
      self.decl_list = list(self.sorter.static_order())
      # The list should include ALL global variables, not just those
      # with dependencies.
      # print(f"size of list is {len(self.decl_list)}")
    except graphlib.CycleError as error:
      decl_node = error.args[1][-1]
      name_node = decl_node.child()
      print(f"error({name_node.token.line}): circular name definition: {name_node.token.lexeme}")

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
    # Add this declaration to dependency graph. This ensures that the
    # declaration appears in the graph even if it has no dependencies
    # in its type specifier or initializer. That way, the graph and
    # subsequent sorted list contains a complete list of all global
    # variable declarations, which will be needed in a later pass.
    self.sorter.add(node)
    # If type specifier exists then compute dependency list and add
    # dependencies to dependency graph. If initializer exists then
    # compute dependency list and add dependencies to dependency
    # graph. The only dependencies that can come from the type
    # specifier are those associated with array size specifiers.
    spec_node = node.child(1)
    if spec_node.child_count():
      self.typeRoot(spec_node)
      dep_list: List[AstNode] = spec_node.attribute('dep_list')
      for dep_node in dep_list:
        self.sorter.add(node, dep_node)
    if node.child_count() == 3:
      init_node = node.child(2)
      self.expressionRoot(init_node)
      # Dep list is a list of symbols that this declaration is
      # dependent upon.
      dep_list: List[AstNode] = init_node.attribute('dep_list')
      for dep_node in dep_list:
        self.sorter.add(node, dep_node)

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
    scope: Scope = node.attribute('scope')
    symbol: VariableSymbol = scope.resolve(node.token.lexeme)
    if symbol:
      # Add this node as dependency of current declaration node
      return [ symbol.declaration ]
    else:
      # It's possible that the name wasn't declared, which is an error.
      # However, we might just wait until pass4b to actually print this
      # error because that pass handles all name expressions, not just
      # those without type specifiers.
      # print(f"error: name {name} not declared.")
      # Also, this might have already been handled by Pass 3a.
      return []

# TYPES

  # Array types can have expressions in their size specifiers, so we
  # need to build dependency lists for these as well.

  def typeRoot (self, node: AstNode):
    dep_list = self.type(node.child())
    node.set_attribute('dep_list', dep_list)

  def type (self, node: AstNode):
    match node.kind:
      case 'ArrayType':
        return self.arrayType(node)
      case 'PointerType':
        return self.pointerType(node)
      case _:
        return []

  def arrayType (self, node: AstNode):
    expr_root_node = node.child(0)
    self.expressionRoot(expr_root_node)
    return expr_root_node.attribute('dep_list') + self.type(node.child(1))

  def pointerType (self, node: AstNode):
    return self.type(node.child())
