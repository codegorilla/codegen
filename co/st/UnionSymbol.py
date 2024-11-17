from co.st.TypeSymbol import TypeSymbol
from co.types import TypeNode

class UnionSymbol (TypeSymbol):

  def __init__ (self, name: str, type: TypeNode):
    super().__init__(name, type)
