from co.st.Symbol import Symbol
from co.types import TypeNode

# Provides ability to create alias for a type symbols.

# Should this inherit from TypeSymbol?

# Not sure if this is needed or if TypeSymbol has all types covered

class TypealiasSymbol (Symbol):

  def __init__ (self, name: str, type: TypeNode, underlying_type: TypeNode):
    super().__init__(name)
    # Needs to have underlying type
    # Not necessarily defined upfront?
    self.underlying_type = underlying_type
