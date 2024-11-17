from typing import List

class TypeNode:

  def __init__ (self, kind: str = 'None'):
    self.kind: str = kind
    self.children: List['TypeNode'] = []

  def __repr__ (self):
    return f"TypeNode({self.kind})"

  def child (self, index: int = 0) -> 'TypeNode':
    return self.children[index]

  def child_count (self) -> int:
    return len(self.children)    

  # Deprecated
  def count (self) -> int:
    return len(self.children)

  def add_child (self, node: 'TypeNode'):
    self.children.append(node)

  def set_kind (self, kind):
    self.kind = kind
