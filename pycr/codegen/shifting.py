from llvmlite import ir
from .registers import *

def emit_sum_shift(builder: ir.IRBuilder, registers: Registers, start,  length):
    for i in range(start, start+length-1):
        registers[i] = builder.fadd(registers[i], registers[i+1])
    
def emit_crprod_shift(builder: ir.IRBuilder, registers: Registers, start, length):
    for i in range(start, start+length-1):
        registers[i] = builder.fmul(registers[i], registers[i+1])

def emit_crtrig_shift(builder: ir.IRBuilder, registers: Registers, start, length):
    t = length//2
    for i in range(t-1):
        ri = registers[start+i]
        ri1 = registers[start+i+1]
        rti = registers[start+t+i]
        rti1 = registers[start+t+i+1]
        a = builder.call(fma, [i, rti1, builder.fmul(rti, ri1)])
        b = builder.call(fma, [rti, rti1, builder.fneg(builder.fmul(ri,ri1))])
        registers[start+i] = a
        registers[start+t+i] = b

