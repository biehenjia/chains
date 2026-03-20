import ast 


def e(src):
    return ast.parse(src, mode="eval").body

def s(src):
    return ast.parse(src, mode="single").body[0]

def rload(reg, idx):
    return ast.Subscript(value=e(reg), slice=e(str(idx)), ctx=ast.Load())

def rstore(reg, idx):
    return ast.Subscript(value= e(reg), slice=e(str(idx)), ctx=ast.Store())

def rmov(reg, dst, src):
    return ast.Assign([rstore(reg,dst)], rload(reg,src))

class Block:
    def __init__(self):
        self.smts = []

    def __iadd__(self, x):
        self.stmts.extend(flatten(x) if isinstance(x, list) else [x])

    def let(self, name, expr):
        self.stmts.append(ast.Assign([e(name)], e(expr) if isinstance(expr, str) else expr))
        return self
    
    def set(self, target, expr):
        self.stmts.append(ast.Assign([target], e(expr) if isinstance(expr, str) else expr))
    
    def for_range(self, var, stop, body_fn):
        b = Block()
        body_fn(b)
        self.stmts.append(ast.For(
            target = ast.Name(var, ast.Store()),
            iter = e(f"range({stop})"),
            body = b.stmts or [ast.Pass()],
            orelse = [],
        ))
        return self
    
    def ret(self, expr):
        self.stmts.append(ast.Return(e(expr) if isinstance(expr,str) else expr))
    
    def build(self):
        return self.stmts 
    

def fn(name, args, body):
    return ast.FunctionDef(
        name,
        ast.arguments(
            posonlyargs=[], args = [ast.arg(a) for a in args], vararg = None, kwonlyargs=[],
            kw_defaults=[], kwarg = None, defaults = []
        ),
        flatten(body) or [ast.Pass()], [], None,
    )

def mod(*items, numpy=True):
    imports = [ast.Import([ast.alias("numpy")])] if numpy else [ast.ImportFrom("math", [ast.alias("*"), 0])]
    m = ast.Module([*imports, *items], [] )
    ast.fix_missing_locations(m)
    return m

def emit(m): 
    return ast.unparse(m)

def flatten(x):
    out = []
    for item in (x if isinstance(x, list) else [x]):
        if item is None: continue
        out.extend(flatten(item) if isinstance(item, list) else [item])
    return out 
