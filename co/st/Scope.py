from co.st.Symbol import Symbol
from co.st.SymbolTable import SymbolTable

class Scope:

  def __init__ (self, kind: str = ''):
    self.kind = kind
    self.table: SymbolTable = SymbolTable()
    self.enclosing_scope: 'Scope' = None

  def define (self, symbol: Symbol):
    self.table.insert(symbol)

  def is_defined (self, name: str) -> bool:
    if self.resolve(name, False):
      return True
    else:
      return False

  def resolve (self, name: str, recurse: bool = True) -> Symbol:
    # Recurse through scope stack, looking for symbol
    symbol = self.table.lookup(name)
    if symbol == None and recurse == True and self.enclosing_scope != None:
      symbol = self.enclosing_scope.resolve(name)
    return symbol

  def set_enclosing_scope (self, scope: 'Scope'):
    self.enclosing_scope = scope
