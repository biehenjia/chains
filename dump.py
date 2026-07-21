

from pycr.core import CRnum, CREconnector
from pycr.codegen.trace import format_program as _format_trace


def format_tree(cr, env) -> str:
    lines: list[str] = []
    _tree(cr, env, "", True, True, lines)
    return "\n".join(lines)


def _tree(cr, env, prefix: str, is_root: bool, is_last: bool, lines: list[str]) -> None:
    branch = "" if is_root else ("└─ " if is_last else "├─ ")
    tag = type(cr).__name__

    if isinstance(cr, CRnum):
        lines.append(f"{prefix}{branch}{tag}({cr.value})")
        return

    cfg = env[cr]
    a, b = cfg.tape_start, cfg.tape_start + len(cr) - 1
    slots = f"slots[{a}]" if a == b else f"slots[{a}..{b}]"
    head = f"{prefix}{branch}{tag} {slots} var={cr.variable}"

    if isinstance(cr, CREconnector):
        src = cr[0]
        orig = type(getattr(cr, "original", src)).__name__
        lines.append(f"{head} -> {type(src).__name__}@{env[src].tape_start} idx={cr.index} orig={orig}")
        return  # do not recurse — aliased source lives elsewhere in the tree

    lines.append(f"{head} len={len(cr)}")
    child_prefix = prefix + ("" if is_root else ("   " if is_last else "│  "))
    for i, child in enumerate(cr):
        _tree(child, env, child_prefix, False, i == len(cr) - 1, lines)


def format_tape(program) -> str:
    owner: dict[int, str] = {}
    for c, cfg in program.env.items():
        if isinstance(c, CRnum): continue
        for k in range(cfg.tape_start, cfg.tape_start + len(c)):
            owner.setdefault(k, f"{type(c).__name__}@{cfg.tape_start}[{k - cfg.tape_start}]")

    tape = program.tape
    o_w = max((len(v) for v in owner.values()), default=1)
    lines = [
        f"slot | {'owner':<{o_w}} | init value",
        f"-----+{'-'*(o_w+2)}+" + "-" * 34,
    ]
    for i, v in enumerate(tape):
        lines.append(f"{i:>4} | {owner.get(i, '?'):<{o_w}} | {v}")
    return "\n".join(lines)


def format_trace(stmts) -> str:
    return _format_trace(stmts)


if __name__ == "__main__":
    import sys
    from pycr.api.parse import parse
    from pycr.analysis.lower import lower
    from pycr.codegen.trace import TraceRegs, trace_generate_nested
    from pycr.analysis.dce import dce

    expr = sys.argv[1] if len(sys.argv) > 1 else "sin(x*y)"

    cr = parse(expr)
    p = lower(cr, 1)
    regs = TraceRegs(p.n_slots)
    trace_generate_nested(regs, p.traces_byorder, p.env)
    raw = regs.program()
    pruned = dce(raw)

    bar = "=" * 72
    print(f"{bar}\n  {expr}\n{bar}")
    print("\n--- tree ---")
    print(format_tree(p.cr, p.env))
    print("\n--- tape ---")
    print(format_tape(p))
    print("\n--- raw trace ---")
    print(format_trace(raw))
    print("\n--- pruned trace ---")
    print(format_trace(pruned))
