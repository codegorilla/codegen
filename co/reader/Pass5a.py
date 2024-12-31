from co.ast import AstNode
from co.st import Scope, FunctionSymbol, VariableSymbol
from co.st import ClassSymbol, PrimitiveSymbol, StructureSymbol, UnionSymbol


# Purpose:
# 1. Determine if expressions are compile-time constants

# Description:
# This works by searching for expression root nodes. These are the
# top-most nodes in an expression tree. For each expression root node
# found, we perform a post-order traversal to compute the
# 'is_constant' attribute for each node, in bottom-up fashion, ending
# with the expression root node itself.

class Pass5a:

  def __init__ (self, root_node: AstNode):
    self.root_node = root_node

  def process (self):
    # Search for expression roots
    self.search(self.root_node)

  def search (self, node: AstNode):
    if node.kind == 'ExpressionRoot':
      self.expressionRoot(node)
    else:
      for child_node in node.children:
        if child_node:
          self.search(child_node)

  # EXPRESSIONS

  def expressionRoot (self, node: AstNode):
    expr_node = node.child()
    self.expression(expr_node)
    result = expr_node.attribute('is_constant')
    node.set_attribute('is_constant', result)

  def expression (self, node: AstNode):
    # Dispatch method
    match node.kind:
      case 'BinaryExpression':
        self.binaryExpression(node)
      case 'UnaryExpression':
        self.unaryExpression(node)
      case 'Name':
        self.name(node)
      case kind if kind in [
        'BooleanLiteral',
        'FloatingPointLiteral',
        'IntegerLiteral'
      ]:
        self.literal(node)

  def binaryExpression (self, node: AstNode):
    left_node  = node.child(0)
    right_node = node.child(1)
    self.expression(left_node)
    self.expression(right_node)
    result = left_node.attribute('is_constant') and right_node.attribute('is_constant')
    node.set_attribute('is_constant', result)

  def name (self, node: AstNode):
    scope: Scope = node.attribute('scope')
    symbol: VariableSymbol = scope.resolve(node.token.lexeme)
    result = symbol.constant_flag
    node.set_attribute('is_constant', result)

  def literal (self, node: AstNode):
    result = True
    node.set_attribute('is_constant', result)

  def unaryExpression (self, node: AstNode):
    expr_node = node.child()
    self.expression(expr_node)
    result = expr_node.attribute('is_constant')
    node.set_attribute('is_constant', result)
