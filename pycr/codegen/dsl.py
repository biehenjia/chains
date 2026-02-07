import ast

def v(x): return ast.Name(x, ast.Load())
def c(x): return ast.Constant(x)

def add(a,b): return ast.BinOp(a, ast.Add(), b)
def sub(a,b): return ast.BinOp(a, ast.Sub(), b)
def mul(a,b): return ast.BinOp(a, ast.Mult(), b)
def div(a,b): return ast.BinOp(a, ast.Div(), b)
def neg(x):  return ast.UnaryOp(ast.USub(), x)
def pow_(a,b): return ast.BinOp(a, ast.Pow(), b)


def _m(fn, x): return ast.Call(ast.Attribute(v("math"), fn, ast.Load()), [x], [])
def sin(x): return _m("sin", x)
def cos(x): return _m("cos", x)
def tan(x): return _m("tan", x)
def exp(x): return _m("exp", x)


def ln(x):  return _m("log", x)
def log(x): return _m("log10", x)


def cot(x): return div(c(1), tan(x))


def assign(name, expr): return ast.Assign([ast.Name(name, ast.Store())], expr)
def aug_add(name, expr): return ast.AugAssign(ast.Name(name, ast.Store()), ast.Add(), expr)

def for_range(i, stop, body):
    # for i in range(0, stop): ...
    return ast.For(
        ast.Name(i, ast.Store()),
        ast.Call(v("range"), [c(0), stop], []),
        body,
        []
    )

def while_(test, body):
    return ast.While(test, body, [])

def ret(x): return ast.Return(x)

def fn(name, args, body):
    return ast.FunctionDef(
        name,
        ast.arguments(
            posonlyargs=[],
            args=[ast.arg(a) for a in args],
            vararg=None,
            kwonlyargs=[],
            kw_defaults=[],
            kwarg=None,
            defaults=[],
        ),
        body,
        [],
        None
    )

def mod(*items):
    m = ast.Module([ast.Import([ast.alias("math", None)]), *items], [])
    ast.fix_missing_locations(m)
    return m



