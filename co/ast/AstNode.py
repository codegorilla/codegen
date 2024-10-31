from typing import List
from co.reader import Token

class AstNode:

  def __init__ (self, kind='None'):
    self._children: List['AstNode'] = []
    self._token = None
    self._kind = kind

  def __repr__ (self):
    return f"AstNode({self._kind},{self._token})"

  def get_token (self):
    return self._token

  def get_child (self, index: int) -> 'AstNode':
    return self._children[index]

  def get_child_count (self) -> int:
    return len(self._children)

  def get_children (self) -> List['AstNode']:
    return self._children

  def get_kind (self) -> str:
    return self._kind

  def add_child (self, node: 'AstNode'):
    self._children.append(node)

  def set_token (self, token: Token):
    self._token = token

  def accept (self, visitor):
    visitor.visit(self)
