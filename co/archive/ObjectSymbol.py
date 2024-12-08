from co.st.Symbol import Symbol
from co.types import TypeNode

# Symbol representing objects (e.g. constants, variables)

class ObjectSymbol (Symbol):

  def __init__ (self, name: str):
    super().__init__(name)
    self.type: TypeNode = None

  def set_is_constant (self, is_constant: bool):
    self.is_constant: bool = is_constant

  def set_type (self, type: TypeNode):
    self.type: TypeNode = type
