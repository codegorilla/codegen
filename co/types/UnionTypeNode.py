from co.types import TypeNode

class UnionTypeNode (TypeNode):

  def __init__ (self, name: str):
    super().__init__()
    self.name: str = name

  def __repr__ (self):
    return f"UnionTypeNode({self.name})"
