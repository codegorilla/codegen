class Message:

  def __init__ (self, kind: str, text: str):
    # Error or warning
    self.kind = kind
    # Information to be conveyed
    self.text = text

  def set_column (self, column: int):
    self.column = column

  def set_line (self, line: int):
    self.line = line
