from typing import List
from co.reader import Token

class AstNode:

  def __init__ (self, kind: str = 'None'):
    self.kind = kind
    self.children: List['AstNode'] = []
    self.token = None
    self.attributes: dict = {}

  def __repr__ (self):
    return f"AstNode({self.kind},{self.token})"

  def child (self, index: int = 0) -> 'AstNode':
    return self.children[index]

  def child_count (self) -> int:
    return len(self.children)

  def add_child (self, node: 'AstNode'):
    self.children.append(node)

  def set_child (self, index: int, node: 'AstNode'):
    self.children[index] = node

  def set_kind (self, kind: str):
    self.kind = kind

  def set_token (self, token: Token):
    self.token = token

  def attribute (self, name: str):
    return self.attributes[name]

  def set_attribute (self, name: str, value):
    self.attributes[name] = value


  # def accept (self, visitor):
  #   visitor.visit(self)
