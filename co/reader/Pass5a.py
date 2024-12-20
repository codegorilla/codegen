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
from co.reader import Pass5

# Purpose:

# For each global variable declaration that has an initializer,
# compute the type of its initializer expression. If no type
# specifier exists, use the computed type of the initialier
# expression to infer the type of the variable. Then update the type
# specifier and symbol table entry.

# Note that all global variable initializers must be constant
# expressions, meaning that their values and types can be computed at
# compile time. However, global variables may be declared out of
# order (whereas local variables follow the normal declare-before-use
# rule). In order to determine the correct ordering, we must do a
# topological sort and check for any cycles. We may be able to do
# this with DFS or Khan's algorithm.

# Expressions will often contain references to variables. Therefore,
# to compute expression types, we first need to know the types of
# variables. However, due to type inference, some variable types are
# unknown. So we need to compute the expression types for their
# initializers first, so that we can compute their types. Thus, the
# first things we must compute are initializer expression types.

class Pass5a (Pass5):

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
    symbol: VariableSymbol = name_node.attribute('symbol')
    symbol.set_type(spec_node.attribute('type'))
