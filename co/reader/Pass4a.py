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

# Perform topological sort on global variable declarations.

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
    # for node in self.ordered:
    #   print(node.children)
    self.logger.print()

  # TRANSLATION UNIT

  def translationUnit (self, node: AstNode):
    for decl_node in node.children:
      self.declaration(decl_node)

  # DECLARATIONS
      
  def declaration (self, node: AstNode):
    match node.kind:
      case 'VariableDeclaration':
        self.variableDeclaration(node)
    
  def variableDeclaration (self, node: AstNode):
    print("found global var")
    spec_node = node.child(1)
    # If type specifier does not exist, that is our cue that this
    # declaration node needs to be added to the dependency graph. We
    # need to pass down the current declaration node so that we can
    # add to its dependency list.
    if spec_node.kind == 'AlphaType':
      init_node = node.child(2)
      self.expressionRoot(init_node, node)

  # We aren't trying to compute the type yet. We just need to build a
  # graph so that we can do a topological sort.

  # EXPRESSIONS

  def expressionRoot (self, node: AstNode, decl_node: AstNode):
    expr_node = node.child()
    self.expression(expr_node, decl_node)

  def expression (self, node: AstNode, decl_node: AstNode):
    # Dispatch method
    match node.kind:
      case 'BinaryExpression':
        self.binaryExpression(node, decl_node)
      case 'UnaryExpression':
        self.unaryExpression(node, decl_node)
      case 'Name':
        self.name(node, decl_node)

  def binaryExpression (self, node: AstNode, decl_node: AstNode):
    left_node  = node.child(0)
    right_node = node.child(1)
    self.expression(left_node, decl_node)
    self.expression(right_node, decl_node)

  def unaryExpression (self, node: AstNode, decl_node: AstNode):
    oper_node = node.child()
    self.expression(oper_node, decl_node)

  def name (self, node: AstNode, decl_node: AstNode):
    # Look up name in symbol table
    name = node.token.lexeme
    scope: Scope = node.attribute('scope')
    symbol: VariableSymbol = scope.resolve(name)
    # It's possible that the name wasn't declared, which is an error.
    # However, we might just wait until pass4b to actually print this
    # error because that pass handles all name expressions, not just
    # those without type specifiers.
    # if symbol == None:
    #   print(f"error: name {name} not declared.")
    # else:
    if symbol:
      # Determine declaration node of name
      predecessor_decl_node = symbol.declaration
      # Add this node as dependency of current declaration node
      self.sorter.add(decl_node, predecessor_decl_node)
