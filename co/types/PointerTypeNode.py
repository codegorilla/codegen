from co.types import TypeNode

class PointerTypeNode (TypeNode):

  def __init__ (self, data_type: TypeNode):
    super().__init__()
    self.data_type: TypeNode = data_type

  def __repr__ (self):
    return f"PointerTypeNode({self.data_type})"
