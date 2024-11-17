from co.st.Symbol import Symbol
from co.types import TypeNode

# Symbol representing types (e.g. primitives, structures, unions)

class TypeSymbol (Symbol):

  def __init__ (self, name: str, type: TypeNode):
    super().__init__(name)
    self.type: TypeNode = type
