from rply import LexerGenerator

class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        # print
        self.lexer.add('PRINT', r'print')

        # parentheses
        self.lexer.add('OPEN_PAREN', r'\(')
        self.lexer.add('CLOSE_PAREN', r'\)')

        # semicolon
        self.lexer.add('SEMI_COLON', r'\;')

        # ops
        self.lexer.add('ADD', r'\+')
        self.lexer.add('SUB', r'\-')

        # numbers
        self.lexer.add('NUMBER', r'\d+')

        # ignore whitespaces
        self.lexer.ignore(r'\s+')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
