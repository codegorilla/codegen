tokens = [
    'AMPERSAND',
    'ARROW',
    'ASSIGN',
    'ASSIGN_MUL',
    'ASSIGN_DIV',
    'ASSIGN_MOD',
    'ASSIGN_ADD',
    'ASSIGN_SUB',
    'ASSIGN_SHL',
    'ASSIGN_SHR',
    'ASSIGN_AND',
    'ASSIGN_XOR',
    'ASSIGN_OR',
    'ASTERISK',
    'AT',
    'CARAT',
    'COLON',
    'COMMA',
    'DOLLAR',
    'DOUBLE_AMPERSAND',
    'EXCLAMATION',
    'EQU',
    'NEQ',
    'LT',
    'GT',
    'LTE',
    'GTE',
    'MINUS',
    'PERCENT',
    'PIPE',
    'PLUS',
    'SEMICOLON',
    'SHL',
    'SHR',
    'SLASH',
    'L_PARENTHESIS',
    'R_PARENTHESIS',
    'L_BRACE',
    'R_BRACE',
    'L_BRACKET',
    'R_BRACKET',
    'IDENTIFIER',
    'INTEGER',
    'FLOATING',
    'CHARACTER',
    'STRING'
]

reserved1 = {
    'abstract':   'ABSTRACT',
    'and':        'AND',
    'as':         'AS',
    'break':      'BREAK',
    'case':       'CASE',
    'catch':      'CATCH',
    'class':      'CLASS',
    'const':      'CONST',
    'continue':   'CONTINUE',
    'def':        'DEF',
    'default':    'DEFAULT',
    'delete':     'DELETE',
    'do':         'DO',
    'else':       'ELSE',
    'enum':       'ENUM',
    'export':     'EXPORT',
    'fn':         'FN',
    'for':        'FOR',
    'foreach':    'FOREACH',
    'fun':        'FUN',
    'goto':       'GOTO',
    'if':         'IF',
    'in':         'IN',
    'inline':     'INLINE',
    'is':         'IS',
    'lambda':     'LAMBDA',
    'let':        'LET',
    'mod':        'MOD',
    'module':     'MODULE',
    'my':         'MY',
    'namespace':  'NAMESPACE',
    'new':        'NEW',
    'not':        'NOT',
    'or':         'OR',
    'our':        'OUR',
    'private':    'PRIVATE',
    'protected':  'PROTECTED',
    'public':     'PUBLIC',
    'return':     'RETURN',
    'static':     'STATIC',
    'struct':     'STRUCT',
    'switch':     'SWITCH',
    'template':   'TEMPLATE',
    'throw':      'THROW',
    'try':        'TRY',
    'typedef':    'TYPEDEF',
    'union':      'UNION',
    'using':      'USING',
    'var':        'VAR',
    'val':        'VAL',
    'virtual':    'VIRTUAL',
    'when':       'WHEN',
    'while':      'WHILE',
    'yield':      'YIELD'
}

reserved2 = {
    'null':     'NULL',
    'false':    'FALSE',
    'this':     'THIS',
    'true':     'TRUE'
}

reserved3 = {
    'void':     'VOID',
    'bool':     'BOOL',
    'char':     'CHAR',
    'short':    'SHORT',
    'int':      'INT',
    'long':     'LONG',
    'uchar':    'UCHAR',
    'ushort':   'USHORT',
    'uint':     'UINT',
    'ulong':    'ULONG',
    'float':    'FLOAT',
    'double':   'DOUBLE'
}

reserved = reserved1 | reserved2 | reserved3

tokens += list(reserved.values())

# Miscellaneous
t_AMPERSAND   = r'&'
t_ARROW       = r'->'
t_ASTERISK    = r'\*'
t_AT          = r'@'
t_CARAT       = r'\^'
t_COLON       = r':'
t_COMMA       = r','
t_DOLLAR      = r'\$'
t_DOUBLE_AMPERSAND = r'&&'
t_EXCLAMATION = r'!'
t_MINUS       = r'-'
t_PERCENT     = r'%'
t_PIPE        = r'\|'
t_PLUS        = r'\+'
t_SEMICOLON   = r';'
t_SLASH       = r'/'

# Assignment operators
t_ASSIGN     = r'='
t_ASSIGN_MUL = r'\*='
t_ASSIGN_DIV = r'/='
t_ASSIGN_MOD = r'%='
t_ASSIGN_ADD = r'\+='
t_ASSIGN_SUB = r'-='
t_ASSIGN_SHL = r'<<='
t_ASSIGN_SHR = r'>>='
t_ASSIGN_AND = r'&='
t_ASSIGN_XOR = r'^='
t_ASSIGN_OR  = r'\|='

# Equality operators
t_EQU = r'=='
t_NEQ = r'!='

# Relational operators
t_LT  = r'<'
t_GT  = r'>'
t_LTE = r'<='
t_GTE = r'>='

# Shift operators
t_SHL = r'<<'
t_SHR = r'>>'

t_L_PARENTHESIS = r'\('
t_R_PARENTHESIS = r'\)'
t_L_BRACE       = r'\{'
t_R_BRACE       = r'\}'
t_L_BRACKET     = r'\['
t_R_BRACKET     = r'\]'

t_ignore = ' \t'

t_INTEGER = r'\d+([uU]|[lL]|[uU][lL]|[lL][uU])?'

t_FLOATING = r'((\d+)(\.\d+)(e(\+|-)?(\d+))? | (\d+)e(\+|-)?(\d+))([lL]|[fF])?'

t_CHARACTER = r'(L)?\'([^\\\n]|(\\.))*?\''

t_STRING = r'\"([^\\\n]|(\\.))*?\"'

# Block comment
# def t_BLOCK_COMMENT (t: lex.LexToken):
#     r'/\*(.|\n)*?\*/'
#     t.lexer.lineno += t.value.count('\n')

# # Line comment
# def t_LINE_COMMENT (t: lex.LexToken):
#     r'//.*\n'
#     t.lexer.lineno += 1

# def t_ignore_newline (t: lex.LexToken):
#     r'\n+'
#     t.lexer.lineno += t.value.count('\n')

# def t_IDENTIFIER (t: lex.LexToken) -> lex.LexToken:
#     r'[a-zA-Z_][a-zA-Z0-9_]*'
#     t.type = reserved.get(t.value, 'IDENTIFIER')
#     return t

# def t_eof (t: lex.LexToken) -> lex.LexToken:
#     t.type = 'EOF'
#     t.value = '<EOF>'
#     return t

# def t_error (t: lex.LexToken):
#     print(f"Illegal character {t.value[0]}")
#     t.lexer.skip(1)
