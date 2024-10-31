from enum import Enum
from typing import List
from co import reader

class State (Enum):

  BIN_START = 2000
  BIN_ERROR = 2001
  BIN_100   = 2100
  BIN_200   = 2200
  BIN_300   = 2300
  BIN_400   = 2400
  BIN_500   = 2500
  BIN_600   = 2600
  BIN_700   = 2700
  BIN_800   = 2800

  OCT_START = 3000
  OCT_ERROR = 3001
  OCT_100   = 3100
  OCT_200   = 3200
  OCT_300   = 3300
  OCT_400   = 3400
  OCT_500   = 3500
  OCT_600   = 3600
  OCT_700   = 3700
  OCT_800   = 3800

  HEX_START = 4000
  HEX_ERROR = 4001
  HEX_10    = 4010
  HEX_20    = 4020
  HEX_30    = 4030
  HEX_100   = 4100
  HEX_200   = 4200
  HEX_210   = 4210
  HEX_220   = 4220
  HEX_230   = 4230
  HEX_300   = 4300
  HEX_400   = 4400
  HEX_500   = 4500
  HEX_600   = 4600
  HEX_700   = 4700
  HEX_800   = 4800
  HEX_810   = 4810
  HEX_820   = 4820

  NUM_START = 6000
  NUM_ERROR = 6001
  NUM_100   = 6100
  NUM_200   = 6200
  NUM_210   = 6210
  NUM_220   = 6220
  NUM_230   = 6230
  NUM_300   = 6300
  NUM_400   = 6400
  NUM_500   = 6500
  NUM_600   = 6600
  NUM_700   = 6700
  NUM_800   = 6800
  NUM_810   = 6810
  NUM_820   = 6820


keyword_lookup = {
  'and': 'AND',
  'break': 'BREAK',
  'case': 'CASE',
  'catch': 'CATCH',
  'class': 'CLASS',
  'const': 'CONST',
  'continue': 'CONTINUE',
  'def': 'DEF',
  'default': 'DEFAULT',
  'delete': 'DELETE',
  'do': 'DO',
  'else': 'ELSE',
  'end': 'END',
  'enum': 'ENUM',
  'extends': 'EXTENDS',
  'for': 'FOR',
  'foreach': 'FOREACH',
  'fun': 'FUN',
  'if': 'IF',
  'or': 'OR',
  'return': 'RETURN',
  'then': 'THEN',
  'val': 'VAL',
  'var': 'VAR',
  'while': 'WHILE',

  'void': 'VOID',
  'bool': 'BOOL',
  'double': 'DOUBLE',
  'float': 'FLOAT',
  'char': 'CHAR',
  'int': 'INT'
}

class Lexer:

  def __init__ (self):
    self.input: str = ""
    self.current: str = 'EOF'
    self.position: int = 0
    self.start: int = 0
    self.end: int = 0
    self.line: int = 0
    self.column: int = 0

  def setInput (self, input: str):
    self.input = input
    if len(self.input) > 0:
      self.current = self.input[self.position]

  def error (self, message):
    coords = f"({self.line},{self.column})"
    print(f"{coords}: error: {message}")

  def consume (self):
    self.position += 1
    self.column += 1
    if self.position < len(self.input):
      self.current = self.input[self.position]
    else:
      self.current = 'EOF'

  def backup (self):
    self.position -= 1
    self.column -=1
    self.current = self.input[self.position]

  def is_bin_digit (self, char: str) -> bool:
    return (char == '0' or char == '1')

  def is_oct_digit (self, char: str) -> bool:
    OCT_DIGITS = [ '0', '1', '2', '3', '4', '5', '6', '7' ]
    return (char in OCT_DIGITS)

  def is_dec_digit (self, char: str) -> bool:
    DEC_DIGITS = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9' ]
    return (char in DEC_DIGITS)

  def is_hex_digit (self, char: str) -> bool:
    HEX_DIGITS = [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 
                   'A', 'B', 'C', 'D', 'E', 'F', 'a', 'b', 'c', 'd', 'e', 'f' ]
    return (char in HEX_DIGITS)

  def getToken (self) -> reader.Token:
    while self.current != 'EOF':
      match self.current:

        case '=':
          self.consume()
          if self.current == '=':
            self.consume()
            return reader.Token('EQUAL_EQUAL', '==', self.line, self.column)
          else:
            return reader.Token('EQUAL', '=', self.line, self.column)

        case '|':
          self.consume()
          if self.current == '|':
            self.consume()
            return reader.Token('BAR_BAR', '||', self.line, self.column)
          elif self.current == '=':
            self.consume()
            return reader.Token('BAR_EQUAL', '|=', self.line, self.column)
          else:
            return reader.Token('BAR', '|', self.line, self.column)

        case '^':
          self.consume()
          if self.current == '=':
            self.consume()
            return reader.Token('CARAT_EQUAL', '^=', self.line, self.column)
          else:
            return reader.Token('CARAT', '^', self.line, self.column)

        case '&':
          self.consume()
          if self.current == '&':
            self.consume()
            return reader.Token('AMPERSAND_AMPERSAND', '&&', self.line, self.column)
          elif self.current == '=':
            self.consume()
            return reader.Token('AMPERSAND_EQUAL', '&=', self.line, self.column)
          else:
            return reader.Token('AMPERSAND', '&', self.line, self.column)

        case '>':
          self.consume()
          if self.current == '>':
            self.consume()
            if self.current == '=':
              self.consume()
              return reader.Token('GREATER_GREATER_EQUAL', '>>=', self.line, self.column)
            else:
              return reader.Token('GREATER_GREATER', '>>', self.line, self.column)
          elif self.current == '=':
            self.consume()
            return reader.Token('GREATER_EQUAL', '>=', self.line, self.column)
          else:
            return reader.Token('GREATER', '>', self.line, self.column)

        case '<':
          self.consume()
          if self.current == '<':
            self.consume()
            if self.current == '=':
              return reader.Token('LESS_LESS_EQUAL', '<<=', self.line, self.column)
            else:
              return reader.Token('LESS_LESS', '<<', self.line, self.column)
          elif self.current == '=':
            self.consume()
            return reader.Token('LESS_EQUAL', '<=', self.line, self.column)
          else:
            return reader.Token('LESS', '<', self.line, self.column)

        case '+':
          self.consume()
          if self.current == '=':
            self.consume()
            return reader.Token('PLUS_EQUAL', '+=', self.line, self.column)
          else:
            return reader.Token('PLUS', '+', self.line, self.column)

        case '-':
          self.consume()
          if self.current == '>':
            self.consume()
            return reader.Token('MINUS_GREATER', '->', self.line, self.column)
          elif self.current == '=':
            self.consume()
            return reader.Token('MINUS_EQUAL', '-=', self.line, self.column)
          else:
            return reader.Token('MINUS', '-', self.line, self.column)

        case '*':
          self.consume()
          if self.current == '=':
            self.consume()
            return reader.Token('ASTERISK_EQUAL', '*=', self.line, self.column)
          else:
            return reader.Token('ASTERISK', '*', self.line, self.column)

        case '/':
          self.consume()
          if self.current == '=':
            self.consume()
            return reader.Token('SLASH_EQUAL', '/=', self.line, self.column)
          elif self.current == '*':
            # Block comment
            self.consume()
            comment_done = False
            while not comment_done:
              while self.current != '*' and self.current != 'EOF':
                self.consume()
              while self.current == '*':
                self.consume()
              if self.current == '/':
                self.consume()
                comment_done = True
              elif self.current == 'EOF':
                # Error - comment not closed
                print("error: comment not closed")
                comment_done = True
          elif self.current == '/':
            # Line comment
            self.consume()
            while self.current != '\n' and self.current != '\r' and self.current != 'EOF':
              self.consume()
          else:
            return reader.Token('SLASH', '/', self.line, self.column)

        case '%':
          self.consume()
          if self.current == '=':
            self.consume()
            return reader.Token('PERCENT_EQUAL', '%=', self.line, self.column)
          else:
            return reader.Token('PERCENT', '%', self.line, self.column)

        case '!':
          self.consume()
          if self.current == '=':
            self.consume()
            return reader.Token('EXCLAMATION_EQUAL', '!=', self.line, self.column)
          else:
            return reader.Token('EXCLAMATION', '!', self.line, self.column)

        case '~':
          self.consume()
          if self.current == '=':
            self.consume()
            return reader.Token('TILDE', '!=', self.line, self.column)
          else:
            return reader.Token('TILDE_EQUAL', '!', self.line, self.column)

        case '"':
          # String
          begin = self.position
          self.consume()
          while self.current != '"' and self.current != 'EOF':
            self.consume()
          if self.current == '"':
            self.consume()
            end = self.position
            value = self.input[begin:end]
            return reader.Token('STRING_LITERAL', value, self.line, self.column)
          elif self.current == 'EOF':
            # Todo: Probably should pretend the terminator is there and return token
            print("error: missing string terminator")

        case '\'':
          # Character
          begin = self.position
          self.consume()
          while self.current != '\'' and self.current != 'EOF':
            self.consume()
          if self.current == '\'':
            self.consume()
            end = self.position
            value = self.input[begin:end]
            return reader.Token('CHARACTER_LITERAL', value, self.line, self.column)
          elif self.current == 'EOF':
            # Todo: Probably should pretend the terminator is there and return token
            print("error: missing character terminator")

        case ':':
          self.consume()
          return reader.Token('COLON', ':', self.line, self.column)

        case ';':
          self.consume()
          return reader.Token('SEMICOLON', ';', self.line, self.column)

        case '.':
          self.consume()
          if self.current == '.':
            self.consume()
            return reader.Token('PERIOD_PERIOD', '..', self.line, self.column)
          elif self.is_dec_digit(self.current):
            return self.number() 
          else:
            return reader.Token('PERIOD', '.', self.line, self.column)

        case ',':
          self.consume()
          return reader.Token('COMMA', ',', self.line, self.column)

        case '{':
          self.consume()
          return reader.Token('L_BRACE', '{', self.line, self.column)

        case '}':
          self.consume()
          return reader.Token('R_BRACE', '}', self.line, self.column)

        case '[':
          self.consume()
          return reader.Token('L_BRACKET', '[', self.line, self.column)

        case ']':
          self.consume()
          return reader.Token('R_BRACKET', ']', self.line, self.column)

        case '(':
          self.consume()
          return reader.Token('L_PARENTHESIS', '(', self.line, self.column)

        case ')':
          self.consume()
          return reader.Token('R_PARENTHESIS', ')', self.line, self.column)

        case '0':
          self.consume()
          if self.current == 'b':
            self.backup()
            return self.binary_integer()
          elif self.current == 'o':
            self.backup()
            return self.octal_integer()
          elif self.current == 'x':
            self.backup()
            return self.hexadecimal_number()
          else:
            self.backup()
            return self.number()

        case ' ' | '\t':
          # Skip spaces and tabs
          while self.current == ' ' or self.current == '\t':
            self.consume()

        case '\n':
          # Skip line feeds (LF)
          while self.current == '\n':
            self.consume()
            self.line += 1
            self.column = 0

        case '\r':
          # Skip carriage return + line feed pairs (CR+LF)
          while self.current == '\r':
            self.consume()
            if self.current == '\n':
              self.consume()
              self.line += 1
              self.column = 0
            else:
              # Should return an error token here maybe
              print("ERROR")

        case _:
          if self.current.isalpha() or self.current == '_':
            begin = self.position
            self.consume()
            # Todo: The end should occur before the consume
            while self.current.isalpha() or self.current.isdigit() or self.current == '_':
              self.consume()
            end = self.position
            id = self.input[begin:end]
            if id in keyword_lookup.keys():
              return reader.Token(keyword_lookup[id], id, self.line, self.column)
            else:
              return reader.Token('IDENTIFIER', id, self.line, self.column)
          elif self.current.isdigit():
            return self.number()
          else:
            print("ERROR")

    return reader.Token('EOF', '', self.line, self.column)

  def binary_integer (self) -> reader.Token:
    # Note: We arrive at this function after lookahead or
    # backtracking, so we really should never fail to match the '0b'
    # portion, unless there is a bug in this program.
    begin = self.position
    state = State.BIN_START
    while True:
      match state:
        case State.BIN_START:
          if self.current == '0':
            self.consume()
            state = State.BIN_100
          else:
            state = State.BIN_ERROR
        case State.BIN_100:
          if self.current == 'b':
            self.consume()
            state = State.BIN_200
          else:
            state = State.BIN_ERROR
        case State.BIN_200:
          if self.is_bin_digit(self.current):
            self.consume()
            state = State.BIN_400
          elif self.current == '_':
            self.consume()
            state = State.BIN_300
          else:
            # Pretend we got an underscore or digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected underscore or binary digit")
            self.consume()
            state = State.BIN_400
        case State.BIN_300:
          if self.is_bin_digit(self.current):
            self.consume()
            state = State.BIN_400
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected binary digit")
            self.consume()
            state = State.BIN_400
        case State.BIN_400:
          if self.is_bin_digit(self.current):
            self.consume()
          elif self.current == '_':
            self.consume()
            state = State.BIN_500
          elif self.current == 'L':
            self.consume()
            state = State.BIN_600
          elif self.current == 'u':
            self.consume()
            state = State.BIN_700
          else:
            # Accept
            end = self.position
            value = self.input[begin:end]
            return reader.Token('BINARY_INT32', value, self.line, self.column)
        case State.BIN_500:
          if self.is_bin_digit(self.current):
            self.consume()
            state = State.BIN_400
          elif self.current == 'L':
            self.consume()
            state = State.BIN_600
          elif self.current == 'u':
            self.consume()
            state = State.BIN_700            
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected binary digit")
            self.consume()
            state = State.BIN_400
        case State.BIN_600:
          if self.current == 'u':
            self.consume()
            state = State.BIN_800
          else:
            # Accept
            end = self.position
            value = self.input[begin:end]
            return reader.Token('BINARY_INT64', value, self.line, self.column)
        case State.BIN_700:
          if self.current == 'L':
            self.consume()
            state = State.BIN_800
          else:
            # Accept
            end = self.position
            value = self.input[begin:end]
            return reader.Token('BINARY_UINT32', value, self.line, self.column)
        case State.BIN_800:
            # Accept
            end = self.position
            value = self.input[begin:end]
            return reader.Token('BINARY_UINT64', value, self.line, self.column)
        case _:
          # Invalid state. Can only be reached through a lexer bug.
          print("error: Invalid state.")

  def octal_integer (self) -> reader.Token:
    # Note: We arrive at this function after lookahead or
    # backtracking, so we really should never fail to match the '0o'
    # portion, unless there is a bug in this program.
    begin = self.position
    state = State.OCT_START
    while True:
      match state:
        case State.OCT_START:
          if self.current == '0':
            self.consume()
            state = State.OCT_100
          else:
            state = State.OCT_ERROR
        case State.OCT_100:
          if self.current == 'o':
            self.consume()
            state = State.OCT_200
          else:
            state = State.OCT_ERROR
        case State.OCT_200:
          if self.is_oct_digit(self.current):
            self.consume()
            state = State.OCT_400
          elif self.current == '_':
            self.consume()
            state = State.OCT_300
          else:
            # Pretend we got an underscore or digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected underscore or octal digit")
            self.consume()
            state = State.OCT_400
        case State.OCT_300:
          if self.is_oct_digit(self.current):
            self.consume()
            state = State.OCT_400
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected octal digit")
            self.consume()
            state = State.OCT_400
        case State.OCT_400:
          if self.is_oct_digit(self.current):
            self.consume()
          elif self.current == '_':
            self.consume()
            state = State.OCT_500
          elif self.current == 'L':
            self.consume()
            state = State.OCT_600
          elif self.current == 'u':
            self.consume()
            state = State.OCT_700
          else:
            # Accept
            end = self.position
            value = self.input[begin:end]
            return reader.Token('OCTAL_INT32', value, self.line, self.column)
        case State.OCT_500:
          if self.is_oct_digit(self.current):
            self.consume()
            state = State.OCT_400
          elif self.current == 'L':
            self.consume()
            state = State.OCT_600
          elif self.current == 'u':
            self.consume()
            state = State.OCT_700            
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected octal digit")
            self.consume()
            state = State.OCT_400
        case State.OCT_600:
          if self.current == 'u':
            self.consume()
            state = State.OCT_800
          else:
            # Accept
            end = self.position
            value = self.input[begin:end]
            return reader.Token('OCTAL_INT64', value, self.line, self.column)
        case State.OCT_700:
          if self.current == 'L':
            self.consume()
            state = State.OCT_800
          else:
            # Accept
            end = self.position
            value = self.input[begin:end]
            return reader.Token('OCTAL_UINT32', value, self.line, self.column)
        case State.OCT_800:
            # Accept
            end = self.position
            value = self.input[begin:end]
            return reader.Token('OCTAL_UINT64', value, self.line, self.column)
        case _:
          # Invalid state. Can only be reached through a lexer bug.
          print("error: Invalid state.")

  def hexadecimal_number (self) -> reader.Token:
    # This scans for a hexadecimal integer or floating point number.
    begin = self.position
    state = State.HEX_START
    while True:
      match state:
        case State.HEX_START:
          if self.current == '0':
            self.consume()
            state = State.HEX_10
          else:
            state = State.HEX_ERROR
        case State.HEX_10:
          if self.current == 'x':
            self.consume()
            state = State.HEX_20
          else:
            state = State.HEX_ERROR
        case State.HEX_20:
          if self.is_hex_digit(self.current):
            self.consume()
            state = State.HEX_100
          elif self.current == '_':
            self.consume()
            state = State.HEX_30
          elif self.current == '.':
            self.consume()
            state = State.HEX_300
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected dot, underscore, or hexadecimal digit")
            self.consume()
            state = State.HEX_100
        case State.HEX_30:
          if self.is_hex_digit(self.current):
            self.consume()
            state = State.HEX_100
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected hexadecimal digit")
            self.consume()
            state = State.HEX_100
        case State.HEX_100:
          if self.is_hex_digit(self.current):
            self.consume()
          elif self.current == '_':
            self.consume()
            state = State.HEX_200
          elif self.current == 'L':
            self.consume()
            state = State.HEX_210
          elif self.current == 'u':
            self.consume()
            state = State.HEX_220
          elif self.current == '.':
            self.consume()
            state = State.HEX_300
          elif self.current == 'p':
            self.consume()
            state = State.HEX_600
          else:
            # Accept
            end = self.position
            value = self.input[begin:end]
            return reader.Token('HEXADECIMAL_INT32', value, self.line, self.column)
        case State.HEX_200:
          if self.is_hex_digit(self.current):
            self.consume()
            state = State.HEX_100
          elif self.current == 'L':
            self.consume()
            state = State.HEX_210
          elif self.current == 'u':
            self.consume()
            state = State.HEX_220
          elif self.current == 'p':
            self.consume()
            state = State.HEX_600
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected 'L', 'u', 'p', or hexadecimal digit")
            self.consume()
            state = State.HEX_100
        case State.HEX_210:
          if self.current == 'u':
            self.consume()
            state = State.HEX_230
          else:
            end = self.position
            value = self.input[begin:end]
            return reader.Token('HEXADECIMAL_INT64', value, self.line, self.column)
        case State.HEX_220:
          if self.current == 'L':
            self.consume()
            state = State.HEX_230
          else:
            end = self.position
            value = self.input[begin:end]
            return reader.Token('HEXADECIMAL_UINT32', value, self.line, self.column)
        case State.HEX_230:
          end = self.position
          value = self.input[begin:end]
          return reader.Token('HEXADECIMAL_UINT64', value, self.line, self.column)
        case State.HEX_300:
          if self.is_hex_digit(self.current):
            self.consume()
            state = State.HEX_400
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected decimal digit")
            self.consume()
        case State.HEX_400:
          if self.is_hex_digit(self.current):
            self.consume()
          elif self.current == '_':
            self.consume()
            state = State.HEX_500
          elif self.current == 'p':
            self.consume()
            state = State.HEX_600
          else:
            end = self.position
            value = self.input[begin:end]
            return reader.Token('HEXADECIMAL_FLOAT64', value, self.line, self.column)
        case State.HEX_500:
          if self.is_hex_digit(self.current):
            self.consume()
            state = State.HEX_400
          elif self.current == 'p':
            self.consume()
            state = State.HEX_600
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected 'p' or hexadecimal digit")
            self.consume()
            state = State.HEX_400
        case State.HEX_600:
          if self.is_dec_digit(self.current):
            self.consume()
            state = State.HEX_800
          elif self.current == '+' or self.current == '-':
            self.consume()
            state = State.HEX_700
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected '+', '-', or decimal digit")
            self.consume()
            state = State.HEX_800
        case State.HEX_700:
          if self.is_dec_digit(self.current):
            self.consume()
            state = State.HEX_800
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected decimal digit")
            self.consume()
            state = State.HEX_800
        case State.HEX_800:
          if self.is_dec_digit(self.current):
            self.consume()
          elif self.current == 'd':
            self.consume()
            state = State.HEX_810
          elif self.current == 'f':
            self.consume()
            state = State.HEX_820
          else:
            end = self.position
            value = self.input[begin:end]
            return reader.Token('HEXADECIMAL_FLOAT64', value, self.line, self.column)
        case State.HEX_810:
          end = self.position
          value = self.input[begin:end]
          return reader.Token('HEXADECIMAL_FLOAT64', value, self.line, self.column)
        case State.HEX_820:
          end = self.position
          value = self.input[begin:end]
          return reader.Token('HEXADECIMAL_FLOAT32', value, self.line, self.column)
        case _:
          # Error - shouldn't be able to get here
          pass

  def number (self) -> reader.Token:
    # This scans for an integer or floating point number.
    begin = self.position
    state = State.NUM_START
    while True:
      match state:
        case State.NUM_START:
          # We are guaranteed to get a digit here unless the lexer
          # has a bug in it.
          if self.is_dec_digit(self.current):
            self.consume()
            state = State.NUM_100
          elif self.current == '.':
            self.consume()
            state = State.NUM_300
          else:
            state = State.NUM_ERROR
        case State.NUM_100:
          if self.is_dec_digit(self.current):
            self.consume()
          elif self.current == '_':
            self.consume()
            state = State.NUM_200
          elif self.current == 'L':
            self.consume()
            state = State.NUM_210
          elif self.current == 'u':
            self.consume()
            state = State.NUM_220
          elif self.current == '.':
            self.consume()
            state = State.NUM_300
          elif self.current == 'e':
            self.consume()
            state = State.NUM_600
          elif self.current == 'd':
            self.consume()
            state = State.NUM_810
          elif self.current == 'f':
            self.consume()
            state = State.NUM_820
          else:
            end = self.position
            value = self.input[begin:end]
            return reader.Token('INT32', value, self.line, self.column)
        case State.NUM_200:
          if self.is_dec_digit(self.current):
            self.consume()
            state = State.NUM_100
          elif self.current == 'e':
            self.consume()
            state = State.NUM_600
          elif self.current == 'd':
            self.consume()
            state = State.NUM_810
          elif self.current == 'f':
            self.consume()
            state = State.NUM_820
          elif self.current == 'L':
            self.consume()
            state = State.NUM_210
          elif self.current == 'u':
            self.consume()
            state = State.NUM_220
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected 'd', 'f', 'e', 'L', 'u', or decimal digit")
            self.consume()
            state = State.NUM_100
        case State.NUM_210:
          if self.current == 'u':
            self.consume()
            state = State.NUM_230
          else:
            end = self.position
            value = self.input[begin:end]
            return reader.Token('INT64', value, self.line, self.column)
        case State.NUM_220:
          if self.current == 'L':
            self.consume()
            state = State.NUM_230
          else:
            end = self.position
            value = self.input[begin:end]
            return reader.Token('UINT32', value, self.line, self.column)
        case State.NUM_230:
          end = self.position
          value = self.input[begin:end]
          return reader.Token('UINT64', value, self.line, self.column)
        case State.NUM_300:
          if self.is_dec_digit(self.current):
            self.consume()
            state = State.NUM_400
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected decimal digit")
            self.consume()
        case State.NUM_400:
          if self.is_dec_digit(self.current):
            self.consume()
          elif self.current == '_':
            self.consume()
            state = State.NUM_500
          elif self.current == 'e':
            self.consume()
            state = State.NUM_600
          elif self.current == 'd':
            self.consume()
            state = State.NUM_810
          elif self.current == 'f':
            self.consume()
            state = State.NUM_820
          else:
            end = self.position
            value = self.input[begin:end]
            return reader.Token('FLOAT64', value, self.line, self.column)
        case State.NUM_500:
          if self.is_dec_digit(self.current):
            self.consume()
            state = State.NUM_400
          elif self.current == 'e':
            self.consume()
            state = State.NUM_600
          elif self.current == 'd':
            self.consume()
            state = State.NUM_810
          elif self.current == 'f':
            self.consume()
            state = State.NUM_820
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected decimal digit")
            self.consume()
            state = State.NUM_400
        case State.NUM_600:
          if self.is_dec_digit(self.current):
            self.consume()
            state = State.NUM_800
          elif self.current == '+' or self.current == '-':
            self.consume()
            state = State.NUM_700
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected '+', '-', or decimal digit")
            self.consume()
            state = State.NUM_800
        case State.NUM_700:
          if self.is_dec_digit(self.current):
            self.consume()
            state = State.NUM_800
          else:
            # Pretend we got a digit for error recovery purposes
            self.error(f"invalid number: found '{self.current}', expected decimal digit")
            self.consume()
            state = State.NUM_800
        case State.NUM_800:
          if self.is_dec_digit(self.current):
            self.consume()
          elif self.current == 'd':
            self.consume()
            state = State.NUM_810
          elif self.current == 'f':
            self.consume()
            state = State.NUM_820
          else:
            end = self.position
            value = self.input[begin:end]
            return reader.Token('FLOAT64', value, self.line, self.column)
        case State.NUM_810:
          end = self.position
          value = self.input[begin:end]
          return reader.Token('FLOAT64', value, self.line, self.column)
        case State.NUM_820:
          end = self.position
          value = self.input[begin:end]
          return reader.Token('FLOAT32', value, self.line, self.column)
        case _:
          # Error - shouldn't be able to get here
          pass
