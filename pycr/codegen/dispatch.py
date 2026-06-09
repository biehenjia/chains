from .registers import Registers, emit_reset
from .shifting import emit_sum_shift, emit_crprod_shift, emit_crtrig_shift
from .access import (
    access_first, access_mid, access_tan, access_cot,
    access_cre_add, access_cre_mul, access_cre_pow, access_cre_log,
    access_cre_sin, access_cre_cos, access_cre_tan, access_cre_cot,
)
from ..core import (
    CR, CRnum, CRsum, CRprod, CRtrig, CRsin, CRcos, CRtan, CRcot,
    CRE, CREadd, CREmul, CREpow, CRElog, CREsin, CREcos, CREtan, CREcot,
    CREconnector,
)
from ..crconfig import CRconfig

def dispatch_shift(regs: Registers, cfg: CRconfig, env: dict[CR, CRconfig]):
    cr, start = cfg.cr, cfg.tape_start
    if isinstance(cr, CRsum): emit_sum_shift(regs, start, len(cr))
    elif isinstance(cr, CRprod): emit_crprod_shift(regs, start, len(cr))
    elif isinstance(cr, CRtrig): emit_crtrig_shift(regs, start, len(cr))
    elif isinstance(cr, CRE):

        for i in range(len(cr)):
            if cr[i].variable == cr.variable:
                child = cr[i]
                sub_cfg = env[child]
                regs[start+i] = dispatch_access(regs, sub_cfg, env)

def dispatch_access(regs: Registers, cfg: CRconfig, env: dict[CR, CRconfig]):
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
            return dispatch_access(regs, sub_cfg, env)
        else:
            #print("original:", cr.original)
            # proof sketch/convince yourself: CREconnector will not recurse
            # NTS: working on the consed subtree tape, but sticking the original access type
            return table[type(cr.original)](regs, sub_start, len(sub_cr))
    else:
        return table[type(cr)](regs, start, len(cr))

"""
scratch:
what conditions will result in a fetch? if the subtree has any non-atomic nodes of lesser variable
if any subtree has lesser variable
"""

def dispatch_fetch(regs: Registers, cfg: CRconfig, env: dict[CR, CRconfig]):
    cr = cfg.cr
    for i, child in enumerate(cr):
        sub_cfg = env[child]
        if not isinstance(child, CRnum) and sub_cfg.least_variable.name != cr.variable.name:
            res = dispatch_access(regs, sub_cfg, env)
            regs[cfg.tape_start+i] = res

def dispatch_reset(regs: Registers, cfg: CRconfig, env: dict[CR, CRconfig]):
    cr, start = cfg.cr, cfg.tape_start
    emit_reset(regs, start, len(cr))
