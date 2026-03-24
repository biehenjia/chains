from ..core import *
from .dsl import *
import sympy

DIMS = "dims"
TAPE_ARRAY = "R"
# it will be i_1 to 
# construct one contiguous tape that we pass around
# tape should be generated beforehand



def generate_initialize(crterm, block, symbol_table, rs = "r"):
    pass


def generate_dimension(crterm, block, symbol_table, rs = "r"):
    # generate on the dimensions, for each element in the dimension in order
    # produce a shift
    orders = crterm.partition_order(symbol_table)
    bounds = []
    for order in orders:
        if order:
            bound_start = order[0].start
            bound_end = order[-1].start + order[-1].trunc
            bounds.append((bound_start,bound_end))
        else:
            bounds.append((0,0))
        
    

    # prefix
    # for loop
    # ... for loop {}
    #    copy level above
    #    broadcast updates


    # pseudo
    # bodies = []
    # for each order in orders:
    #   for each item in the order: 
    #       generate the shift body for it
    #       append to bodies
    # flatten bodies 
    # foreach member to update, broadcast to update indices.

    # we use i_1, i_2, for each of the loops
    indices = [f"i_{i}" for i in range(len(symbol_table))]
    inner = Block()
    print(type(Block))
    inner += s(f"A[{','.join(indices)}] = r[-1]")
    

    # 
    for i in range(len(orders)):
        order = orders[-i-1]
        for crterm in order:
            generate_shift(crterm,inner,rs)
            generate_update(crterm,inner, rs)
        outer = Block()
        outer.for_range(f"i_{len(orders)-i-1}",f"b_{len(orders)-i-1}",inner)
        b1, b2 = bounds[-i-1]
        if b1 != b2:
            outer += s(f"r[{b1}:{b2}] = R[{b1}:{b2}]")
        generate_fetch(crterm,outer,rs)
        inner = outer
        
    block += inner
    
        


    

def generate_shift(crterm, block, rs = "r"):
    print(type(block))
    # generate a statement that is the shift
    cr = crterm.cr
    if isinstance(cr, CRtrig):
        t = crterm.trunc//2
        start = crterm.start
        inner = Block()
        inner += s(f"__a = {rs}[{start}+i] * {rs}[{start}+{t}+i+1] + {rs}[{start}+ {t}+i] * {rs}[{start}+i+1]")
        inner += s(f"__b = {rs}[{start}+{t}+i] * {rs}[{start}+{t}+i+1] - {rs}[{start}+i]*{rs}[{start}+i+1] ")
        inner += s(f"{rs}[{start}+i] = __a")
        inner += s(f"{rs}[{start}+{t}+i] = __b")
        block.for_range("i", t-1, inner)

    elif isinstance(cr, CRsum):
        start = crterm.start
        inner = Block()
        inner += s(f"{rs}[{start} + i] += {rs}[{start} + i + 1]")
        block.for_range("i", crterm.trunc-1, inner)

    elif isinstance(cr, CRprod):
        start = crterm.start
        inner = Block()
        inner += s(f"{rs}[{start} + i] *= {rs}[{start} + i + 1]")
        block.for_range("i", crterm.trunc-1, inner)




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


def generate_update(crterm, block, rs="r"):
    
    start = f"{rs}[{crterm.start}]"
    m = f"{rs}[{crterm.mid}]"
    u = f"{rs}[{crterm.start + 1}]"
    tmpl = _UPDATE_EXPR[type(crterm.cr)]
    block += s(f"{rs}[{crterm.update_index}] = {tmpl.format(start=start,m=m,u=u)}")


# make into numpy array
def generate_fetch(crterm, block, rs= "r"):
    for update in crterm.updates:
        # write, cr, read
        write, cr, read = update
        block += s(f"{rs}[{write}] = {rs}[{cr.start+read}]")
    
    # should look something like this
    if False:
        # 2d array: A[i] = (r,w): (read write)
        # iterate over and put R[read] to R[write]
        pass



    


