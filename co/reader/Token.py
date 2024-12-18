
class Token:

  def __init__ (self, kind: str, lexeme: str, line: int, position: int):
    self.kind = kind
    # Need to change lexeme to value
    self.lexeme = lexeme
    self.line = line
    self.position = position

  def __repr__ (self):
    return f"Token({self.kind}, '{self.lexeme}', {self.line}, {self.position})"
