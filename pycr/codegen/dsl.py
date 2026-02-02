import ast

def L(name): 
    return ast.Name(id=name,ctx=ast.Load())

def S(name): 
    return ast.Name(id=name,ctx=ast.Store())

def C(name): 
    return ast.Constant(value=name)

def Attr(expr, name):
    return ast.Attribute(value=expr, attr=name, ctx=ast.Load())

def Call(f, *args): 
    return ast.Call(func=f, args=list(args),keywords=[])

def Bin(left, op, right):
    return ast.BinOp(left=left, op=op, right=right)

def Unary(op, operand): 
    return ast.UnaryOp(op=op, operand=operand)

def IndexL(arr, index): 
    return ast.Subscript(value=arr, slice=index, ctx=ast.Load())

def IndexS(arr, index): 
    return ast.Subscript(value=arr, slice=index, ctx=ast.Store())

def IndexNL(arr, indices): 
    slice = ast.Tuple(value=ast.Tuple(elts=list(indices), ctx=ast.Load()))
    return ast.Subscript(value=arr, slice=slice, ctx=ast.Load())

def IndexNS(arr, indices):
    slice = ast.Tuple(value=ast.Tuple(elts=list(indices), ctx=ast.Load()))
    return ast.Subscript(value=arr, slice=slice, ctx=ast.Store())

def Assign(lhs, rhs):
    return ast.Assign(targets=[lhs], value=rhs)

def AugAssign(lhs, op, rhs):
    return ast.AugAssign(target=lhs, op=op, value=rhs)

def ExprStmt(expr):
    return ast.Expr(value=expr)

def Return(expr=None):
    return ast.Return(value=expr)

def Import(name):
    return ast.Import(names=[ast.alias(name=name, asname=None)])

def For(target, iter, body, orelse=[]):
    return ast.For(target=target, iter=iter, body=body, orelse=orelse)

def ForRange(var, n, body):
    return For(S(var), Call(L('range'), n), body)

def Break():
    return ast.Break()

def Continue():
    return ast.Continue()

def ASTSin(expr):
    return Call(Attr(L('math'),'sin'),expr)

def ASTCos(expr):
    return Call(Attr(L('math'),'cos'),expr)

def ASTTan(expr):
    return Call(Attr(L('math'),'tan'),expr)

def ASTCot(expr):
    return Call(Attr(L('math'),'cot'),expr)

def ASTExp(expr):
    return Call(Attr(L('math'),'exp'),expr)

def ASTLog(expr):
    return Call(Attr(L('math'),'log'),expr)


def ASTAdd(left, right):
    return Bin(left, ast.Add(), right)

def ASTSub(left, right):
    return Bin(left, ast.Sub(), right)

def ASTMul(left, right):
    return Bin(left, ast.Mult(), right)

def ASTDiv(left, right):
    return Bin(left, ast.Div(), right)

def ASTPow(left, right):
    return Bin(left, ast.Pow(), right)


def ASTNeg(operand):
    return Unary(ast.USub(), operand)

def seed_locations(node, lineno=1, col=0):
    for n in ast.walk(node):
        attrs = getattr(n, "_attributes", ())
        if "lineno" in attrs:
            n.lineno = getattr(n, "lineno", lineno) or lineno
        if "col_offset" in attrs:
            n.col_offset = getattr(n, "col_offset", col) or col

def build( args, blocks, filename="<generated code>"):
    # blocks: list of lists of ast.stmt, or a flat list of ast.stmt
    body = []
    for b in blocks:
        if isinstance(b, list):
            body.extend(b)
        else:
            body.append(b)
    fname = "_generated"
    f = ast.FunctionDef(
        name=fname,
        args=ast.arguments(
            posonlyargs=[], args=[ast.arg(arg=a) for a in args],
            kwonlyargs=[], kw_defaults=[],
            defaults=[], vararg=None, kwarg=None,
        ),
        body=body, decorator_list=[],
        returns=None, type_comment=None,
    )

    f.lineno = 1
    f.col_offset = 0
    seed_locations(f, 1, 0)

    mod = ast.Module(body=[f], type_ignores=[])
    ast.fix_missing_locations(mod)

    ns = {}
    print(ast.unparse(mod))
    exec(compile(mod, filename, "exec"), ns, ns)
    return ns[fname]
