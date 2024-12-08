from co.types import TypeNode

class ArrayTypeNode (TypeNode):

  def __init__ (self, base_type: TypeNode, size: int):
    super().__init__()
    self.base_type: TypeNode = base_type
    self.size: int = size

  def __repr__ (self):
    return f"ArrayTypeNode({self.base_type}, {self.size})"
