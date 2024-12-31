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

# 1. Check for illegal references to undeclared variables.
# 2. Check for illegal forward references in expressions.

# Although we can easily detect references to undeclared variables,
# we cannot easily detect references to uninitalized variables
# without performing control flow analysis. That must occur in a much
# later pass.

# Valid:
# var t = 1; x = t;
# Detectable:
# x = t; var t = 1;
# Not detectable (here):
# var t; x = t;
# Marginally detectable with extra work (not sure if its worth it
# because this is generally pretty obvious to a developer):
# var t = t;

class Pass3a:

  def __init__ (self, root_node: AstNode):
    self.root_node = root_node
    self.logger = Logger()

  def process (self):
    self.search(self.root_node)
    self.logger.print()

  # To do: We want the search to only occur for expressions in local
  # scopes. Global scopes allow forward references.

  def search (self, node: AstNode):
    if node.kind == 'ExpressionRoot':
      self.expressionRoot(node)
    else:
      for child_node in node.children:
        self.search(child_node)

  def expressionRoot (self, node: AstNode):
    self.expression(node.child())

  def expression (self, node: AstNode):
    # Dispatch method
    match node.kind:
      case 'BinaryExpression':
        self.binaryExpression(node)
      case 'UnaryExpression':
        self.unaryExpression(node)
      case 'Name':
        self.name(node)

  def binaryExpression (self, node: AstNode):
    self.expression(node.child(0))
    self.expression(node.child(1))

  def unaryExpression (self, node: AstNode):
    self.expression(node.child())

  # Non-existent variable references:
  # If name doesn't resolve, then the variable doesn't exist.

  # Illegal forward references:
  # Resolve the name. Get the token of the associated symbol. If the
  # name's token position comes before the symbol's token position
  # then then this is an illegal forward reference. (But only for
  # local scopes.)
  
  def name (self, node: AstNode):
    # Look up name in symbol table
    name = node.token.lexeme
    scope: Scope = node.attribute('scope')
    # print(scope.kind)
    symbol: VariableSymbol = scope.resolve(name)
    if symbol:
      decl_node = symbol.declaration
      if not decl_node.attribute('is_global'):
        name_node = decl_node.child(0)
        ref_position = node.token.position
        def_position = name_node.token.position
        if ref_position < def_position:
          print(f"error({node.token.line}): variable '{name}' referenced before declaration.")
    else:
      print(f"error({node.token.line}): name '{name}' not declared.")
