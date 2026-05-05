import sympy, numba, numpy, numexpr, ast, pycr, inspect
from pycr.codegen import api 
from bench import benchmark

class Testcase:

    def __init__(self, expr):
        self.expr = expr
        self.s_expr = sympy.sympify(expr)
        self.symbols = sorted(list(map(lambda x: x.name, self.s_expr.free_symbols)))

    def compile_scalar(self, n):
        index = ','.join(self.symbols)
        inner = api.s(f"A[{index}] = {self.expr}")
        
        for i in range(len(self.symbols)):
            outer = api.Block()
            outer.for_range(self.symbols[i],n,inner)
            inner = outer
        
        tree = api.mod(api.fn("generated",["A"], inner.stmts ),numpy=False)
        ast.fix_missing_locations(tree)
        return api.compile_ast(tree)
    
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
        inner = api.s(f"A[{index}] = {self.expr}")
        for i in range(len(self.symbols)-1):
            outer = api.Block()
            outer.for_range(self.symbols[i],n,inner)
            inner = outer
        block = api.Block()
        block.for_range(self.symbols[-1],n,inner, range="prange")
        tree = api.mod(api.fn("generated",["A"], block.stmts ),numpy=False)
        print(ast.unparse(tree))
        ast.fix_missing_locations(tree)
        return numba.njit(api.compile_ast(tree),parallel=True)

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
        m = g.generate_test(n)
        # print(ast.unparse(m))
        f = pycr.compile_ast(m)
        return f
    
    def _compile_prpycr(self, n, p=False):
        cr, symbol_table = pycr.chainify(self.expr)
        ir = pycr.IR(cr, symbol_table)
        g = pycr.Generator(ir)
        m = g.generate_testparallel(n)
        if p:
            print(ast.unparse(m))
        f = pycr.compile_ast(m)
        return f
    
    def compile_npycr(self, n):
        return numba.njit(self.compile_pycr(n))
    
    def compile_nprpycr(self, n, p = False):
        return numba.njit(self._compile_prpycr(n,p),parallel=True)
    
    # gets all of the functions into a list
    def getall(self, n,r=2):
        fs = [
            self.compile_nprpycr,
              self.compile_npycr, 
            #   self.compile_pycr,
              self.compile_numba,
            #   self.compile_scalar,
            #   self.compile_numexpr,
              self.compile_numpy,
              self.compile_prange
              ]
        funcs = {}
        times = [[] for i in range(len(fs))]
        res = {}
        for i in range(len(fs)):
            funcs[fs[i].__name__] = benchmark(times[i],repeats=r)(fs[i](n))
            res[fs[i].__name__] = times[i]
        return funcs, res 
        
            
# thing = "x**2"
# tc = Testcase(thing)
# f = tc.compile_nprpycr(5,p=True)
        


    
    













        







        
        



    

    

    


