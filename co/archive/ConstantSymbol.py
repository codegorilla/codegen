from co.archive.ObjectSymbol import ObjectSymbol

class ConstantSymbol (ObjectSymbol):

  def __init__ (self, name: str):
    super().__init__(name)

  def __repr__ (self):
    return f"ConstantSymbol({self.name}, {self.type})"
