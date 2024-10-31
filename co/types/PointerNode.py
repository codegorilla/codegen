from .Node import Node

class PointerNode (Node):

  def __init__ (self):
    super().__init__()
    self.reference: Node = None

  def setReference (self, node: Node):
    self.reference = node
