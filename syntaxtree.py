from llvmlite import ir

class BaseBuilder:
    def __init__(self, builder, module):
        self.builder: ir.IRBuilder = builder
        self.module = module

"""
Data types
- 64-bit double
"""
class Number(BaseBuilder):
    def __init__(self, builder, module, value):
        super().__init__(builder, module)
        self.value = value

    def eval(self):
        return ir.Constant(ir.DoubleType(), float(self.value))
    
"""
Identifier
"""
class Identifier(BaseBuilder):
    def __init__(self, builder, module, var_ptr):
        super().__init__(builder, module)
        self.var_ptr = var_ptr

    def eval(self):
        return self.builder.load(self.var_ptr)
    
"""
Variable declaration
"""
class Declaration(BaseBuilder):
    def __init__(self, builder, module, var_ptr, expr):
        super().__init__(builder, module)
        self.var_ptr = var_ptr
        self.expr = expr

    def eval(self):
        var_val = self.expr.eval()
        self.builder.store(var_val, self.var_ptr)

"""
Binary operations
- Addition
- Subtraction
- Multiplication
- Division
"""
class BinaryOp(BaseBuilder):
    def __init__(self, builder, module, left, right):
        super().__init__(builder, module)
        self.left = left
        self.right = right

class Add(BinaryOp):
    def eval(self):
        return self.builder.fadd(self.left.eval(), self.right.eval())

class Sub(BinaryOp):
    def eval(self):
        return self.builder.fsub(self.left.eval(), self.right.eval())
    
class Mul(BinaryOp):
    def eval(self):
        return self.builder.fmul(self.left.eval(), self.right.eval())
    
class Div(BinaryOp):
    def eval(self):
        return self.builder.fdiv(self.left.eval(), self.right.eval())

"""
Print utility function
"""
class Print(BaseBuilder):
    _global_fmt = None

    def __init__(self, builder, module, printf, value):
        super().__init__(builder, module)
        self.printf = printf
        self.value = value

        if Print._global_fmt is None:
            fmt = "%f\n\0"
            c_fmt = ir.Constant(ir.ArrayType(ir.IntType(8), len(fmt)),
                                bytearray(fmt.encode("utf8")))
            global_fmt = ir.GlobalVariable(self.module, c_fmt.type, name="fstr")
            global_fmt.linkage = 'internal'
            global_fmt.global_constant = True
            global_fmt.initializer = c_fmt
            Print._global_fmt = global_fmt

    def eval(self):
        value = self.value.eval()

        voidptr_ty = ir.IntType(8).as_pointer()
        fmt_arg = self.builder.bitcast(Print._global_fmt, voidptr_ty)
        self.builder.call(self.printf, [fmt_arg, value])
