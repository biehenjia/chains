# vector/scalar agnostic

from llvmlite import ir
from .registers import *

def emit_sum_shift(registers:Registers, start, length):
    for i in range(start, start+length -1):
        registers[i] = registers.add(registers[i], registers[i+1])

def emit_crprod_shift(registers: Registers, start, length):
    for i in range(start, start+length -1):
        registers[i] = registers.mul(registers[i], registers[i+1])

def emit_crtrig_shift(registers: Registers, start, length):
    t = length//2 
    for i in range(t-1):
        ri, ri1 = registers[start+i], registers[start+i+1]
        rti, rti1 = registers[start+t+i], registers[start+t+i+1]
        a = registers.fma(ri, rti1, registers.mul(rti, ri1))
        b = registers.fma(rti, rti1, registers.neg(registers.mul(ri, ri1)))
        registers[start+i] = a
        registers[start+t+i] = b



