import sympy, numba, numpy, numexpr, ast, pycr, inspect
from pycr.codegen import dsl 
from bench import benchmark

class Generator:

    def __init__(self, expr):
        self.expr = expr
        self.s_expr = sympy.sympify(expr)
        self.symbols = sorted(list(map(lambda x: x.name, self.s_expr.free_symbols)))

    def compile_scalar(self, n):
        index = ','.join(self.symbols)
        inner = dsl.s(f"A[{index}] = {self.expr}")
        
        for i in range(len(self.symbols)):
            outer = dsl.Block()
            outer.for_range(self.symbols[i],n,inner)
            inner = outer
        
        tree = dsl.mod(dsl.fn("generated",["A"], inner.stmts ),numpy=False)
        ast.fix_missing_locations(tree)
        return dsl.compile_ast(tree)
    
    def compile_numba(self, n):
        return numba.njit(self.compile_scalar(n))
    
    def compile_numpy(self, n):
        f = sympy.lambdify(self.symbols, self.s_expr, modules="numpy")
        grids = numpy.meshgrid(*[numpy.arange(n) for _ in self.symbols], indexing='ij')
        
        def _grid(A):
            A[:] = f(*grids)
            return A
        
        return _grid
    
    def compile_prange(self, n):
        index = ','.join(self.symbols)
        inner = dsl.s(f"A[{index}] = {self.expr}")
        

        for i in range(len(self.symbols)-1):
            outer = dsl.Block()
            outer.for_range(self.symbols[i],n,inner)
            inner = outer
        block = dsl.Block()
        block.for_range(self.symbols[-1],n,inner, range="prange")
        tree = dsl.mod(dsl.fn("generated",["A"], block.stmts ),numpy=False)
        print(ast.unparse(tree))
        ast.fix_missing_locations(tree)
        return dsl.compile_ast(tree)

    def compile_numexpr(self, n ):
        grids = {s: numpy.arange(n) for s in self.symbols}  # 1D, not meshgrid
        expr_str = str(self.s_expr)


        def _grid(A):
            A[:] = numexpr.evaluate(expr_str, local_dict=grids)
            return A
        
        return _grid
    
    def compile_pycr(self, n):
        cr, symbol_table = pycr.chainify(self.expr)
        kwargs = {f"{v}_0": 0 for v in self.symbols} | {f"{v}_h":1 for v in self.symbols} | {f"B_{i}":n for i in range(len(self.symbols))}
        ir = pycr.IR(cr, symbol_table)
        g = pycr.Generator(ir)
        m = g.generate()
        print(ast.unparse(m))
        f = pycr.compile_ast(m)
        return lambda A: f(A,**kwargs)
    
    
    
expr = "x**2+(0.5)*sin(45*y)"
g = Generator(expr)
s = g.compile_pycr(10)
A = numpy.zeros((10,10),dtype=numpy.float32)
s(A)
print(A)







        







        
        



    

    

    


