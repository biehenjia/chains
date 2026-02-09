from .dsl import *
from ..core import *

def _r(register_symbol, idx):
    return f"{register_symbol}{idx}"

def rload(register_symbol, idx):
    return load(_r(register_symbol, idx))

def rstore(register_symbol, idx):
    return store(_r(register_symbol, idx))


def gen_fetch(crterm, register_symbol= "r"):
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


def gen_shift(crterm, register_symbol= "r"):
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
def gen_update(crterm, register_symbol = "r"):
    block = []

    update_idx = crterm.start + crterm.update_index
    start_idx  = crterm.start
    second_idx = crterm.start + 1
    mid_idx    = crterm.mid

    updateR_L = rload(register_symbol, update_idx)
    updateR_S = rstore(register_symbol, update_idx)

    startR_L = rload(register_symbol, start_idx)
    startR_S = rstore(register_symbol, start_idx)

    secondR_L = rload(register_symbol, second_idx)
    secondR_S = rstore(register_symbol, second_idx)

    midR_L = rload(register_symbol, mid_idx)
    midR_S = rstore(register_symbol, mid_idx)

    if isinstance(crterm.cr, (CRsum, CRprod, CRsin)):
        block.append(
            assign(updateR_S, startR_L)
        )
    elif isinstance(crterm.cr, CRcos):
        block.append(
            assign(updateR_S, midR_L)
        )
    elif isinstance(crterm.cr, CRtan):
        block.append(
            assign(
                updateR_S,
                div(startR_L, midR_L)
            )
        )
    elif isinstance(crterm.cr, CRcot):
        block.append(
            assign(
                updateR_S,
                div(midR_L, startR_L)
            )
        )

    # kwargs this away
    elif isinstance(crterm.cr, CREadd):
        block.append(
            assign(
                updateR_S,
                add(startR_L, secondR_L)
            )
        )
    elif isinstance(crterm.cr, CREmul):
        block.append(
            assign(
                updateR_S,
                mul(startR_L, secondR_L)
            )
        )
    elif isinstance(crterm.cr, CREsin):
        block.append(
            assign(
                updateR_S,
                sin(startR_L)
            )
        )
    elif isinstance(crterm.cr, CREcos):
        block.append(
            assign(
                updateR_S,
                cos(startR_L)
            )
        )

    elif isinstance(crterm.cr, CREtan):
        block.append(
            assign(
                updateR_S,
                tan(startR_L)
            )
        )

    elif isinstance(crterm.cr, CREcot):
        block.append(
            assign(
                updateR_S,
                cot(startR_L)
            )
        )

    elif isinstance(crterm.cr, CREpow):
        block.append(
            assign(
                updateR_S,
                pow_(startR_L, secondR_L)
            )
        )
    
    elif isinstance(crterm.cr, CRElog):
        block.append(
            assign(
                updateR_S,
                logb(startR_L, secondR_L)
            )
        )
    return block


def gen_nested(blocks, bounds):
    pass