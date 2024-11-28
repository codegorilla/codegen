from enum import Enum
from typing import List

from co.ast import AstNode
from co.types import TypeNode, TypealiasTypeNode
from co.types import PrimitiveTypeNode, StructureTypeNode, UnionTypeNode

from co.st import Scope, ConstantSymbol, FunctionSymbol, VariableSymbol
from co.st import ClassSymbol, StructureSymbol, UnionSymbol, TypeSymbol, TypealiasSymbol

# Purpose:

# Define type (and function?) symbols

# We only need to create the symbol table entries for objects. We
# do not need to set their types, which will be done in a later pass.

# I don't think this is true anymore:
# We only need to define symbols that represent types in this pass.
# Future passes that define objects (e.g. constants, variables) will
# need to reference these type symbols. We might also need to define
# function symbols here in order to allow forward references.

# We might need to do all types first before doing function symbols.

# Notes:
#
# 1. In C, global variables must be constants and must be declared
# before use. In C++, they don't need to be constants, but still need
# to be declared before use.
#
# 2. We might be able to create a dependency graph and move global
# variables to a place before they are used. However, this is not
# foolproof and circular dependencies cannot be handled anyways.
# Moreover, this would be a pretty low priority.
#
# 3. Can we just recurse through looking for declaration nodes and
# declaration statement nodes, or do we need to descend methodically?
# I think we need to descend because we need to define all symbols.
#
# 4. For now, we don't support nested structures, unions, or classes.
# These are all declared globally. At some point we may add nested
# structures and unions to match C, but it is unclear if nested
# classes are ever needed. They might be if they are used to
# implement lambda methods. Regardless, we do need to support nesting
# of classes within modules and/or namespaces.
#
# 5. We may only need to support forward references for structs,
# unions, classes, and functions. There shouldn't be any cases where
# we need to support forward references for variables.
#
# 6. We might need to add symbols for constants and variables so that
# they can be declared extern in header files. But I think this can
# be done in a future pass.

class Pass1:

  def __init__ (self):
    self.builtin_scope: Scope = Scope('Builtin')
    self.current_scope: Scope = self.builtin_scope
    self.definePrimitiveTypes()

  def definePrimitiveTypes(self):
    # Built-in primitive types
    # Is null_t (nullptr_t) considered a primitive type? Can you declare
    # a variable of this type? It seems you can in C++.
    self.builtin_scope.define(TypeSymbol('null_t',  PrimitiveTypeNode('null_t')))
    self.builtin_scope.define(TypeSymbol('bool',    PrimitiveTypeNode('bool')))
    self.builtin_scope.define(TypeSymbol('int8',    PrimitiveTypeNode('int8')))
    self.builtin_scope.define(TypeSymbol('int16',   PrimitiveTypeNode('int16')))
    self.builtin_scope.define(TypeSymbol('int32',   PrimitiveTypeNode('int32')))
    self.builtin_scope.define(TypeSymbol('int64',   PrimitiveTypeNode('int64')))
    self.builtin_scope.define(TypeSymbol('uint8',   PrimitiveTypeNode('uint8')))
    self.builtin_scope.define(TypeSymbol('uint16',  PrimitiveTypeNode('uint16')))
    self.builtin_scope.define(TypeSymbol('uint32',  PrimitiveTypeNode('uint32')))
    self.builtin_scope.define(TypeSymbol('uint64',  PrimitiveTypeNode('uint64')))
    self.builtin_scope.define(TypeSymbol('float32', PrimitiveTypeNode('float32')))
    self.builtin_scope.define(TypeSymbol('float64', PrimitiveTypeNode('float64')))
    self.builtin_scope.define(TypeSymbol('void',    PrimitiveTypeNode('void')))

  # BEGIN

  def translationUnit (self, node: AstNode):
    # Create and push global scope
    scope = Scope('Global')
    scope.set_enclosing_scope(self.current_scope)
    self.current_scope = scope
    node.set_attribute('scope', self.current_scope)
    # For now, type definitions only exist at global scope
    for decl_node in node.children:
      self.declaration(decl_node)
    # Pop global scope
    self.current_scope = self.current_scope.enclosing_scope

  # DECLARATIONS

  def declaration (self, node: AstNode):
    match node.kind:
      case 'ClassDeclaration':
        self.classDeclaration(node)
      case 'ConstantDeclaration':
        self.constantDeclaration(node)
      case 'FunctionDeclaration':
        self.functionDeclaration(node)
      case 'StructureDeclaration':
        self.structureDeclaration(node)
      case 'TypealiasDeclaration':
        self.typealiasDeclaration(node)
      case 'UnionDeclaration':
        self.unionDeclaration(node)
      case 'VariableDeclaration':
        self.variableDeclaration(node)

  def classDeclaration (self, node: AstNode):
    self.className(node.child(0))
    # Create and push new class scope
    scope = Scope('Class')
    # We could just set this to the global scope if we are sure that
    # we will never support nested classes. But for now, keep it
    # flexible.
    scope.set_enclosing_scope(self.current_scope)
    self.current_scope = scope
    node.set_attribute('scope', self.current_scope)
    self.classBody(node.child(1))
    # Pop scope
    self.current_scope = self.current_scope.enclosing_scope

  def className (self, node: AstNode):
    name = node.token.lexeme
    if self.current_scope.is_defined(name):
      print(f"error ({node.token.line}): symbol '{name}' already defined")
    else:
      self.current_scope.define(ClassSymbol(name, TypeNode(name)))

  def classBody (self, node: AstNode):
    pass

  def constantDeclaration (self, node: AstNode):
    self.constantName(node.child(0))

  def constantName (self, node: AstNode):
    name = node.token.lexeme
    if self.current_scope.is_defined(name):
      print(f"error ({node.token.line}): symbol '{name}' already defined")
    else:
      symbol = ConstantSymbol(name)
      self.current_scope.define(symbol)
      node.set_attribute('symbol', symbol)

  def functionDeclaration (self, node: AstNode):
    self.functionName(node.child(0))
    # Create and push new local scope
    scope = Scope('Local')
    # We could just set this to the global scope if we are sure that
    # we will never support nested functions. But for now, keep it
    # flexible. Standard C/C++ do not support nested functions.
    scope.set_enclosing_scope(self.current_scope)
    self.current_scope = scope
    node.set_attribute('scope', self.current_scope)
    self.parameterList(node.child(1))
    self.functionBody(node.child(3))
    # Pop scope
    self.current_scope = self.current_scope.enclosing_scope

  def functionName (self, node: AstNode):
    name = node.token.lexeme
    if self.current_scope.is_defined(name):
      print(f"error ({node.token.line}): symbol '{name}' already defined")
    else:
      self.current_scope.define(FunctionSymbol(name))

  def parameterList (self, node: AstNode):
    for param_node in node.children:
      self.parameter(param_node)

  def parameter (self, node: AstNode):
    self.parameterName(node.child(0))

  def parameterName (self, node: AstNode):
    name = node.token.lexeme
    if self.current_scope.is_defined(name):
      print(f"error ({node.token.line}): symbol '{name}' already defined")
    else:
      self.current_scope.define(VariableSymbol(name))

  def functionBody (self, node: AstNode):
    self.block(node.child())

  def block (self, node: AstNode):
    for stmt_node in node.children:
      self.statement(stmt_node)

  def statement (self, node: AstNode):
    if node.kind == 'DeclarationStatement':
      self.declarationStatement(node.child())

  def declarationStatement (self, node: AstNode):
    match node.kind:
      case 'ConstantDeclaration':
        self.constantDeclaration(node)
      case 'VariableDeclaration':
        self.variableDeclaration(node)
      case _:
        raise Exception(f"error: invalid node kind '{node.kind}' in statement")

  def structureDeclaration (self, node: AstNode):
    self.structureName(node.child(0))
    # Create and push new structure scope
    scope = Scope('Structure')
    # We could just set this to the global scope if we are sure that
    # we will never support nested structures. But for now, keep it
    # flexible.
    scope.set_enclosing_scope(self.current_scope)
    self.current_scope = scope
    node.set_attribute('scope', self.current_scope)
    self.structureBody(node.child(1))
    # Pop scope
    self.current_scope = self.current_scope.enclosing_scope

  def structureName (self, node: AstNode):
    name = node.token.lexeme
    if self.current_scope.is_defined(name):
      print(f"error ({node.token.line}): symbol '{name}' already defined")
    else:
      self.current_scope.define(TypeSymbol(name, StructureTypeNode(name)))

  def structureBody (self, node: AstNode):
    for member_node in node.children:
      self.member(member_node)

  def member (self, node: AstNode):
    self.memberName(node.child(0))

  def memberName (self, node: AstNode):
    name = node.token.lexeme
    if self.current_scope.is_defined(name):
      print(f"error ({node.token.line}): symbol '{name}' already defined")
    else:
      # It seems like we can just use variable symbol here
      # Do we need to set the scope attribute on variable declaration nodes?
      self.current_scope.define(VariableSymbol(name))

  def typealiasDeclaration (self, node: AstNode):
    # We are declaring a type alias for an existing type. Should we
    # try to resolve the actual type in this pass, or do so in
    # another pass? If we do it in another pass, then we can support
    # out-of-order typealias declarations.
    self.typealiasName(node.child(0))

  def typealiasName (self, node: AstNode):
    # Should we set a scope attribute on names that says what scope
    # they are in? I don't think so, because the scope would already
    # be tracked as you descend into scoped elements.
    name = node.token.lexeme
    if self.current_scope.is_defined(name):
      print(f"error ({node.token.line}): symbol '{name}' already defined")
    else:
      s = TypeSymbol(name, TypealiasTypeNode(name))
      self.current_scope.define(s)

  def unionDeclaration (self, node: AstNode):
    self.unionName(node.child(0))
    # Create and push new union scope
    scope = Scope('Union')
    # We could just set this to the global scope if we are sure that
    # we will never support nested unions. But for now, keep it
    # flexible.
    scope.set_enclosing_scope(self.current_scope)
    self.current_scope = scope
    node.set_attribute('scope', self.current_scope)
    self.unionBody(node.child(1))
    # Pop scope
    self.current_scope = self.current_scope.enclosing_scope

  def unionName (self, node: AstNode):
    name = node.token.lexeme
    if self.current_scope.is_defined(name):
      print(f"error ({node.token.line}): symbol '{name}' already defined")
    else:
      self.current_scope.define(TypeSymbol(name, UnionTypeNode(name)))

  def unionBody (self, node: AstNode):
    for member_node in node.children:
      self.member(member_node)

  def variableDeclaration (self, node: AstNode):
    self.variableName(node.child(0))

  def variableName (self, node: AstNode):
    name = node.token.lexeme
    if self.current_scope.is_defined(name):
      print(f"error ({node.token.line}): symbol '{name}' already defined")
    else:
      symbol = VariableSymbol(name)
      self.current_scope.define(symbol)
      node.set_attribute('symbol', symbol)
