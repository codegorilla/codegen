from enum import Enum
from typing import List
from typing import cast
from collections import deque

from graphlib import TopologicalSorter

from co.ast import AstNode
from co.types import TypeNode, ArrayTypeNode, PointerTypeNode, PrimitiveTypeNode
from co.st import Scope, FunctionSymbol, VariableSymbol, TypeSymbol
from co.st import ClassSymbol, PrimitiveSymbol, StructureSymbol, UnionSymbol
from co.reader import Logger, Message
from co.reader import PrimitiveType
from co.reader import Pass4

# Purpose:

# For each global variable declaration requiring type inference,
# compute the type of its initializer expression. Use this computed
# type to infer the type of the variable. Then update the type
# specifier placeholder and symbol table entry.

# Note that all global variable initializers must be constant
# expressions, meaning that their values and types can be computed at
# compile time. However, global variables may be declared out of
# order (whereas local variables follow the normal declare-before-use
# rule). In order to determine the correct ordering, we must do a
# topological sort and check for any cycles. We may be able to do
# this with DFS or Khan's algorithm.

class Pass4b (Pass4):

  def __init__ (self, root_node: AstNode, decl_list: List[AstNode]):
    super().__init__(root_node)
    self.decl_list = decl_list

  def process (self):
    # We need to process global variables that require type inference
    # first. This way, the types of all global variables will be
    # known in advance. We need to know these in advance because
    # global variables are not required to be declared before use, so
    # their order of declaration may differ significantly from their
    # order of use. In contrast, local variables must be declared
    # before use, so the types of local variables will always be
    # known before they are referenced.
    for node in self.decl_list:
      self.variableDeclaration(node)
    self.logger.print()

  # DECLARATIONS

  def variableDeclaration (self, node: AstNode):
    name_node = node.child(0)
    spec_node = node.child(1)
    init_node = node.child(2)
    self.expressionRoot(init_node)
    spec_node.set_attribute('type', init_node.attribute('type'))
    name_node.set_attribute('type', spec_node.attribute('type'))
    self.variableName(name_node)

  def variableName (self, node: AstNode):
    # Update symbol
    symbol: VariableSymbol = node.attribute('symbol')
    type = node.attribute('type')
    symbol.set_type(type)
