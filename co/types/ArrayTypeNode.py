from co.types import TypeNode

class ArrayTypeNode (TypeNode):

  def __init__ (self, data_type: TypeNode, size: int):
    super().__init__()
    self.data_type: TypeNode = data_type
    self.size = size

  def __repr__ (self):
    return f"ArrayTypeNode({self.data_type}, {self.size})"
