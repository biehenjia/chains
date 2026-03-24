from ..engine import IR
from ..core import *
from .dsl import *

RS = "r" # register symbol
OT = "R" # original tape
SV = "i" # shift variable 
UR = "UR" # fetch read symbol
UW = "UW" # fetch write symbol 
RV = "A" # return array
LS = "L" # loop symbol
BS = "B" # bound symbol




_UPDATE_EXPR = { 
    CRsum: "{start}",
    CRprod: "{start}",
    CRsin: "{start}",
    CRcos: "{m}",
    CRtan: "{start} / {m}",
    CRcot: "{m} / {s}",
    CREadd: "{start} + {u}",
    CREmul: "{start} * {u}",
    CREsin: "numpy.sin({start})",
    CREcos: "numpy.cos({start})",
    CREtan: "numpy.tan({start})",
    CREcot: "1/numpy.tan({start})",
    CREpow: "{start} ** {u}",
    CRElog: "numpy.log({start})/numpy.log({u})",
}


def gen_shift(ir, cr, block):
    start = ir.starts[cr]
    inner = Block()

    ri = f"{RS}[{start}+i]"
    ri1 = f"{RS}[{start}+i+1]"

    if isinstance(cr, CRtrig):
        t = len(cr)//2
        
        rti = f"{RS}[{start}+{t}+i]"
        rti1 = f"{RS}[{start}+{t}+i+1]"

        inner += s(f"__a={ri}*{rti1}+{rti}*{ri1}")
        inner += s(f"__b={rti}*{rti1}-{rti}*{ri1}")

        inner += s(f"{ri}=__a")
        inner += s(f"{rti}=__b")

        block.for_range(f"{SV}", t-1, inner)
    
    elif isinstance(cr, CRsum):
        inner += s(f"{ri}+={ri1}")
        block.for_range(f"{SV}", len(cr)-1, inner)

    elif isinstance(cr, CRprod):
        inner += s(f"{ri}*={ri1}")
        block.for_range(f"{SV}", len(cr)-1, inner)

def gen_fetch(order, reads,  block):
    inner = Block()
    inner += s(f"{RS}[{UW}_{order}[i]] = {RS}[{UR}_{order}[i]]")
    block.for_range(f"{SV}", len(reads[order]),inner)

# initialize register array and fetch arrays
# 
def gen_initialize(ir, block):
    # initial tape is passed as an argument
    block += s(f"{RS}[:] = {OT}[:]")
    # updates for each order
    reads = [[] for order in ir.orders]
    writes = [[] for order in ir.orders]

    for i,order in enumerate(ir.orders):
        for c in order:
            for j, operand in enumerate(c):
                if not isinstance(operand, CRnum):
                    reads[i].append(ir.starts[operand] + len(operand))
                    writes[i].append( ir.starts[c] + j)
    print(len(ir.st))
    
    for i in range(len(ir.st)):
        if reads[i]:
            block += s(f"{UR}_{i}={reads[i]}")
            block += s(f"{UW}_{i}={writes[i]}")
    return reads

# assume that IR is ready to go
def gen_nested(ir):
    block = Block()
    reads = gen_initialize(ir, block)
    loop_symbols = [f"{LS}_{i}" for i in range(len(ir.st))]
    
    inner = Block()
    inner += s(f"{RV}[{','.join(loop_symbols)}]={RS}[-1]")

    for i in range(len(ir.st)):
        order = ir.orders[-i-1]

        if not order:
            continue

        for c in order:
            gen_shift(ir,c,inner)
        outer = Block()
        outer.for_range(loop_symbols[-i-1],f"{BS}_{len(ir.st)-i-1}", inner)
        b1 = ir.starts[order[0]]
        b2 = ir.starts[order[-1]] + len(order[-1])
        if i +1 < len(ir.st):
            outer += s(f"{RS}[{b1}:{b2}] = {OT}[{b1}:{b2}]")
            gen_fetch(len(ir.st)-i-1,reads, outer)
        inner = outer
    
    block += inner
    return block

        
        
    



    