from co.types import TypeNode

class TypealiasTypeNode (TypeNode):

  # Is actual type ever known before creating this type node?
  # Probably not, because we create this in pass 1, but the actual
  # type is determined in pass 2.

  def __init__ (self, name: str):
    super().__init__()
    self.name: str = name
    self.actual_type: TypeNode = None

  def __repr__ (self):
    return f"TypealiasTypeNode({self.name}, {self.actual_type})"

  def set_actual_type (self, actual_type: TypeNode):
    self.actual_type = actual_type
