from llvmlite import ir
from .registers import *

def emit_access_first(builder, registers, start,  length):
    return registers[start]
def emit_access_mid(builder, registers, start, length):  
    return registers[start + length//2]
def emit_access_tan(builder, registers, start, length):  
    return builder.fdiv(registers[start], registers[start+length//2])
def emit_access_cos(builder, registers, start,length ): 
    return builder.fdiv(registers[start+length//2], registers[start])
def emit_access_creadd(builder, registers, start, length): 
    return builder.fadd(registers[start], registers[start+1])
def emit_access_cremul(builder, registers, start, length): 
    return builder.fmul(registers[start], registers[start+1])


def emit_access_crelog(builder, registers, start, length): 
    return call_intrinsic(builder, "llvm.log", )


