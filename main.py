from enum import Enum
from typing import List
from collections import deque

from co import reader
from co.reader import Parser, Pass1, Pass2
from co.reader import Pass3a, Pass3b
from co.reader import Pass4a, Pass4b, Pass4c, Pass4d

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
with open('test.co.txt', 'rt', newline='') as file:
  content = file.read()
print(content)

# Create lexer
lexer = reader.Lexer()
lexer.setInput(content)

# Create parser
parser = Parser(lexer)
root = parser.process()

# To do: For each source file in the package, we parse it and add it to a
# package AstNode.

pass1 = Pass1(root)
pass1.process()

pass2 = Pass2(root, pass1.builtin_scope)
pass2.process()

pass3a = Pass3a(root)
pass3a.process()

pass3b = Pass3b(root)
pass3b.process()

# pass4a = Pass4a(root)
# pass4a.process()

# pass4b = Pass4b(root, pass4a.decl_list)
# pass4b.process()

# pass4c = Pass4c(root)
# pass4c.process()

# pass5c = Pass5c(root)
# pass5c.process()

# pass5d = Pass5d(root)
# pass5d.process()

