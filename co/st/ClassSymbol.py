from co.st.TypeSymbol import TypeSymbol
from co.types import TypeNode

class ClassSymbol (TypeSymbol):

  def __init__ (self, name: str, type: TypeNode):
    super().__init__(name, type)

  def add_type_parameter (self, typeParameter: str):
    self.typeParameter: str = typeParameter
