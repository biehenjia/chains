"""
Backward-liveness DCE over the tape-trace representation
(see `pycr.codegen.trace`).

Equivalent, on this domain, to the constructive forward slot-dirt
propagation from SHIFT_ANALYSIS.md §4 — same lattice, opposite direction.
Backward is chosen here because it runs directly on the trace tuples without
duplicating dispatch's structural knowledge; the constructive forward pass is
a future refactor.

Semantics: at each program point, a slot is `live` iff some subsequent read
of it precedes any overwrite. A `store` is dropped iff its target slot is
not live at that point. Loop bodies take a fixed point on `live_out` to
account for loop-carried reads (steady-state induction: ≤ a few passes).
"""

from __future__ import annotations


def read_slots(expr) -> set[int]:
    if not isinstance(expr, tuple): return set()
    tag = expr[0]
    if tag == 'load': return {expr[1]}
    if tag == 'op':
        out: set[int] = set()
        for a in expr[2]:
            out |= read_slots(a)
        return out
    return set()


def _walk(stmts, live_out):
    """Backward walk; returns (kept_stmts_in_original_order, live_in)."""
    live = set(live_out)
    kept_rev: list = []
    for s in reversed(stmts):
        tag = s[0]
        if tag == 'store':
            slot, expr = s[1], s[2]
            if slot in live:
                kept_rev.append(s)
                live.discard(slot)
                live |= read_slots(expr)
            # else: dead, drop
        elif tag == 'result':
            kept_rev.append(s)
            live |= read_slots(s[2])
        elif tag == 'loop':
            _, bound, stride, body = s
            body_live_out = set(live)
            pruned, body_live_in = body, set()
            for _ in range(8):
                pruned, body_live_in = _walk(body, body_live_out)
                new_out = body_live_in | live
                if new_out == body_live_out: break
                body_live_out = new_out
            kept_rev.append(('loop', bound, stride, pruned))
            live |= body_live_in
        else:
            kept_rev.append(s)
    return list(reversed(kept_rev)), live


def dce(program) -> list:
    """Prune dead stores from a top-level trace. Live-out at program end is {}."""
    pruned, _ = _walk(program, set())
    return pruned
