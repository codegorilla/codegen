from co.st.Symbol import Symbol

class FunctionSymbol (Symbol):

  def __init__ (self, name: str):
    super().__init__(name)

  def add_parameter (self, parameter: str):
    self.parameter: str = parameter
