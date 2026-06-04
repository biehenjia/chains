from llvmlite import ir
from .registers import *

# accessing patterns; abstracted

def access_first(registers: Registers, start, length):return registers[start]
def access_mid(registers: Registers, start, length):return registers[start+length//2]
def access_tan(registers: Registers, start, length): return registers.div(registers[start], registers[start+length//2])
def access_cot(registers: Registers, start, length): return registers.div(registers[start+length//2], registers[start])
def access_cre_add(registers: Registers, start, length): return registers.add(registers[start], registers[start+1])
def access_cre_mul(registers: Registers, start, length): return registers.mul(registers[start], registers[start+1])
def access_cre_pow(registers: Registers, start, length): return registers.pow(registers[start], registers[start+1])
def access_cre_log(registers: Registers, start, length): return registers.logab(registers[start], registers[start+1])
def access_cre_sin(registers: Registers, start, length): return registers.sin(registers[start])
def access_cre_cos(registers: Registers, start, length): return registers.cos(registers[start])
def access_cre_tan(registers: Registers, start, length): return registers.tan(registers[start])
def access_cre_cot(registers: Registers, start, length): return registers.cot(registers[start])
