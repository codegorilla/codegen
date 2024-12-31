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

# Perform type checking by comparing expression types to what is
# expected.

class Pass4e:

  def __init__ (self, root_node: AstNode):
    self.root_node = root_node
    self.logger = Logger()

  def process (self):
    self.translationUnit(self.root_node)
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
    print("GOT HERE...")
    spec_node = node.child(1)
    init_node = node.child(2)
    t1 = spec_node.attribute('type')
    t2 = init_node.attribute('type')
    print(t1)
    print(t2)


  def functionDeclaration (self, node: AstNode):
    self.functionBody(node.child(3))

  def functionBody (self, node: AstNode):
    self.topBlock(node.child())

  def topBlock (self, node: AstNode):
    for stmt_node in node.children:
      self.statement(stmt_node)

  # def variableDeclaration (self, node: AstNode):
  #   print("var decl")
  #   name_node = node.child(0)
  #   spec_node = node.child(1)
  #   # If type specifier does not exist, that is our cue that this
  #   # declaration requires type inference.
  #   if spec_node.kind == 'AlphaType':
  #     init_node = node.child(2)
  #     self.expressionRoot(init_node)
  #     spec_node.set_attribute('type', init_node.attribute('type'))
  #     symbol: VariableSymbol = name_node.attribute('symbol')
  #     symbol.set_type(spec_node.attribute('type'))

  # STATEMENTS

  def statement (self, node: AstNode):
    if node.kind == 'DeclarationStatement':
      self.declarationStatement(node)

  def declarationStatement (self, node: AstNode):
    # Need to get child in this case
    child_node = node.child()
    match child_node.kind:
      case 'VariableDeclaration':
        self.variableDeclaration(child_node)

