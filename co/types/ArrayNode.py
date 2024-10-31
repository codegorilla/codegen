from .Node import Node

class ArrayNode (Node):

  def __init__ (self):
    super().__init__()
    self.reference: Node = None
    self.size: int = 0

  def setReference (self, node: Node):
    self.reference = node

  def setSize (self, size: int):
    self.size = size
