from ..codegen import *
from.crconfig import *
from ..core import *
from .scheduler import *
from .subexpressions import *

def generate_code(root: CR):
    env = initialize_env(root)
    traces_byorder = partition_orders(env, root)
    # starts are implicitly initialized here:
    tape = construct_tape(env, root)

    # for each order... 
    # for each cr in the order, use 
    for order in range(len(traces_byorder)):
        for cr in order:
            pass

def generate_nested(registers: Registers, traces_byorder:  list[list[CR]]):
    dimensions = len(traces_byorder)
    latches = [None for i in range(len(traces_byorder))]
    for i in range(dimensions):
        pass


def dispatch_shift(registers: Registers, cfg: CRconfig, env: dict[CR, CRconfig]):
    cr, start = cfg.cr, cfg.tape_start
    if isinstance(cr, CRsum): emit_sum_shift(registers, start, len(cr))
    elif isinstance(cr, CRprod): emit_crprod_shift(registers, start, len(cr))
    elif isinstance(cr, CRtrig): emit_crtrig_shift(registers, start, len(cr))
    elif isinstance(cr, CRE):
        for i in range(len(cr)):
            if cr[i].variable == cr.variable:
                child = cr[i]
                sub_cfg = env[child]
                dispatch_access(registers, sub_cfg, env)


def dispatch_access(registers: Registers, cfg: CRconfig, env: dict[CR, CRconfig]):
    cr, start = cfg.cr, cfg.tape_start
    args = (cr, start, len(cr))
    # make idempotent, a little bit sketchy:

    table = { 
            CRsum: access_first, CRprod: access_first, CRsin: access_first,
            CRcos: access_mid, CRtan: access_tan, CRcot: access_cot,
            CREadd: access_cre_add, CREmul: access_cre_mul, CREpow: access_cre_pow,
            CRElog: access_cre_log, CREsin: access_cre_sin, CREcos: access_cre_cos,
            CREtan: access_cre_tan, CREcot: access_cre_cot
        }
    
    if isinstance(cr, CREconnector):
        sub_cfg = env[cr[0]] # consed subtree
        sub_cr, sub_start = sub_cfg.cr, sub_cfg.tape_start
        if not isinstance(cr.original, CRtrig) or cr.index != -1:
            dispatch_access(registers, sub_cfg, env)
        else:
            # proof sketch/convince yourself: CREconnector will not recurse
            # NTS: working on the consed subtree tape, but sticking the original access type
            table[type(cr.original)](registers, sub_start, len(sub_cr))
    else:
        return table[type(cr)]


"""
scratch: 
what conditions will result in a fetch? if the subtree has any non-atomic nodes of lesser variable
if any subtree has lesser variable
"""

def dispatch_fetch(registers: Registers, cfg: CRconfig, env: dict[CR, CRconfig]):
    cr = cfg.cr
    for i, child in enumerate(cr):
        sub_cfg = env[child]
        if not isinstance(child, CRnum) and sub_cfg.least_variable != cr.variable:
            dispatch_access(registers, sub_cfg, env)

