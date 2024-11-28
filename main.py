from enum import Enum
from typing import List
from collections import deque

from co import reader

from co import st
from co import ast
from co import types
from co.st import Scope

from co.types import TypeNode
from co.types import TypealiasTypeNode
from co.types import ArrayTypeNode
from co.types import ClassTypeNode
from co.types import PointerTypeNode
from co.types import PrimitiveTypeNode
from co.types import StructureTypeNode
from co.types import FunctionTypeNode


# Load input from file
with open('test.co.txt', 'r') as file:
  content = file.read()
print(content)

# Create lexer
lexer = reader.Lexer()

# lexer.setInput("var x: **(*int[5])[10][20];")
# lexer.setInput("var x: fn (int, float) -> int;")
# lexer.setInput("var x: int = 1.5 + 2;")
# lexer.setInput("== = break breaks 0b1011 || |= = ==")

lexer.setInput(content)

# t = lexer.getToken()
# print(t)

# Create parser
parser = reader.Parser()
parser.setInput(lexer)
root = parser.translationUnit()

# pass0 = reader.Pass0()

pass1 = reader.Pass1()
pass1.translationUnit(root)

pass2 = reader.Pass2(pass1.builtin_scope)
pass2.translationUnit(root)

pass3 = reader.Pass3(pass1.builtin_scope)
pass3.translationUnit(root)
