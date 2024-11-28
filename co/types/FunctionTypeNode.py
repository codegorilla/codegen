from typing import List
from co.types import TypeNode

class FunctionTypeNode (TypeNode):

  def __init__ (self, parameter_types: List[TypeNode] = []):
    super().__init__()
    self.parameter_types: List[TypeNode] = parameter_types
    self.return_type = None

  def add_parameter_type (self, parameter_type: TypeNode):
    self.parameter_types.append(parameter_type)

  def parameter_type (self, index: int):
    return self.parameter_types[index]

  def set_return_type (self, return_type: TypeNode):
    self.return_type = return_type

  def __repr__ (self):
    return f"FunctionTypeNode({[t for t in self.parameter_types]}, {self.return_type})"
