from enum import Enum
from typing import List
from collections import deque

from co.ast import AstNode
from co.types import TypeNode
from co.st import Scope, ConstantSymbol, FunctionSymbol, VariableSymbol
from co.st import ClassSymbol, PrimitiveSymbol, StructureSymbol, UnionSymbol

# Purpose:

# Define type (and function?) symbols

# We only need to define symbols that represent types in this pass.
# Future passes that define objects (e.g. constants, variables) will
# need to reference these type symbols. We might also need to define
# function symbols here in order to allow forward references.

# Q. Should primitive types be entered into the symbol table too?
# What advantages/disadvantages does that have?

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
    # Create built-in scope and define primitive types
    self.builtin_scope = Scope('Builtin')
    self.current_scope = self.builtin_scope
    self.definePrimitiveTypes()

  def definePrimitiveTypes (self):
    # Built-in primitive types
    self.builtin_scope.define(PrimitiveSymbol('bool',    TypeNode('bool')))
    self.builtin_scope.define(PrimitiveSymbol('int8',    TypeNode('int8')))
    self.builtin_scope.define(PrimitiveSymbol('int16',   TypeNode('int16')))
    self.builtin_scope.define(PrimitiveSymbol('int32',   TypeNode('int32')))
    self.builtin_scope.define(PrimitiveSymbol('int64',   TypeNode('int64')))
    self.builtin_scope.define(PrimitiveSymbol('uint8',   TypeNode('uint8')))
    self.builtin_scope.define(PrimitiveSymbol('uint16',  TypeNode('uint16')))
    self.builtin_scope.define(PrimitiveSymbol('uint32',  TypeNode('uint32')))
    self.builtin_scope.define(PrimitiveSymbol('uint64',  TypeNode('uint64')))
    self.builtin_scope.define(PrimitiveSymbol('float32', TypeNode('float32')))
    self.builtin_scope.define(PrimitiveSymbol('float64', TypeNode('float64')))
    # Aliases for built-in primitive types
    self.builtin_scope.define(PrimitiveSymbol('char',   TypeNode('char')))
    self.builtin_scope.define(PrimitiveSymbol('short',  TypeNode('short')))
    self.builtin_scope.define(PrimitiveSymbol('int',    TypeNode('int')))
    self.builtin_scope.define(PrimitiveSymbol('long',   TypeNode('long')))
    self.builtin_scope.define(PrimitiveSymbol('uchar',  TypeNode('uchar')))
    self.builtin_scope.define(PrimitiveSymbol('ushort', TypeNode('ushort')))
    self.builtin_scope.define(PrimitiveSymbol('uint',   TypeNode('uint')))
    self.builtin_scope.define(PrimitiveSymbol('ulong',  TypeNode('ulong')))
    self.builtin_scope.define(PrimitiveSymbol('float',  TypeNode('float')))
    self.builtin_scope.define(PrimitiveSymbol('double', TypeNode('double')))

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
      print(f"error ({node.token.line}): class '{name}' already defined")
    else:
      self.current_scope.define(ClassSymbol(name, TypeNode(name)))

  def classBody (self, node: AstNode):
    pass

  def constantDeclaration (self, node: AstNode):
    self.constantName(node.child(0))

  def constantName (self, node: AstNode):
    name = node.token.lexeme
    if self.current_scope.is_defined(name):
      print(f"error ({node.token.line}): constant '{name}' already defined")
    else:
      self.current_scope.define(ConstantSymbol(name))

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
      print(f"error ({node.token.line}): function '{name}' already defined")
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
      print(f"error ({node.token.line}): parameter '{name}' already defined")
    else:
      self.current_scope.define(VariableSymbol(name))

  def functionBody (self, node: AstNode):
    self.block(node.child())

  def block (self, node: AstNode):
    for stmt_node in node.children:
      self.statement(stmt_node)

  def statement (self, node: AstNode):
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
      print(f"error ({node.token.line}): structure '{name}' already defined")
    else:
      self.current_scope.define(StructureSymbol(name, TypeNode(name)))

  def structureBody (self, node: AstNode):
    for member_node in node.children:
      self.member(member_node)

  def member (self, node: AstNode):
    self.memberName(node.child(0))

  def memberName (self, node: AstNode):
    name = node.token.lexeme
    if self.current_scope.is_defined(name):
      print(f"error ({node.token.line}): member '{name}' already defined")
    else:
      # It seems like we can just use variable symbol here
      # Do we need to set the scope attribute on variable declaration nodes?
      self.current_scope.define(VariableSymbol(name))

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
      print(f"error ({node.token.line}): union '{name}' already defined")
    else:
      self.current_scope.define(UnionSymbol(name, TypeNode(name)))

  def unionBody (self, node: AstNode):
    for member_node in node.children:
      self.member(member_node)

  def variableDeclaration (self, node: AstNode):
    self.variableName(node.child(0))

  def variableName (self, node: AstNode):
    name = node.token.lexeme
    if self.current_scope.is_defined(name):
      print(f"error ({node.token.line}): variable '{name}' already defined")
    else:
      symbol = VariableSymbol(name)
      self.current_scope.define(symbol)
      node.set_attribute('symbol', symbol)
