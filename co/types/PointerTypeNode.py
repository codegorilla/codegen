from co.types import TypeNode

class PointerTypeNode (TypeNode):

  def __init__ (self, base_type: TypeNode):
    super().__init__()
    self.base_type: TypeNode = base_type

  def __repr__ (self):
    return f"PointerTypeNode({self.base_type})"
