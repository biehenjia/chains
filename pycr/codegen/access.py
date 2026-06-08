from llvmlite import ir
from .registers import *

# accessing patterns; abstracted

def access_first(regs: Registers, start, length):return regs[start]
def access_mid(regs: Registers, start, length):return regs[start+length//2]
def access_tan(regs: Registers, start, length): return regs.div(regs[start], regs[start+length//2])
def access_cot(regs: Registers, start, length): return regs.div(regs[start+length//2], regs[start])
def access_cre_add(regs: Registers, start, length): return regs.add(regs[start], regs[start+1])
def access_cre_mul(regs: Registers, start, length): return regs.mul(regs[start], regs[start+1])
def access_cre_pow(regs: Registers, start, length): return regs.pow(regs[start], regs[start+1])
def access_cre_log(regs: Registers, start, length): return regs.logab(regs[start], regs[start+1])
def access_cre_sin(regs: Registers, start, length): return regs.sin(regs[start])
def access_cre_cos(regs: Registers, start, length): return regs.cos(regs[start])
def access_cre_tan(regs: Registers, start, length): return regs.tan(regs[start])
def access_cre_cot(regs: Registers, start, length): return regs.cot(regs[start])

