from co import st

class ClassSymbol (st.Symbol):

  def __init__ (self, name: str):
    super().__init__(name)
    #self.name: str = name

  def addTypeParameter (self, typeParameter: str):
    self.addTypeParameter: str = typeParameter
