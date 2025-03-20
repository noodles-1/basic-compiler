from rply import LexerGenerator
import re

class Lexer():
    def __init__(self):
        self.lexer = LexerGenerator()

    def _add_tokens(self):
        # print
        self.lexer.add('PRINT', r'print')

        # parentheses
        self.lexer.add('OPEN_PAREN', r'\(')
        self.lexer.add('CLOSE_PAREN', r'\)')

        # braces
        self.lexer.add('OPEN_BRACE', r'\{')
        self.lexer.add('CLOSE_BRACE', r'\}')

        # semicolon
        self.lexer.add('SEMI_COLON', r'\;')

        # ops assign
        self.lexer.add('ADD_ASSIGN', r'\+=')
        self.lexer.add('SUB_ASSIGN', r'-=')
        self.lexer.add('MUL_ASSIGN', r'\*=')
        self.lexer.add('DIV_ASSIGN', r'/=')

        # ops
        self.lexer.add('ADD', r'\+')
        self.lexer.add('SUB', r'-')
        self.lexer.add('MUL', r'\*')
        self.lexer.add('DIV', r'/')

        # rel ops
        self.lexer.add('EQUALS_REL', r'==')
        self.lexer.add('NOT_EQUALS_REL', r'!=')
        self.lexer.add('LESS_THAN_REL', r'<')
        self.lexer.add('GREATER_THAN_REL', r'>')
        self.lexer.add('LESS_THAN_EQUALS_REL', r'<=')
        self.lexer.add('GREATER_THAN_EQUALS_REL', r'>=')

        # assign
        self.lexer.add('ASSIGN', r'=')

        # conditions
        self.lexer.add('IF', r'if')
        self.lexer.add('ELIF', r'elif')
        self.lexer.add('ELSE', r'else')
        
        # loop conditions
        self.lexer.add('WHILE', r'while')

        # logical conditions
        self.lexer.add('LOGICAL_OR', r'\|\|')
        self.lexer.add('LOGICAL_AND', r'\&\&')

        # data types
        self.lexer.add('NUMBER_TYPE', r'number')

        # identifiers
        self.lexer.add('IDENTIFIER', r'[a-zA-Z_][a-zA-Z0-9_]*')

        # values
        self.lexer.add('NUMBER', r'\d+(\.\d+)?')
        self.lexer.add('STRING', r'"([^"\\]*(\\.[^"\\]*)*)*"', re.DOTALL)

        # ignore single-line comments
        self.lexer.ignore(r'//.*')

        # ignore multi-line comments
        self.lexer.ignore(r'/\*[\s\S]*?\*/')

        # ignore whitespaces
        self.lexer.ignore(r'\s+')

    def get_lexer(self):
        self._add_tokens()
        return self.lexer.build()
