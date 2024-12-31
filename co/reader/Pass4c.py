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

# For each local variable declaration, if it has an initializer,
# compute the type of the initializer expression. If it has a type
# specifier, compute its type from the type specifier. Otherwise set
# its type as the type of the initializer expression.

## that has an initializer,
## compute the type of its initializer expression. If no type
## specifier exists, use the computed type of the initialier
## expression to infer the type of the variable. Then update the type
## specifier and symbol table entry.

class Pass4c (Pass4):

  def __init__ (self, root_node: AstNode):
    super().__init__(root_node)

  def process (self):
    self.translationUnit(self.root_node)
    self.logger.print()

  # TRANSLATION UNIT

  def translationUnit (self, node: AstNode):
    for decl_node in node.children:
      self.declaration(decl_node)

  # DECLARATIONS
      
  def declaration (self, node: AstNode):
    # Dispatch method
    match node.kind:
      case 'FunctionDeclaration':
        self.functionDeclaration(node)

  def functionDeclaration (self, node: AstNode):
    self.functionBody(node.child(3))

  def functionBody (self, node: AstNode):
    self.topBlock(node.child())

  def topBlock (self, node: AstNode):
    for stmt_node in node.children:
      self.statement(stmt_node)

  def variableDeclaration (self, node: AstNode):
    print("var decl")
    spec_node = node.child(1)
    has_type_specifier = spec_node.child_count()
    has_initializer = node.child_count() == 3
    if has_type_specifier:
      # Compute type of type specifier. Inherit type to name node in
      # preparation for updating symbol table entry.
      self.typeRoot(spec_node)
      name_node = node.child(0)
      name_node.set_attribute('type', spec_node.attribute('type'))
      self.variableName(name_node)
      if has_initializer:
        # Compute type of initializer
        init_node = node.child(2)
        self.expressionRoot(init_node)
    else:
      if has_initializer:
        print("HERE")
        # Compute type of initializer. Inherit type to spec node, and
        # then name node in preparation for updating symbol table
        # entry.
        init_node = node.child(2)
        self.expressionRoot(init_node)
        spec_node.set_attribute('type', init_node.attribute('type'))
        name_node = node.child(0)
        name_node.set_attribute('type', spec_node.attribute('type'))
        self.variableName(name_node)
      else:
        # This is an error condition. This scenario should never be
        # possible, and thus should never occur.
        pass

  def variableName (self, node: AstNode):
    # Update symbol
    symbol: VariableSymbol = node.attribute('symbol')
    type = node.attribute('type')
    symbol.set_type(type)

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
