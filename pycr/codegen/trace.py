from __future__ import annotations

class TraceRegs:
    """
    Impersonates `Registers` + `Math` enough to drive the existing
    dispatch/generator code. Records into a nested loop scope tree.
    """

    def __init__(self, n_slots: int):
        self.n_slots = n_slots
        self.constants = [('init', i) for i in range(n_slots)]
        self.bounds: list = []
        self.indices: list = []
        self.result = None
        self._top: list = []
        self._scope: list[list] = [self._top]
        self._tag: str | None = None

    # Registers surface
    def __getitem__(self, i): return ('load', i)
    def __setitem__(self, i, v):
        if self._tag is None:
            self._scope[-1].append(('store', i, v))
        else:
            self._scope[-1].append(('store', i, v, self._tag))
    def __len__(self): return self.n_slots + 1
    def bind(self, *a, **kw): pass
    def prologue(self, n):
        for i in range(n): self._scope[-1].append(('store', i, ('init', i)))
    def store_result(self, indices, val):
        self._scope[-1].append(('result', tuple(indices), val))
    def linearize(self, indices): return tuple(indices)

    # Math surface — every op returns ('op', name, args)
    def add(self, a, b): return ('op', 'add', (a, b))
    def sub(self, a, b): return ('op', 'sub', (a, b))
    def mul(self, a, b): return ('op', 'mul', (a, b))
    def div(self, a, b): return ('op', 'div', (a, b))
    def neg(self, a):    return ('op', 'neg', (a,))
    def fma(self, a, b, c): return ('op', 'fma', (a, b, c))
    def exp(self, a):    return ('op', 'exp', (a,))
    def exp2(self, a):   return ('op', 'exp2', (a,))
    def log(self, a):    return ('op', 'log', (a,))
    def log2(self, a):   return ('op', 'log2', (a,))
    def log10(self, a):  return ('op', 'log10', (a,))
    def logab(self, a, b): return ('op', 'logab', (a, b))
    def pow(self, a, b): return ('op', 'pow', (a, b))
    def sin(self, a):    return ('op', 'sin', (a,))
    def cos(self, a):    return ('op', 'cos', (a,))
    def tan(self, a):    return ('op', 'tan', (a,))
    def cot(self, a):    return ('op', 'cot', (a,))

    # Loop scope
    def enter_loop(self, axis: int, stride: int = 1):
        body: list = []
        self._scope[-1].append(('loop', ('bound', axis), stride, body))
        self._scope.append(body)
        self.indices.append(('idx', axis))

    def exit_loop(self):
        self._scope.pop()
        self.indices.pop()

    def program(self): return self._top


def trace_generate_nested(regs: TraceRegs, traces_byorder, env, stride_last: int = 1):
    """Mirror of `codegen.generators.generate_nested` for TraceRegs."""
    from .dispatch import (
        dispatch_shift, dispatch_access, dispatch_fetch,
        dispatch_reset, dispatch_connector_fetch,
    )
    from .generators import _fetch_slots

    dims = len(traces_byorder)

    def tag(cr, phase):
        regs._tag = f"{type(cr).__name__}@{env[cr].tape_start} {phase}"

    for i in range(dims - 1):
        regs.enter_loop(i)
        for cr in traces_byorder[i]:
            tag(cr, 'cfetch')
            dispatch_connector_fetch(regs, env[cr], env)
        for cr in traces_byorder[i]:
            tag(cr, 'shift')
            dispatch_shift(regs, env[cr], env)
        regs._tag = None

    regs.enter_loop(dims - 1, stride=stride_last)
    order = traces_byorder[-1]
    for cr in order:
        tag(cr, 'cfetch')
        dispatch_connector_fetch(regs, env[cr], env)
    regs._tag = None
    root = order[-1]
    regs.store_result(tuple(regs.indices), dispatch_access(regs, env[root], env))
    for cr in order:
        tag(cr, 'shift')
        dispatch_shift(regs, env[cr], env)
    regs._tag = None
    regs.exit_loop()

    for i in range(dims - 1):
        for j in range(-i - 1, 0):
            for cr in traces_byorder[j]:
                cfg = env[cr]
                skip = _fetch_slots(cr, env)
                tag(cr, 'cleanup:reset')
                dispatch_reset(regs, cfg, env, skip=skip)
                tag(cr, 'cleanup:fetch')
                dispatch_fetch(regs, cfg, env)
            regs._tag = None
        regs.exit_loop()


_BINOP = {'add': '+', 'sub': '-', 'mul': '*', 'div': '/'}
_AUGOP = {'add': '+=', 'sub': '-=', 'mul': '*='}

def format_expr(e) -> str:
    tag = e[0]
    if tag == 'load':  return f"a[{e[1]}]"
    if tag == 'init':  return f"init[{e[1]}]"
    if tag == 'idx':   return f"i{e[1]}"
    if tag == 'bound': return f"N{e[1]}"
    if tag == 'const': return repr(e[1])
    if tag == 'op':
        name, args = e[1], e[2]
        if name == 'neg': return f"-{format_expr(args[0])}"
        if name in _BINOP:
            return f"({format_expr(args[0])} {_BINOP[name]} {format_expr(args[1])})"
        return f"{name}({', '.join(format_expr(a) for a in args)})"
    return repr(e)


def _compound(store):
    """Store(i, ('op', op, (('load', i), rhs))) → (op, rhs) or None."""
    slot, expr = store[1], store[2]
    if not (isinstance(expr, tuple) and expr[:1] == ('op',)): return None
    name, args = expr[1], expr[2]
    if name not in _AUGOP or len(args) != 2: return None
    if args[0] != ('load', slot): return None
    return name, args[1]

def format_stmt(s, indent: int = 0) -> str:
    pad = '  ' * indent
    tag = s[0]
    if tag == 'store':
        note = f'   # {s[3]}' if len(s) > 3 and s[3] else ''
        c = _compound(s)
        if c is not None:
            op, rhs = c
            return f"{pad}a[{s[1]}] {_AUGOP[op]} {format_expr(rhs)}{note}"
        return f"{pad}a[{s[1]}] := {format_expr(s[2])}{note}"
    if tag == 'result':
        idx = ', '.join(format_expr(i) for i in s[1])
        return f"{pad}result[{idx}] := {format_expr(s[2])}"
    if tag == 'loop':
        _, bound, stride, body = s
        tail = '' if stride == 1 else f" stride={stride}"
        head = f"{pad}for _ in range({format_expr(bound)}){tail}:"
        inner = '\n'.join(format_stmt(x, indent + 1) for x in body) or f"{pad}  pass"
        return f"{head}\n{inner}"
    return f"{pad}{s!r}"

def format_program(stmts) -> str:
    return '\n'.join(format_stmt(s) for s in stmts)
