from ..core import *
from .dsl import *
import sympy


def _r(register_symbol, idx):
    return f"{register_symbol}{idx}"


def rload(register_symbol, idx):
    return load(_r(register_symbol, idx))


def rstore(register_symbol, idx):
    return store(_r(register_symbol, idx))


def gen_fetch(crterm, register_symbol="r"):
    block = []
    for write, source, read in crterm.updates:
        location = source.start + read
        block.append(
            assign(
                rstore(register_symbol, read),
                rload(register_symbol, location),
            )
        )
    return block


def gen_shift(crterm, register_symbol="r"):
    block = []

    if isinstance(crterm.cr, CRtrig):
        n = len(crterm.cr)
        t = n // 2

        for i in range(t - 1):
            a_idx = crterm.start + i
            b_idx = crterm.start + t + i
            ap1_idx = crterm.start + i + 1
            bp1_idx = crterm.start + t + i + 1

            aL = rload(register_symbol, a_idx)
            bL = rload(register_symbol, b_idx)
            ap1L = rload(register_symbol, ap1_idx)
            bp1L = rload(register_symbol, bp1_idx)

            aS = rstore(register_symbol, a_idx)
            bS = rstore(register_symbol, b_idx)

            tmp_a_name = f"__tmp_a_{a_idx}_{b_idx}"
            tmp_b_name = f"__tmp_b_{a_idx}_{b_idx}"
            tmp_aS = store(tmp_a_name)
            tmp_bS = store(tmp_b_name)
            tmp_aL = load(tmp_a_name)
            tmp_bL = load(tmp_b_name)

            new_a = add(mul(aL, bp1L), mul(bL, ap1L))
            new_b = sub(mul(bL, bp1L), mul(aL, ap1L))

            block.append(assign(tmp_aS, new_a))
            block.append(assign(tmp_bS, new_b))
            block.append(assign(aS, tmp_aL))
            block.append(assign(bS, tmp_bL))

    elif isinstance(crterm.cr, CRsum):
        for i in range(len(crterm.cr) - 1):
            block.append(
                aug_add(
                    rstore(register_symbol, crterm.start + i),
                    rload(register_symbol, crterm.start + i + 1),
                )
            )

    elif isinstance(crterm.cr, CRprod):
        for i in range(len(crterm.cr) - 1):
            block.append(
                aug_mult(
                    rstore(register_symbol, crterm.start + i),
                    rload(register_symbol, crterm.start + i + 1),
                )
            )

    return block


# ad-hoc; i dont like this
def gen_update(crterm, register_symbol="r"):
    block = []

    update_idx = crterm.update_index
    start_idx = crterm.start
    second_idx = crterm.start + 1
    mid_idx = crterm.mid

    updateR_L = rload(register_symbol, update_idx)
    updateR_S = rstore(register_symbol, update_idx)

    startR_L = rload(register_symbol, start_idx)
    startR_S = rstore(register_symbol, start_idx)

    secondR_L = rload(register_symbol, second_idx)
    secondR_S = rstore(register_symbol, second_idx)

    midR_L = rload(register_symbol, mid_idx)
    midR_S = rstore(register_symbol, mid_idx)

    if isinstance(crterm.cr, (CRsum, CRprod, CRsin)):
        block.append(assign(updateR_S, startR_L))
    elif isinstance(crterm.cr, CRcos):
        block.append(assign(updateR_S, midR_L))
    elif isinstance(crterm.cr, CRtan):
        block.append(assign(updateR_S, div(startR_L, midR_L)))
    elif isinstance(crterm.cr, CRcot):
        block.append(assign(updateR_S, div(midR_L, startR_L)))

    # kwargs this away
    elif isinstance(crterm.cr, CREadd):
        block.append(assign(updateR_S, add(startR_L, secondR_L)))
    elif isinstance(crterm.cr, CREmul):
        block.append(assign(updateR_S, mul(startR_L, secondR_L)))
    elif isinstance(crterm.cr, CREsin):
        block.append(assign(updateR_S, sin(startR_L)))
    elif isinstance(crterm.cr, CREcos):
        block.append(assign(updateR_S, cos(startR_L)))

    elif isinstance(crterm.cr, CREtan):
        block.append(assign(updateR_S, tan(startR_L)))

    elif isinstance(crterm.cr, CREcot):
        block.append(assign(updateR_S, cot(startR_L)))

    elif isinstance(crterm.cr, CREpow):
        block.append(assign(updateR_S, pow_(startR_L, secondR_L)))

    elif isinstance(crterm.cr, CRElog):
        block.append(assign(updateR_S, logb(startR_L, secondR_L)))
    return block


def gen_nested(blocks, symbol_table, out_name, n_registers, register_symbol="r", idx_prefix="_i"):
    syms = list(symbol_table.keys())
    idx_names = [f"{idx_prefix}{d}" for d in range(len(syms))]

    val = load(f"{register_symbol}{n_registers - 1}")

    inner = flatten(blocks[-1]) + [set_nd(out_name, idx_names, val)]

    body = inner
    for depth in reversed(range(len(syms))):
        name = getattr(syms[depth], "name", str(syms[depth]))
        bound = load(f"{name}_b")

        body = flatten(body)
        body = [for_range(store(idx_names[depth]), bound, body)]
        if depth > 0:
            body = blocks[depth - 1] + body

    return flatten(body)



def flatten(blocks):
    out = []
    for x in blocks:
        if isinstance(x, list):
            out.extend(flatten(x))
        else:
            out.append(x)
    return out


def seed_stmt_locations(tree, lineno=1, col=0):
    for n in ast.walk(tree):
        attrs = getattr(n, "_attributes", ())
        if "lineno" in attrs and not hasattr(n, "lineno"):
            n.lineno = lineno
            n.col_offset = col
        if "end_lineno" in attrs and not hasattr(n, "end_lineno"):
            n.end_lineno = getattr(n, "lineno", lineno)
            n.end_col_offset = getattr(n, "col_offset", col)


def _sym_name(s): 
    return getattr(s, "name", str(s))

def _sym_sort_key(n):
    try:
        a, b = n.rsplit("_", 1)
        return (a, int(b))
    except Exception:
        return (n, 0)


def sympy_to_astexpr(e):
    return ast.parse(str(e), mode="eval").body

def stitch(stmts, fn_name="generated", symtab=None, tape=(), register_symbol="r", out_name="out"):
    symtab = symtab or {}

    args = [out_name]
    for s in symtab.keys():
        n = getattr(s, "name", str(s))
        args += [f"{n}_0", f"{n}_h", f"{n}_b"]

    pre = [assign(store(f"{register_symbol}{k}"), sympy_to_astexpr(e)) for k, e in enumerate(tape)]
    stmts = flatten(stmts)

    f = fn(fn_name, args, pre + stmts)
    m = mod(f)
    seed_stmt_locations(m)
    ast.fix_missing_locations(m)
    return m

def set_nd(out_name, idx_names, value_expr):
    t = load(out_name)
    for d in range(len(idx_names) - 1):
        t = subscript(t, load(idx_names[d]), ast.Load())
    tgt = subscript(t, load(idx_names[-1]), ast.Store())
    return assign(tgt, value_expr)
