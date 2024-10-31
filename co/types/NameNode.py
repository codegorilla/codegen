from .Node import Node

class NameNode (Node):

  def __init__ (self, name: str):
    super().__init__()
    self.name: str = name
