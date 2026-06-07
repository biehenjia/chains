from .crconfig import *
from .dispatch import *

def generate_nested(regs, traces_byorder, env, policy):
    dimensions = len(traces_byorder)
    latches = []

    for i in range(dimensions - 1):
        latches.append(begin_loop(regs, regs.bounds[i]))
        generate_loop(regs, traces_byorder[i], env)


    latches.append(begin_loop(regs, regs.bounds[dimensions - 1], policy.W))
    generate_loop(regs, traces_byorder[-1], env, final=True)
    policy.emit_tail(regs.builder, regs.result, regs[0], latches[-1].idx, regs.bounds[dimensions - 1])
    end_loop(regs, latches.pop())

    for i in range(dimensions-1):
        order = traces_byorder[-i-1]
        generate_cleanup(regs, order, env)
        end_loop(regs, latches.pop())


def generate_loop(regs: Registers, order: list[CR], env: dict[CR, CRconfig], final=False):
    if final:
        root = order[-1]
        cfg = env[root]
        regs.store_result(regs.indices, dispatch_access(regs, cfg, env))
    for cr in order:
        sub_cfg = env[cr]
        dispatch_shift(regs, sub_cfg, env )

def generate_cleanup(regs: Registers, order: list[CR], env: dict[CR, CRconfig] ):
    for cr in order:
        sub_cfg = env[cr]
        dispatch_reset(regs, sub_cfg, env)
        dispatch_fetch(regs, sub_cfg, env)