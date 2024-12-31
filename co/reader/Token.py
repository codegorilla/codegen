
class Token:

  def __init__ (self, kind: str, lexeme: str, position: int, line: int, column: int):
    self.kind = kind
    # Need to change lexeme to value
    self.lexeme = lexeme
    self.position = position
    self.line = line
    self.column = column

  def __repr__ (self):
    return f"Token({self.kind}, '{self.lexeme}', {self.position}, {self.line}, {self.column})"
