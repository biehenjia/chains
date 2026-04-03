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
        self.stmts = []

    def __iadd__(self, x):
        if isinstance(x, Block):
            self.stmts.extend(x.stmts)
        elif isinstance(x, list):
            self.stmts.extend(flatten(x))
        else:
            self.stmts.append(x)
        return self


    def for_range(self, var, stop, body, range = "range"):
        stmts = body.stmts if isinstance(body, Block) else flatten(body)
        self.stmts.append(ast.For(
            target=ast.Name(var, ast.Store()),
            iter=e(f"{range}({stop})"),
            body=stmts or [ast.Pass()],
            orelse=[],
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
    imports = [
        ast.ImportFrom(module="numpy", names=[ast.alias("*")], level=0),
        ast.ImportFrom(module="numba", names=[ast.alias("*")], level=0),
    ] if numpy else [
        ast.ImportFrom(module="math", names=[ast.alias("*")], level=0),
        ast.ImportFrom(module="numba", names=[ast.alias("*")], level=0),
    ]
    m = ast.Module([*imports, *items], [] )
    ast.fix_missing_locations(m)
    return m

def emit(m): 
    return ast.unparse(m)

def flatten(x):
    out = []
    for item in (x if isinstance(x, list) else [x]):
        if item is None: continue
        if isinstance(item, Block):
            out.extend(flatten(item.stmts))
        elif isinstance(item, list):
            out.extend(flatten(item))
        else:
            out.append(item)
    return out

def compile_ast(tree):
    ast.fix_missing_locations(tree)
    code = compile(tree, filename="generated",mode="exec")
    namespace = {}
    exec(code, namespace)
    return namespace["generated"]