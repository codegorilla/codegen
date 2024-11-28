from co.st.TypeSymbol import TypeSymbol
from co.types import PrimitiveTypeNode

class PrimitiveSymbol (TypeSymbol):

  def __init__ (self, name: str, type: PrimitiveTypeNode):
    super().__init__(name, type)
    # Might need a size field in bytes, or that might be part of the
    # type.
