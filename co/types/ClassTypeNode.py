from co.types import TypeNode

class ClassTypeNode (TypeNode):

  def __init__ (self, name: str):
    super().__init__()
    self.name: str = name

  def __repr__ (self):
    return f"ClassTypeNode({self.name})"
