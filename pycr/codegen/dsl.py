import ast


def name(id: str, ctx):
    return ast.Name(id, ctx)


def load(id: str):
    return name(id, ast.Load())


def store(id: str):
    return name(id, ast.Store())


def c(x):
    return ast.Constant(x)


def add(a, b):
    return ast.BinOp(a, ast.Add(), b)


def sub(a, b):
    return ast.BinOp(a, ast.Sub(), b)


def mul(a, b):
    return ast.BinOp(a, ast.Mult(), b)


def div(a, b):
    return ast.BinOp(a, ast.Div(), b)


def neg(x):
    return ast.UnaryOp(ast.USub(), x)


def pow_(a, b):
    return ast.BinOp(a, ast.Pow(), b)


def _m(fn, x):
    return ast.Call(ast.Attribute(load("math"), fn, ast.Load()), [x], [])


def sin(x):
    return _m("sin", x)


def cos(x):
    return _m("cos", x)


def tan(x):
    return _m("tan", x)


def exp(x):
    return _m("exp", x)


def ln(x):
    return _m("log", x)


def log(x):
    return _m("log10", x)


def cot(x):
    return div(c(1), tan(x))


def logb(x, base):
    return div(ln(x), ln(base))


def assign(target: ast.expr, value: ast.expr):
    return ast.Assign([target], value)


def aug_add(target: ast.expr, value: ast.expr):
    return ast.AugAssign(target, ast.Add(), value)


def aug_mult(target: ast.expr, value: ast.expr):
    return ast.AugAssign(target, ast.Mult(), value)


def _flatten_stmts(xs):
    out = []
    for x in xs:
        if x is None:
            continue
        if isinstance(x, list):
            out.extend(_flatten_stmts(x))
        else:
            out.append(x)
    return out


def for_range(i_target: ast.expr, stop: ast.expr, body):
    body = _flatten_stmts(body)
    if not body:
        body = [ast.Pass()]

    return ast.For(
        target=i_target,
        iter=ast.Call(load("range"), [c(0), stop], []),
        body=body,
        orelse=[],
    )



def while_(test, body):
    return ast.While(test, body, [])


def ret(x):
    return ast.Return(x)


def fn(name_s: str, args, body):
    return ast.FunctionDef(
        name_s,
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
        None,
    )


def mod(*items):
    m = ast.Module(
        [
            ast.Import([ast.alias("math", None)]),
            ast.ImportFrom("math", [ast.alias("*", None)], 0),
            *items,
        ],
        [],
    )
    ast.fix_missing_locations(m)
    return m



def subscript(value_expr: ast.expr, idx_expr: ast.expr, ctx):
    return ast.Subscript(value=value_expr, slice=idx_expr, ctx=ctx)


def set_at(arr_expr: ast.expr, idx_expr: ast.expr, value_expr: ast.expr):
    return assign(subscript(arr_expr, idx_expr, ast.Store()), value_expr)


