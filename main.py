from enum import Enum
from typing import List
from collections import deque

from co import reader

from co import st
from co import ast
from co import types
from co.st import Scope


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

pass1 = reader.Pass1()
pass1.translationUnit(root)

pass2 = reader.Pass2()
pass2.translationUnit(root)
