from ..engine import IR
from ..core import *
from .dsl import *
import sympy
from sympy.printing.numpy import NumPyPrinter
from sympy.printing.python import PythonPrinter,StrPrinter
RS = "r" # register symbol
OT = "R" # original tape
SV = "i" # shift variable 
UR = "UR" # fetch read symbol
UW = "UW" # fetch write symbol 
RV = "A" # return array
LS = "L" # loop symbol
BS = "B" # bound symbol
NT = "n_threads" # number of threads used
CN = "K" # chunk number
CK = "chunk" # chunk
UL = "UL"


_UPDATE_EXPR = { 
    CRsum: "{start}",
    CRprod: "{start}",
    CRsin: "{start}",
    CRcos: "{m}",
    CRtan: "{start} / {m}",
    CRcot: "{m} / {s}",
    CREadd: "{start} + {u}",
    CREmul: "{start} * {u}",
    CREsin: "sin({start})",
    CREcos: "cos({start})",
    CREtan: "tan({start})",
    CREcot: "1/tan({start})",
    CREpow: "{start} ** {u}",
    CRElog: "log({start})/log({u})",
}

_WRITE_EXPR = {
    CRsum: "{start}",
    CRprod: "{start}",
    CRsin: "{start}",
    CRcos: "{m}",
    CRtan: "{start} / {m}",
    CRcot: "{m} / {s}",
    CREadd: "{start}",
    CREmul: "{start}",
    CREsin: "{start}",
    CREcos: "{start}",
    CREtan: "{start}", 
    CREcot: "{start}",
    CREpow: "{start}",
    CRElog: "{start}"

}

# just a wrapper
class Generator:
    
    def __init__(self, ir):
        self.ir = ir

    # generate a shift for a particular cr
    def _gen_shift(self, cr):
        inner = Block()
        ir = self.ir
        start = ir.starts[cr]

        if isinstance(cr, CRtrig):
            t = len(cr)//2
            for i in range(t-1):
                ri = f"{RS}_{start+i}"
                ri1 = f"{RS}_{start+i+1}"
                rti = f"{RS}_{start+t+i}"
                rti1 = f"{RS}_{start+t+i+1}"
                inner += s(f"__a={ri}*{rti1}+{rti}*{ri1}")
                inner += s(f"__b={rti}*{rti1}-{ri}*{ri1}")
                inner += s(f"{ri}=__a")
                inner += s(f"{rti}=__b")

        elif isinstance(cr, CRsum):
            for i in range(len(cr)-1):
                inner += s(f"{RS}_{start+i} += {RS}_{start+i+1}")

        elif isinstance(cr, CRprod):
            for i in range(len(cr)-1):
                inner += s(f"{RS}_{start+i} *= {RS}_{start+i+1}")
        
        elif isinstance(cr, CRE):
            fmt = _UPDATE_EXPR[type(cr)]
            l = f"{RS}_{ir.starts[cr[0]]}"
            if len(cr) < 2:
                r = None
            elif isinstance(cr[1],CRnum):
                r = cr[1].valueof()
            else:
                r = f"{RS}_{ir.starts[cr[1]]}"
            inner += s(f"{RS}_{start} = {fmt.format(start=l, u=r)}")

        return inner
        
    def _gen_fetch(self, cr):
        
        starts = self.ir.starts
        inner = Block()
        if isinstance(cr, CRE):
            return inner
        
        for i in range(len(cr)):
            operand = cr[i]
            mystart = starts[cr]
            if not isinstance(operand, (CRnum,CRE)):
                opstart = starts[operand]
                oplen = len(operand)
                # not a leaf node, might be updated
                inner += s(f"{RS}_{mystart+i} = {RS}_{opstart + oplen}")
        start = f"{RS}_{mystart}"
        u = f"{RS}_{mystart+1}"
        mid = f"{RS}_{mystart+len(cr)//2}"
        fmt = _UPDATE_EXPR[type(cr)]
        inner += s(f"{RS}_{mystart+len(cr)} = {fmt.format(start=start,m=mid,u=u)}")
        
        return inner
    
    def _gen_reload(self, cr):
        inner = Block()
        mystart = self.ir.starts[cr]
        for i in range(len(cr)):
            inner += s(f"{RS}_{mystart+i} = {OT}_{mystart+i}")
        return inner 
    
    def _gen_update(self, cr ):
        block = Block()
        if isinstance(cr, CRE):
            return block
        start = self.ir.starts[cr]
        t = len(cr)//2
        m = start+t
        u = start+1
        s_start = f"{RS}_{start}"
        s_mid = f"{RS}_{m}"
        s_second = f"{RS}_{u}"
        fmt = _UPDATE_EXPR[type(cr)]
        block += s(f"{RS}_{start+len(cr)}={fmt.format(start=s_start,m=s_mid,u=s_second)}")
        return block 

    def _gen_order(self, i, inner,manual= Block()):
        order = self.ir.orders[i]
        outer = Block()
        loop = Block()
        loop += manual
        for cr in order:
            loop += self._gen_shift(cr)
            # loop += self._gen_update(cr)
        loop += inner
        outer.for_range(f"{LS}_{i}", f"{BS}_{i}", loop)
        if i > 0:
            for cr in order:
                outer += self._gen_reload(cr)
                outer += self._gen_fetch(cr)
        return outer
    
    def _gen_nested(self):
        block = Block()
        loop_symbols = [f"{LS}_{i}" for i in range(len(self.ir.orders))]
        manual = Block()
        last_cr = self.ir.orders[-1][-1]
        start = f"{RS}_{self.ir.starts[last_cr]}"
        mid = f"{RS}_{self.ir.starts[last_cr]+len(last_cr)//2}"
        manual += s(f"{RV}[{','.join(loop_symbols)}]={_WRITE_EXPR[type(last_cr)].format(start=start,m=mid)}")
        inner = Block()
        inner += self._gen_order(len(self.ir.orders)-1, Block(), manual=manual)
        for i in range(len(self.ir.orders)-2,-1,-1 ):
            inner = self._gen_order(i, inner)
        return inner 
    
    """
    IDEA: 

    given avx/simd register lane width, we can construct a numpy vector with 
    the width the number lanes. (done right before hot loop)

    In the hot loop, everything will be elementwise on vectors in terms of operations

    """
    def _gen_nested_vectorized(self):
        pass

    def _gen_initialize(self):
        block = Block()
        for i in range(len(self.ir.tape)):
            # block += s(f"{RS}_{i}={OT}_{i} = {NumPyPrinter().doprint(self.ir.tape[i])}")
            block += s(f"{RS}_{i}={OT}_{i} = {PythonPrinter().doprint(self.ir.tape[i])}")
        return block 

    def _gen_initialize_parallel(self):
        block = Block()
        block += s(f"{CN} = t*{CK}")
        outerS = min(self.ir.st, key= lambda x:  self.ir.st[x].get("order",float('inf')))
        start,step = self.ir.st[outerS]["params"]
        # BUG: should be t * chunk * x_h, i.e., that many steps later... 

        # fixed? 
        block += s(f"{start} = {CN}*{step}")
        for i in range(len(self.ir.tape)):
            block += s(f"{RS}_{i}={OT}_{i} = {PythonPrinter().doprint(self.ir.tape[i])}")
        
        return block
    
    def generate(self):
        self.ir.prepare()
        block = Block()



        block += self._gen_initialize()
        block += self._gen_nested()
        B = [f"B_{i}" for i in range(len(self.ir.st))]
        P = []
        for symbol in self.ir.st:
            start,step = self.ir.st[symbol]["params"]
            P.append(f"{start}")
            P.append(f"{step}")

        tree = mod(fn("generated", ['A'] + P + B, block.stmts))
        ast.fix_missing_locations(tree)
        print(ast.unparse(tree))
        return tree
    
    def generate_test(self,n ):
        self.ir.prepare()
        block = Block()
        B = [f"B_{i}" for i in range(len(self.ir.st))]
        BJ = "=".join(B)
        block += s(f"{BJ} = {n}")

        for symbol in self.ir.st:
            start,step = self.ir.st[symbol]["params"]
            block += s(f"{start}=0")
            block += s(f"{step}=1")
        block += self._testgen_initialize()
        block += self._gen_nested()


        tree = mod(fn("generated", ['A'], block.stmts))
        ast.fix_missing_locations(tree)
        return tree
    
    def construct_tape(self):
        pass
    
    def _gen_order_parallel(self, i ,inner, manual = Block()):
        order = self.ir.orders[i]
        outer = Block()
        loop = Block()
        loop += manual
        for cr in order:
            loop += self._gen_shift(cr)
            #loop += self._gen_update(cr)
        loop += inner
        # if we're the first to go, i.e., first nest in the thread
        if i == 0:
            outer += s(f"{UL}={BS}_0 if t=={NT}-1 else {CN} + {CK}")#upper limit 
            outer.for_range(f"{LS}_{i}",f"{CN},{UL}", loop)
        else:
            outer.for_range(f"{LS}_{i}", f"{BS}_{i}", loop)

        if i > 0:
            for cr in order:
                outer += self._gen_reload(cr)
                outer += self._gen_fetch(cr)
        return outer

    # just a copy of the previous one for now. 
    def _gen_nested_parallel(self):
        block = Block()
        loop_symbols = [f"{LS}_{i}" for i in range(len(self.ir.orders))]
        manual = Block()
        last_cr = self.ir.orders[-1][-1]
        start = f"{RS}_{self.ir.starts[last_cr]}"
        mid = f"{RS}_{self.ir.starts[last_cr]+len(last_cr)//2}"
        manual += s(f"{RV}[{','.join(loop_symbols)}]={_WRITE_EXPR[type(last_cr)].format(start=start,m=mid)}")
        inner = Block()

        inner += self._gen_order_parallel(len(self.ir.orders)-1, Block(), manual=manual)
        for i in range(len(self.ir.orders)-2,-1,-1 ):
            inner = self._gen_order_parallel(i, inner)
        return inner 

    def generate_parallel(self):
        self.ir.prepare()
        block = Block()
        outer = Block()
        outer += s(f"{CK} = {BS}_0 // {NT}")

        block += self._gen_initialize_parallel()
        block += self._gen_nested_parallel()
        outer.for_range("t", NT, block, range="numba.prange")
        B = [f"B_{i}" for i in range(len(self.ir.st))]
        P = []
        for symbol in self.ir.st:
            start,step = self.ir.st[symbol]["params"]
            P.append(f"{start}")
            P.append(f"{step}")
        
        
        tree = mod(fn("generated", ['A'] +P+ B + [f"{NT}"], outer.stmts))
        ast.fix_missing_locations(tree)
        return tree
    
    def _testgen_initialize_parallel(self):
        block = Block()
        block += s(f"{CN} = t*{CK}")
        outerS = min(self.ir.st, key= lambda x:  self.ir.st[x].get("order",float('inf')))
        start,step = self.ir.st[outerS]["params"]
        block += s(f"{start} = {CN}")
        x0,xh, y0,yh, z0,zh = sympy.symbols("x_0 x_h y_0 y_h z_0 z_h")
        seed = {
            x0:0,
            xh:1,
            y0:0,
            yh:1,
            z0:0,
            zh:1
        }
        for i in range(len(self.ir.tape)):
            block += s(f"{RS}_{i}={OT}_{i} = {(float(self.ir.tape[i].subs(seed)))}")
        return block
    
    def _testgen_initialize(self):
        block = Block()
        x0,xh, y0,yh, z0,zh = sympy.symbols("x_0 x_h y_0 y_h z_0 z_h")
        seed = {
            x0:0,
            xh:1,
            y0:0,
            yh:1,
            z0:0,
            zh:1
        }
        for i in range(len(self.ir.tape)):
            # block += s(f"{RS}_{i}={OT}_{i} = {NumPyPrinter().doprint(self.ir.tape[i])}")
            block += s(f"{RS}_{i}={OT}_{i} = {(float(self.ir.tape[i].subs(seed)))}")
        return block 
    
    def generate_testparallel(self,n):
        self.ir.prepare()
        block = Block()
        outer = Block()
        outer += s(f"{NT} = 4")
        B = [f"B_{i}" for i in range(len(self.ir.st))]
        BJ = "=".join(B)
        outer += s(f"{BJ} = {n}")
        outer += s(f"{CK} = {BS}_0 // {NT}")

        for symbol in self.ir.st:
            start,step = self.ir.st[symbol]["params"]
            outer += s(f"{start}=0")
            outer += s(f"{step}=1")
        
        block += self._testgen_initialize_parallel()
        block += self._gen_nested_parallel()
        outer.for_range("t", NT, block, range="prange")

        
        tree = mod(fn("generated", ['A'], outer.stmts))
        ast.fix_missing_locations(tree)
        print(ast.unparse(tree))
        # print(len(ast.unparse(tree)))
        return tree




