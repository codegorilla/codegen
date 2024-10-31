from co import st

class FunctionSymbol (st.Symbol):

  def __init__ (self, name: str):
    super().__init__(name)

  def addParameter (self, parameter: str):
    self.addParameter: str = parameter
