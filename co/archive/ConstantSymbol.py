from co import types
from co.st.Symbol import Symbol

class ConstantSymbol (Symbol):

  def __init__ (self, name: str):
    super().__init__(name)
    self.type: types.TypeNode = None

  def set_type (self, type: types.TypeNode):
    self.type: types.TypeNode = type
