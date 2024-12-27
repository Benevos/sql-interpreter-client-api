from ply.lex import lex

class SQLLexer:
    tokens = (
        'IDENTIFIER',
        'NUMBER',
        'STRING',
        'COMMA',
        'SEMICOLON',
        'LPAREN',
        'RPAREN',
        'EQUAL',
        'LESS',
        'GREATER',
    )

    t_COMMA     = r'\,'
    t_LESS      = r'\<'
    t_GREATER   = r'\>'
    t_SEMICOLON = r'\;'
    t_EQUAL     = r'\='
    t_RPAREN    = r'\)'
    t_LPAREN    = r'\('

    t_ignore = " \t"

    reserved = {
        'select': 'SELECT',
        'from': 'FROM',
        'insert': 'INSERT',
        'into': 'INTO',
        'values': 'VALUES',
        'update': 'UPDATE',
        'set': 'SET',
        'delete': 'DELETE',
        'where': 'WHERE',
        'and': 'AND',
        'or': 'OR',
        'table': 'TABLE',
        'as': 'AS'
    }

    tokens = list(tokens) + list(reserved.values())

    def __init__(self):
        self.lexer = lex(module=self)

    def t_NUMBER(self, t):
        r'\d+(\.\d+)?'
        t.value = float(t.value)
        return t

    def t_IDENTIFIER(self, t):
        r"[A-Za-z][A-Za-z\d]*|\*"
        keyword = str(t.value).lower()
        if keyword in self.reserved:
            t.type = self.reserved[keyword]
        return t

    def t_STRING(self, t):
        r'\".*\"|\'.*\''
        return t

    def t_error(self, t):
        print(f"<<! ERROR: Illegal character '{t.value[0]}'")
        t.lexer.skip(1)