from rply import ParserGenerator
from syntaxtree import Number, Add, Sub, Mul, Div, Print

class Parser():
    def __init__(self, module, builder, printf):
        self.pg = ParserGenerator(
            ['PRINT',
             'NUMBER',
             'OPEN_PAREN', 'CLOSE_PAREN',
             'ADD', 'SUB', 'MUL', 'DIV',
             'SEMI_COLON'],
            precedence=[
                ('left', ['ADD', 'SUB']),
                ('left', ['MUL', 'DIV']),
                ('nonassoc', ['OPEN_PAREN', 'CLOSE_PAREN'])
            ]
        )
        self.module = module
        self.builder = builder
        self.printf = printf

    def parse(self):
        @self.pg.production('program : PRINT OPEN_PAREN expression CLOSE_PAREN SEMI_COLON')
        def program(p):
            return Print(self.builder, self.module, self.printf, p[2])
        
        @self.pg.production('expression : OPEN_PAREN expression CLOSE_PAREN')
        def expression_parentheses(p):
            return p[1]

        @self.pg.production('expression : expression ADD expression')
        @self.pg.production('expression : expression SUB expression')
        @self.pg.production('expression : expression MUL expression')
        @self.pg.production('expression : expression DIV expression')
        def expression(p):
            left = p[0]
            right = p[2]
            operator = p[1]
            if operator.gettokentype() == 'ADD':
                return Add(self.builder, self.module, left, right)
            elif operator.gettokentype() == 'SUB':
                return Sub(self.builder, self.module, left, right)
            elif operator.gettokentype() == 'MUL':
                return Mul(self.builder, self.module, left, right)
            elif operator.gettokentype() == 'DIV':
                return Div(self.builder, self.module, left, right)

        @self.pg.production('expression : NUMBER')
        def number(p):
            num = p[0]
            return Number(self.builder, self.module, num.value)

        @self.pg.error
        def error_handle(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
