from co.types import TypeNode
from co.types import PrimitiveTypeNode
from co.types import PointerTypeNode

from co.st import Scope
from co.st import TypeSymbol

# Purpose:

# Define primitive types and establish built-in scope

class Pass0:

  def __init__ (self):
    # Create built-in scope and define primitive types
    self.builtin_scope = Scope('Builtin')
    self.definePrimitiveTypes()

  def definePrimitiveTypes (self):
    # Is nullptr considered a primitive type? Can you declare
    # a variable of this type? It seems you can in C++.
    T_NULLPTR = PrimitiveTypeNode('nullptr')
    T_BOOL    = PrimitiveTypeNode('bool')
    T_INT8    = PrimitiveTypeNode('int8')
    T_INT16   = PrimitiveTypeNode('int16')
    T_INT32   = PrimitiveTypeNode('int32')
    T_INT64   = PrimitiveTypeNode('int64')
    T_UINT8   = PrimitiveTypeNode('uint8')
    T_UINT16  = PrimitiveTypeNode('uint16')
    T_UINT32  = PrimitiveTypeNode('uint32')
    T_UINT64  = PrimitiveTypeNode('uint64')
    T_FLOAT32 = PrimitiveTypeNode('float32')
    T_FLOAT64 = PrimitiveTypeNode('float64')
    T_VOID    = PrimitiveTypeNode('void')
    # Built-in primitive types
    self.builtin_scope.define(TypeSymbol('nullptr', T_NULLPTR))
    self.builtin_scope.define(TypeSymbol('bool',    T_BOOL))
    self.builtin_scope.define(TypeSymbol('int8',    T_INT8))
    self.builtin_scope.define(TypeSymbol('int16',   T_INT16))
    self.builtin_scope.define(TypeSymbol('int32',   T_INT32))
    self.builtin_scope.define(TypeSymbol('int64',   T_INT64))
    self.builtin_scope.define(TypeSymbol('uint8',   T_UINT8))
    self.builtin_scope.define(TypeSymbol('uint16',  T_UINT16))
    self.builtin_scope.define(TypeSymbol('uint32',  T_UINT32))
    self.builtin_scope.define(TypeSymbol('uint64',  T_UINT64))
    self.builtin_scope.define(TypeSymbol('float32', T_FLOAT32))
    self.builtin_scope.define(TypeSymbol('float64', T_FLOAT64))
    self.builtin_scope.define(TypeSymbol('void',    T_VOID))
