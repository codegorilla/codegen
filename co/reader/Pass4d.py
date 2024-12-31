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
from co.reader import Pass4

# Purpose:

# For each expression, determine if its type has already been
# computed. If not, compute the type of the expression.

class Pass4d (Pass4):

  def __init__ (self, root_node: AstNode):
    super().__init__(root_node)

  def process (self):
    print("Pass 4d")
    self.search(self.root_node)
    self.logger.print()

  def search (self, node: AstNode):
    if node.kind == 'ExpressionRoot':
      self.expressionRoot(node)
    else:
      for child_node in node.children:
        self.search(child_node)

  # EXPRESSIONS

  def expressionRoot (self, node: AstNode):
    if not node.attribute('type'):
      print("Expr root!")
      expr_node = node.child()
      self.expression(expr_node)
      node.set_attribute('type', expr_node.attribute('type'))
