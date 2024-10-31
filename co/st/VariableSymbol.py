from co import st
from co import types

class VariableSymbol (st.Symbol):

  def __init__ (self, name: str):
    super().__init__(name)
    self.type = None

  def setType (self, type: types.Node):
    self.type: types.Node = type
