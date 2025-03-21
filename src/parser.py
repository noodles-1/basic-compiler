from llvmlite import ir
from rply import ParserGenerator
from syntaxtree import Number, Add, Sub, Mul, Div, Print, Declaration, Identifier, Assignment

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
            
            if var_name.getstr() in self.symbol_table:
                raise ValueError(f'Variable {var_name.getstr()} is already defined')
            
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
            var = Identifier(self.builder, self.module, var_ptr)

            if assign_op.gettokentype() == 'ASSIGN':
                res_expr = expr
            elif assign_op.gettokentype() == 'ADD_ASSIGN':
                res_expr = Add(self.builder, self.module, var, expr)
            elif assign_op.gettokentype() == 'SUB_ASSIGN':
                res_expr = Sub(self.builder, self.module, var, expr)
            elif assign_op.gettokentype() == 'MUL_ASSIGN':
                res_expr = Mul(self.builder, self.module, var, expr)
            elif assign_op.gettokentype() == 'DIV_ASSIGN':
                res_expr = Div(self.builder, self.module, var, expr)
            else:
                raise ValueError(f'Unsupported assignment operator: {assign_op.gettokentype()}')
            
            return Assignment(self.builder, self.module, res_expr, var_ptr)
        
        @self.pg.production('print_stmt : PRINT OPEN_PAREN expression CLOSE_PAREN')
        def print_stmt(p):
            return Print(self.builder, self.module, self.printf, p[2])

        @self.pg.production('expression : expression ADD term')
        @self.pg.production('expression : expression SUB term')
        def expression(p):
            left, op, right = p
            if op.gettokentype() == 'ADD':
                return Add(self.builder, self.module, left, right)
            elif op.gettokentype() == 'SUB':
                return Sub(self.builder, self.module, left, right)

            raise ValueError(f'Unsupported assignment operator: {op.getstr()}')
        
        @self.pg.production('expression : term')
        def expression_term(p):
            return p[0]
        
        @self.pg.production('term : term MUL factor')
        @self.pg.production('term : term DIV factor')
        def term(p):
            left, op, right = p
            if op.gettokentype() == 'MUL':
                return Mul(self.builder, self.module, left, right)
            elif op.gettokentype() == 'DIV':
                return Div(self.builder, self.module, left, right)

            raise ValueError(f'Unsupported assignment operator: {op.getstr()}')
        
        @self.pg.production('term : factor')
        def term_factor(p):
            return p[0]
        
        @self.pg.production('factor : SUB factor')
        def unary_negation(p):
            operand = p[1]
            return Sub(self.builder, self.module, Number(self.builder, self.module, 0), operand)
                
        @self.pg.production('factor : OPEN_PAREN expression CLOSE_PAREN')
        def expression_parentheses(p):
            return p[1]
        
        @self.pg.production('factor : IDENTIFIER')
        @self.pg.production('factor : NUMBER')
        def expression_terminals(p):
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
