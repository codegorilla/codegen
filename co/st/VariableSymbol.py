from co.st.Symbol import Symbol
from co.types import TypeNode

class VariableSymbol (Symbol):

  def __init__ (self, name: str):
    super().__init__(name)
    self.type: TypeNode = None
    # Could use a flags list or dictionary instead
    self.constant_flag: bool = False
    self.final_flag: bool = False

  def __repr__ (self):
    return f"VariableSymbol({self.name}, {self.type})"

  def set_constant (self, value: bool):
    self.constant_flag = value

  def set_final (self, value: bool):
    self.final_flag = value

  def set_type (self, type: TypeNode):
    self.type = type
