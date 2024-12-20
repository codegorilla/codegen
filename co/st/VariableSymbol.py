from co.ast import AstNode
from co.st.Symbol import Symbol
from co.types import TypeNode

class VariableSymbol (Symbol):

  def __init__ (self, name: str):
    super().__init__(name)
    self.type: TypeNode = None
    self.declaration: AstNode = None
    # Could use a flags list or dictionary instead
    self.constant_flag = False
    self.final_flag = False
    # Do we need this?
    # self.global_flag = False

  def __repr__ (self):
    return f"VariableSymbol({self.name}, {self.type})"

  def set_constant (self, value: bool):
    self.constant_flag = value

  def set_declaration (self, declaration: AstNode):
    self.declaration = declaration

  def set_final (self, value: bool):
    self.final_flag = value

  # Do we need this here, or on the variable declaration itself?
  # Currently, I believe this should be on the variable declaration itself.
  # def set_global (self, value: bool):
  #   self.global_flag = value

  def set_type (self, type: TypeNode):
    self.type = type

