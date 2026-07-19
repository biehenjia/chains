from ..crconfig import CRconfig
from ..core import CR
from .dispatch import dispatch_shift, dispatch_access, dispatch_fetch, dispatch_reset, dispatch_connector_fetch
from .looping import begin_loop, end_loop
from .registers import Registers


def generate_nested(regs, traces_byorder, env, policy):
    dimensions = len(traces_byorder)
    latches = []
    for i in range(dimensions - 1):
        latches.append(begin_loop(regs, regs.bounds[i]))
        generate_loop(regs, traces_byorder[i], env)

    latches.append(begin_loop(regs, regs.bounds[dimensions - 1], policy.W))
    generate_loop(regs, traces_byorder[-1], env, final=True)
    # regs[-1] = dispatch_access(regs,env[traces_byorder[-1][-1]],env)
    # policy.emit_tail(regs.builder, regs.result, regs[-1], latches[-1].idx, regs.bounds[dimensions - 1])
    end_loop(regs, latches.pop())

    for i in range(dimensions-1):
        for j in range(-i-1, 0):
            generate_cleanup(regs, traces_byorder[j], env)
        end_loop(regs, latches.pop())

def generate_loop(regs: Registers, order: list[CR], env: dict[CR, CRconfig], final=False):
    for cr in order:
        dispatch_connector_fetch(regs, env[cr], env)
    if final:
        root = order[-1]
        cfg = env[root]
        regs.store_result(regs.indices, dispatch_access(regs, cfg, env))
    for cr in order:
        dispatch_shift(regs, env[cr], env)

def generate_cleanup(regs: Registers, order: list[CR], env: dict[CR, CRconfig]):
    for cr in order:
        sub_cfg = env[cr]
        dispatch_reset(regs, sub_cfg, env)
        dispatch_fetch(regs, sub_cfg, env)
