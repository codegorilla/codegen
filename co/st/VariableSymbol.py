from co.st.ObjectSymbol import ObjectSymbol

class VariableSymbol (ObjectSymbol):

  def __init__ (self, name: str):
    super().__init__(name)

  def __repr__ (self):
    return f"VariableSymbol({self.name}, {self.type})"
