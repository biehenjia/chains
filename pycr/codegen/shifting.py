# vector/scalar agnostic

from llvmlite import ir
from .registers import *

def emit_sum_shift(regs:Registers, start, length):
    for i in range(start, start+length -1): regs[i] = regs.add(regs[i], regs[i+1])

def emit_crprod_shift(regs: Registers, start, length):
    for i in range(start, start+length -1): regs[i] = regs.mul(regs[i], regs[i+1])

def emit_crtrig_shift(regs: Registers, start, length):
    t = length//2 
    for i in range(t-1):
        ri, ri1 = regs[start+i], regs[start+i+1]
        rti, rti1 = regs[start+t+i], regs[start+t+i+1]
        a = regs.fma(ri, rti1, regs.mul(rti, ri1))
        b = regs.fma(rti, rti1, regs.neg(regs.mul(ri, ri1)))
        regs[start+i] = a
        regs[start+t+i] = b