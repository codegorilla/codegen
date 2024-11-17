from co.st.Symbol import Symbol

class SymbolTable:

  def __init__ (self):
    self.data: dict[str, Symbol] = {}

  def insert (self, symbol: Symbol):
    self.data[symbol.name] = symbol

  def lookup (self, name: str) -> Symbol:
    return self.data.get(name)
