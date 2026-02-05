import ast


# --- core nodes ---
def L(name):  # load name
    return ast.Name(id=name, ctx=ast.Load())

def S(name):  # store name
    return ast.Name(id=name, ctx=ast.Store())

def C(v):
    return ast.Constant(value=v)

def Attr(obj, name):
    return ast.Attribute(value=obj, attr=name, ctx=ast.Load())

def Call(f, *args):
    return ast.Call(func=f, args=list(args), keywords=[])

def Bin(left, op, right):
    return ast.BinOp(left=left, op=op, right=right)

def Unary(op, x):
    return ast.UnaryOp(op=op, operand=x)

def Assign(lhs, rhs):
    return ast.Assign(targets=[lhs], value=rhs)

def AugAssign(lhs, op, rhs):
    return ast.AugAssign(target=lhs, op=op, value=rhs)

def ExprStmt(expr):
    return ast.Expr(value=expr)

def Return(expr=None):
    return ast.Return(value=expr)

def ForRange(var, n, body):
    return ast.For(
        target=S(var),
        iter=Call(L("range"), n),
        body=body,
        orelse=[],
    )

def Add(a, b): return Bin(a, ast.Add(), b)
def Sub(a, b): return Bin(a, ast.Sub(), b)
def Mul(a, b): return Bin(a, ast.Mult(), b)
def Div(a, b): return Bin(a, ast.Div(), b)
def Neg(x):   return Unary(ast.USub(), x)

def build(args, blocks, filename="<generated code>", fname="_generated", dump=False):
    body = []
    for b in blocks:
        body.extend(b if isinstance(b, list) else [b])

    f = ast.FunctionDef(
        name=fname,
        args=ast.arguments(
            posonlyargs=[],
            args=[ast.arg(arg=a) for a in args],
            kwonlyargs=[],
            kw_defaults=[],
            defaults=[],
            vararg=None,
            kwarg=None,
        ),
        body=body,
        decorator_list=[],
        returns=None,
        type_comment=None,
    )

    mod = ast.Module(body=[f], type_ignores=[])
    ast.fix_missing_locations(mod)

    if dump:
        print(ast.unparse(mod))

    ns = {}
    exec(compile(mod, filename, "exec"), ns, ns)
    return ns[fname]
