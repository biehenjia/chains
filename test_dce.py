

from pycr.api.parse import parse
from pycr.analysis.lower import lower
from pycr.codegen.trace import TraceRegs, trace_generate_nested, format_program
from pycr.analysis.dce import dce, read_slots


def collect_stores(stmts):
    """Return list of (slot, expr) for every store, recursing into loops."""
    out = []
    for s in stmts:
        if s[0] == 'store': out.append((s[1], s[2]))
        elif s[0] == 'loop': out.extend(collect_stores(s[3]))
    return out


def written_slots(stmts):
    return {slot for slot, _ in collect_stores(stmts)}


def build(expr: str):
    cr = parse(expr)
    p = lower(cr, 1)
    regs = TraceRegs(p.n_slots)
    trace_generate_nested(regs, p.traces_byorder, p.env)
    return regs.program()


def show(expr: str):
    raw = build(expr)
    pruned = dce(raw)
    print(f"\n{'='*70}\n{expr}\n{'='*70}")
    print("--- raw ---")
    print(format_program(raw))
    print("--- pruned ---")
    print(format_program(pruned))
    before, after = written_slots(raw), written_slots(pruned)
    dropped = sorted(before - after)
    print(f"--- dropped slots: {dropped} ---")
    return raw, pruned




def test_sin_xy_drops_dead_connectors():
    """CSE creates connectors into slots 8, 9 that no downstream consumer reads."""
    raw, pruned = show("sin(x*y)")
    b, a = written_slots(raw), written_slots(pruned)
    dropped = b - a
    assert 8 in dropped and 9 in dropped, f"expected {{8,9}} dropped, got {dropped}"


def test_tight_cases_unchanged():
    """Expressions with no dead stores should DCE to an identical trace."""
    for expr in ["x**2 + y", "x*y*z", "x + y"]:
        raw = build(expr)
        pruned = dce(raw)
        # Both should have identical structure — nothing dropped.
        assert format_program(raw) == format_program(pruned), \
            f"{expr}: DCE removed live stores"


def test_result_is_never_dropped():
    """The result stmt must always survive DCE."""
    def has_result(stmts):
        for s in stmts:
            if s[0] == 'result': return True
            if s[0] == 'loop' and has_result(s[3]): return True
        return False
    for expr in ["x + y", "sin(x*y)", "x**2 + y*z"]:
        assert has_result(dce(build(expr))), f"{expr}: result lost"


def test_pruned_read_writes_closed():
    """Every read in the pruned trace must be to a slot that's written somewhere in it."""
    def all_reads(stmts):
        out = set()
        for s in stmts:
            if s[0] == 'store': out |= read_slots(s[2])
            elif s[0] == 'result': out |= read_slots(s[2])
            elif s[0] == 'loop': out |= all_reads(s[3])
        return out
    for expr in ["sin(x*y)", "x**2 + y", "x*y*z", "cos(x + y**2)"]:
        pruned = dce(build(expr))
        reads = all_reads(pruned)
        writes = written_slots(pruned)
        raw_writes = written_slots(build(expr))
        pruned_only_written = writes
        orphaned = (reads & raw_writes) - pruned_only_written
        assert not orphaned, f"{expr}: reads to pruned-only slots {orphaned}"


if __name__ == "__main__":
    test_sin_xy_drops_dead_connectors()
    test_tight_cases_unchanged()
    test_result_is_never_dropped()
    test_pruned_read_writes_closed()
    print("\n\nAll tests passed.")
