from enum import Enum
from typing import List
from collections import deque

# from co import ast
# from co import types

from co.ast import AstNode
from co.types import TypeNode, ArrayTypeNode, PointerTypeNode, TypealiasTypeNode
from co.st import Scope, FunctionSymbol, VariableSymbol, TypeSymbol
from co.st import ClassSymbol, PrimitiveSymbol, StructureSymbol, UnionSymbol


# Purpose:

# Compute type expressions for typealiases

class Pass2:

  def __init__ (self, root_node: AstNode, builtin_scope: Scope):
    # Might not need scopes this round
    self.root_node = root_node
    self.builtin_scope: Scope = builtin_scope
    self.current_scope: Scope = builtin_scope

  def process (self):
    self.translationUnit(self.root_node)

  # TRANSLATION UNIT

  def translationUnit (self, node: AstNode):
    self.current_scope = node.attribute('scope')
    for decl_node in node.children:
      self.declaration(decl_node)

  # DECLARATIONS

  def declaration (self, node: AstNode):
    if node.kind == 'TypealiasDeclaration':
      self.typealiasDeclaration(node)

  def typealiasDeclaration (self, node: AstNode):
    name_node = node.child(0)
    type_node = node.child(1)
    self.type(type_node)
    # Do we set the type on the name node or update its symbol in the
    # symbol table, or both? I believe in the case of a typealias, we
    # just need to update its symbol in the symbol table because we
    # won't be trying to type check the typealias declaration itself.
    name = name_node.token.lexeme
    symbol: TypeSymbol = self.current_scope.resolve(name)
    # Assume this is a typealias type, otherwise it would be an
    # exception.
    t: TypealiasTypeNode = symbol.type
    t.set_actual_type(type_node.attribute('type'))

  # TYPES

  def type (self, node: AstNode):
    match node.kind:
      case 'ArrayType':
        self.arrayType(node)
      case 'NominalType':
        self.nominalType(node)
      case 'PointerType':
        self.pointerType(node)
      case 'PrimitiveType':
        self.primitiveType(node)
      case _:
        print(f"No matching type {node.kind}")

  def arrayType (self, node: AstNode):
    # We still need to check the size to make sure it is a compile-
    # time integral constant.
    size_node = node.child(0)
    base_type_node = node.child(1)
    # This should really be a compile-time constant expression. But
    # we need to determine if it is a valid compile-time constant
    # (that is also an integer) by semantic analysis.
    size = size_node.token.lexeme
    self.type(base_type_node)
    type = ArrayTypeNode(size, base_type_node.attribute('type'))
    node.set_attribute('type', type)

  def nominalType (self, node: AstNode):
    type_name = node.token.lexeme
    symbol: TypeSymbol = self.current_scope.resolve(type_name)
    type = symbol.type
    node.set_attribute('type', type)

  def pointerType (self, node: AstNode):
    base_type_node = node.child()
    self.type(base_type_node)
    type = PointerTypeNode(base_type_node.attribute('type'))
    node.set_attribute('type', type)

  def primitiveType (self, node: AstNode):
    type_name = node.token.lexeme
    symbol: TypeSymbol = self.builtin_scope.resolve(type_name)
    type = symbol.type
    node.set_attribute('type', type)
