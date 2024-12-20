from typing import List
from co.reader import Token

from co.ast import AstNode

class DependencyNode:

  def __init__ (self):
    self.node: AstNode
    self.edges: List['DependencyNode'] = []

  def __repr__ (self):
    return f"DependencyNode({self.node})"

  def edge (self, index: int = 0) -> 'DependencyNode':
    return self.edges[index]

  def edge_count (self) -> int:
    return len(self.edges)

  def add_edge (self, node: 'AstNode'):
    self.edges.append(node)
