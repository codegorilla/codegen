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
    self.typeRoot(type_node)
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

  # Note: The type root for a type alias cannot be empty. It must
  # have a valid child.

  def typeRoot (self, node: AstNode):
    type = self.type(node.child())
    node.set_attribute('type', type)
    # print(node.attribute('type'))

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
    # Could alternatively do node.token.kind instead
    type_name = node.token.lexeme
    symbol: TypeSymbol = self.builtin_scope.resolve(type_name)
    return symbol.type
