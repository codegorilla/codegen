from co.ast import AstNode
from co.reader import Logger, Message
from co.st import Scope, FunctionSymbol, VariableSymbol
from co.st import ClassSymbol, PrimitiveSymbol, StructureSymbol, UnionSymbol


# Purpose:
# 1. Validate that constant variables, any global variables, and
# array sizes are initialized with compile-time constant expressions.

# Description:
# This works by searching for designated variable declaration nodes
# and checking if their initializer expressions evaluate to
# compile-time constants.

# Notes:
# Semantic rules that must be followed:
# - All global variable initializers must be compile-time constants.
# - All array sizes must be compile-time constants.
# - If a local variable is declared constant, then its initializer
#   must be a compile-time constant.
# - A non-final, non-constant global variable does not require an
#   initializer.

class Pass5b:

  def __init__ (self, root_node: AstNode):
    self.root_node = root_node
    self.logger = Logger()

  def process (self):
    # Search for variable declaration nodes. For now just search for
    # any globals, but eventually we need local constant variables
    # too.
    self.search(self.root_node)
    self.logger.print()

  def search (self, node: AstNode):
    match node.kind:
      case 'VariableDeclaration':
        self.variableDeclaration(node)
      case 'ArrayType':
        self.arrayType(node)
    # Continue search
    for child_node in node.children:
      if child_node:
        self.search(child_node)

  # DECLARATIONS

  def variableDeclaration (self, node: AstNode):
    # For now, only worry about global variables.
    # Ensure initializer expression evaluates to constant
    if node.child_count() == 3:
      init_node = node.child(2)
      is_constant = init_node.attribute('is_constant')
      if not is_constant:
        message = Message('error', "global initializer expression must be constant")
        message.set_line(init_node.child().token.line)
        self.logger.add_message(message)

  # TYPES

  def arrayType (self, node: AstNode):
    # Ensure array size expression evaluates to constant
    size_node = node.child(0)
    is_constant = size_node.attribute('is_constant')
    if not is_constant:
      message = Message('error', "array size must be constant")
      message.set_line(size_node.child().token.line)
      self.logger.add_message(message)
