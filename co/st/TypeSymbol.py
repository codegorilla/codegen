from co.st.Symbol import Symbol
from co.types import TypeNode

# Symbol representing types (e.g. primitives, structures, unions)

class TypeSymbol (Symbol):

  def __init__ (self, name: str, type: TypeNode = None):
    super().__init__(name)
    self.type: TypeNode = type

  def __repr__ (self):
    return f"TypeSymbol({self.name}, {self.type})"

  def set_type (self, type: TypeNode):
    self.type = type
