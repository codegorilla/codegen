from co import st

class SymbolTable:

  def __init__ (self):
    self.table: dict[str, st.Symbol] = {}
    self.enclosingScope: 'SymbolTable' = None

  def define (self, symbol: st.Symbol):
    self.table[symbol.name] = symbol

  def lookup (self, name: str) -> st.Symbol:
    return self.table[name]

  def setEnclosingScope (self, scope: 'SymbolTable'):
    self.enclosingScope = scope
