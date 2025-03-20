from llvmlite import ir
from rply import ParserGenerator
from syntaxtree import Number, Add, Sub, Mul, Div, Print, Declaration, Identifier

class Parser():
    def __init__(self, module, builder, printf):
        self.pg = ParserGenerator(
            ['PRINT',
             'IDENTIFIER',
             'ASSIGN', 'ADD_ASSIGN', 'SUB_ASSIGN', 'MUL_ASSIGN', 'DIV_ASSIGN',
             #'IF', 'ELIF', 'ELSE',
             'NUMBER',
             'OPEN_PAREN', 'CLOSE_PAREN',
             'ADD', 'SUB', 'MUL', 'DIV',
             'SEMI_COLON',
             'NUMBER_TYPE'],
            precedence=[
                ('left', ['ADD', 'SUB']),
                ('left', ['MUL', 'DIV']),
                ('nonassoc', ['OPEN_PAREN', 'CLOSE_PAREN'])
            ]
        )

        self.module = module
        self.builder: ir.IRBuilder = builder
        self.printf = printf
        
        self.symbol_table = {}

    def parse(self):
        @self.pg.production('program : program statement SEMI_COLON')
        def program_recursive(p):
            program_list = p[0]
            program_list.append(p[1])
            return program_list
        
        @self.pg.production('program : statement SEMI_COLON')
        def program_base(p):
            return [p[0]]
        
        @self.pg.production('statement : declaration')
        @self.pg.production('statement : assignment')
        @self.pg.production('statement : print_stmt')
        #@self.pg.production('statement : if_stmt')
        #@self.pg.production('statement : while_stmt')
        def statement(p):
            return p[0]
        
        @self.pg.production('declaration : NUMBER_TYPE IDENTIFIER ASSIGN expression')
        def declaration(p):
            var_type, var_name, _, expr = p
            
            if var_type.gettokentype() == 'NUMBER_TYPE':
                llvm_type = ir.DoubleType()
            else:
                raise ValueError(f'Unsupported type: {var_type}')
            
            var_ptr = self.builder.alloca(llvm_type, name=var_name.getstr())
            self.symbol_table[var_name.getstr()] = var_ptr
            return Declaration(self.builder, self.module, var_ptr, expr)
        
        @self.pg.production('assignment : IDENTIFIER ASSIGN expression')
        @self.pg.production('assignment : IDENTIFIER ADD_ASSIGN expression')
        @self.pg.production('assignment : IDENTIFIER SUB_ASSIGN expression')
        @self.pg.production('assignment : IDENTIFIER MUL_ASSIGN expression')
        @self.pg.production('assignment : IDENTIFIER DIV_ASSIGN expression')
        def assignment(p):
            var_name, assign_op, expr = p

            if var_name.getstr() not in self.symbol_table:
                raise ValueError(f'Variable {var_name.getstr()} is not defined')
            
            var_ptr = self.symbol_table[var_name.getstr()]
            var_val = self.builder.load(var_ptr)
            new_val = expr.eval()

            if assign_op.gettokentype() == 'ASSIGN':
                res = new_val
            elif assign_op.gettokentype() == 'ADD_ASSIGN':
                res = self.builder.fadd(var_val, new_val)
            elif assign_op.gettokentype() == 'SUB_ASSIGN':
                res = self.builder.fsub(var_val, new_val)
            elif assign_op.gettokentype() == 'MUL_ASSIGN':
                res = self.builder.fmul(var_val, new_val)
            elif assign_op.gettokentype() == 'DIV_ASSIGN':
                res = self.builder.fdiv(var_val, new_val)
            else:
                raise ValueError(f'Unsupported assignment operator: {assign_op.getstr()}')
            
            self.builder.store(res, var_ptr)
            return res
        
        @self.pg.production('print_stmt : PRINT OPEN_PAREN expression CLOSE_PAREN')
        def print_stmt(p):
            return Print(self.builder, self.module, self.printf, p[2])

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

            raise ValueError(f'Unsupported assignment operator: {operator.getstr()}')
                
        @self.pg.production('expression : OPEN_PAREN expression CLOSE_PAREN')
        def expression_parentheses(p):
            return p[1]
        
        @self.pg.production('expression : IDENTIFIER')
        @self.pg.production('expression : NUMBER')
        def number(p):
            terminal = p[0]
            if terminal.gettokentype() == 'NUMBER':
                return Number(self.builder, self.module, terminal.value)
            elif terminal.gettokentype() == 'IDENTIFIER':
                var_ptr = self.symbol_table[terminal.getstr()]
                return Identifier(self.builder, self.module, var_ptr)
            
            raise ValueError(f'Invalid expression: {terminal.getstr()}')

        @self.pg.error
        def error_handle(token):
            raise ValueError(token)

    def get_parser(self):
        return self.pg.build()
