from lexer import Lexer
from parser import Parser
from codegen import CodeGen

fname = "input.foo"
with open(fname) as f:
    text_input = f.read()

lexer = Lexer().get_lexer()
tokens = lexer.lex(text_input)

codegen = CodeGen()

module = codegen.module
builder = codegen.builder
printf = codegen.printf

pg = Parser(module, builder, printf)
pg.parse()
parser = pg.get_parser()
parsed_stmts = parser.parse(tokens)

for stmt in parsed_stmts:
    stmt.eval()

codegen.create_ir()
codegen.save_ir("output.ll")