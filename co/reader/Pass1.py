from enum import Enum
from typing import List

from co.ast import AstNode
from co.types import TypeNode
from co.types import PrimitiveTypeNode, StructureTypeNode, TypealiasTypeNode, UnionTypeNode

from co.st import Scope, FunctionSymbol, VariableSymbol
from co.st import ClassSymbol, StructureSymbol, UnionSymbol, TypeSymbol

# Purpose:
#
# 1. Create scope tree
# 2. Define primitive type symbols
# 3. Define nominal type symbols
# 3. Define variable symbols
# 4. Prepare variable name references to be resolved

# Not sure if we need to define function symbols here too.

# Should we process modifiers in this pass?

# We only need to create the symbol table entries for variables. We
# do not need to set their types, which will be done in a later pass.
# This needs to be done in a later pass because types can be omitted
# when using type inference.

# I don't think this is true anymore:
# We only need to define symbols that represent types in this pass.
# We might also need to define function symbols here in order to
# allow forward references.

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
# Global variables must be initialized when declared, and their
# initializer expressions must only contain constant values, which
# may either be literals or names of constant variables.
#
# A global variable that is not initialized will get a default value
# such as the following:
# - integer: 0
# - floating point: 0.0
# - bool: false
#
# Variable declarations may not have circular definitions (direct or
# transitive). This requires building a dependency graph and checking
# for cycles.
#
# Local variables must be declared before use. Global variables do
# not have that restriction.
#
# 4. For now, we don't support nested structures, unions, or classes.
# These are all declared globally. At some point we may add nested
# structures and unions to match C, but it is unclear if nested
# classes are ever needed. They might be if they are used to
# implement lambda methods. Regardless, we do need to support nesting
# of classes within modules and/or namespaces.
#
# 5. We may only need to support forward references for structs,
# unions, classes, and functions.

class PrimitiveType (Enum):
  NULL_T  = PrimitiveTypeNode('null_t')
  BOOL    = PrimitiveTypeNode('bool')
  INT8    = PrimitiveTypeNode('int8')
  INT16   = PrimitiveTypeNode('int16')
  INT32   = PrimitiveTypeNode('int32')
  INT64   = PrimitiveTypeNode('int64')
  UINT8   = PrimitiveTypeNode('uint8')
  UINT16  = PrimitiveTypeNode('uint16')
  UINT32  = PrimitiveTypeNode('uint32')
  UINT64  = PrimitiveTypeNode('uint64')
  FLOAT32 = PrimitiveTypeNode('float32')
  FLOAT64 = PrimitiveTypeNode('float64')
  VOID    = PrimitiveTypeNode('void')

class Pass1:

  def __init__ (self, root_node: AstNode):
    self.root_node = root_node
    self.builtin_scope: Scope = Scope('Builtin')
    self.current_scope: Scope = self.builtin_scope
    self.definePrimitiveTypes()

  def definePrimitiveTypes(self):
    # Define built-in primitive types. C++ calls these "fundamental"
    # types, whereas Java uses the term "primitive" types.
    self.builtin_scope.define(TypeSymbol('null_t',  PrimitiveType.NULL_T.value))
    self.builtin_scope.define(TypeSymbol('bool',    PrimitiveType.BOOL.value))
    self.builtin_scope.define(TypeSymbol('int8',    PrimitiveType.INT8.value))
    self.builtin_scope.define(TypeSymbol('int16',   PrimitiveType.INT16.value))
    self.builtin_scope.define(TypeSymbol('int32',   PrimitiveType.INT32.value))
    self.builtin_scope.define(TypeSymbol('int64',   PrimitiveType.INT64.value))
    self.builtin_scope.define(TypeSymbol('uint8',   PrimitiveType.UINT8.value))
    self.builtin_scope.define(TypeSymbol('uint16',  PrimitiveType.UINT16.value))
    self.builtin_scope.define(TypeSymbol('uint32',  PrimitiveType.UINT32.value))
    self.builtin_scope.define(TypeSymbol('uint64',  PrimitiveType.UINT64.value))
    self.builtin_scope.define(TypeSymbol('float32', PrimitiveType.FLOAT32.value))
    self.builtin_scope.define(TypeSymbol('float64', PrimitiveType.FLOAT64.value))
    self.builtin_scope.define(TypeSymbol('void',    PrimitiveType.VOID.value))

  def process (self):
    self.translationUnit(self.root_node)

  # TRANSLATION UNIT

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
    self.variableName(node.child(0), node)
    # This was used when type specifier could be 'None'. Going
    # forward, it looks like we need to make it a real (placeholder)
    # node because we need to be able to set attributes on it, such
    # as its computed type when doing type inference.
    # spec_node = node.child(1)
    # if spec_node:
    #   self.type(spec_node)
    self.type(node.child(1))
    # Initializer is optional in some cases, so we need to check for
    # its existence.
    if node.child_count() == 3:
      self.expressionRoot(node.child(2))

  # Should we create parent node links in AST nodes or just rely on
  # passing them in during traversals? For now, pass them in via
  # traversals on an as-needed basis because it is relatively rare
  # that parent links are needed. If we find them being needed more
  # often, then we can add parent links in the future.

  # As a general rule, we want parent and child nodes to be read-only
  # when being processed by a their own child and parent nodes,
  # respectively.

  def variableName (self, node: AstNode, parent_node: AstNode):
    name = node.token.lexeme
    if self.current_scope.is_defined(name):
      print(f"error ({node.token.line}): symbol '{name}' already defined")
    else:
      symbol = VariableSymbol(name)
      symbol.set_declaration(parent_node)
      symbol.set_constant(parent_node.attribute('is_constant') == True)
      symbol.set_final(parent_node.attribute('is_final') == True)
      self.current_scope.define(symbol)
      node.set_attribute('symbol', symbol)
      # Should we also set scope attribute too? See Parr, pg. 168. If
      # we set scope attribute on appropriate nodes, then there is no
      # need to keep track of current scope in future passes.
      # We might not need to set it on variableName because we
      # already have the symbol as an attribute. But we should
      # probably set it on names in expressions because we still need
      # to be able to resolve those names.
      # node.set_attribute('scope', self.current_scope)

# TYPES

  def type (self, node: AstNode):
    match node.kind:
      case 'ArrayType':
        self.arrayType(node)

  def arrayType (self, node: AstNode):
    # Might be incompletely specified (e.g. int[]), but assume fully
    # specified for now.
    self.expressionRoot(node.child(0))
    self.type(node.child(1))

# STATEMENTS

# EXPRESSIONS

  def expressionRoot (self, node: AstNode):
    self.expression(node.child())

  def expression (self, node: AstNode):
    match node.kind:
      case 'BinaryExpression':
        self.binaryExpression(node)
      case 'UnaryExpression':
        self.unaryExpression(node)
      case 'Name':
        self.name(node)
      # There are additional node kinds that we need to address

  def binaryExpression (self, node: AstNode):
    self.expression(node.child(0))
    self.expression(node.child(1))

  def name (self, node: AstNode):
    node.set_attribute('scope', self.current_scope)

  def unaryExpression (self, node: AstNode):
    self.expression(node.child())

