from llvmlite import ir
from typing import NamedTuple
from .registers import *

class LoopHandle(NamedTuple):
    idx: ir.PhiInstr
    header: ir.Block
    body: ir.Block
    exit: ir.Block

def begin_loop(registers: Registers, n: ir.Value)-> LoopHandle:
    builder = registers.builder
    fn = builder.function
    pre = builder.block 
    h = fn.append_basic_block("loop.h")
    b = fn.append_basic_block("loop.b")
    x = fn.append_basic_block("loop.x")
    builder.branch(h)
    builder.position_at_end(h)
    idx = builder.phi(i64, name="i")
    idx.add_incoming(ir.Constant(i64, 0), pre)
    builder.cbranch(builder.icmp_signed("<", idx, n), b, x)
    builder.position_at_end(b)
    return LoopHandle(idx, h, x)

def end_loop(regs: Registers, handle: LoopHandle) -> None:
    builder = regs.builder
    latch = builder.block
    nxt = builder.add(handle.idx, ir.Constant(i64, 1))
    handle.idx.add_incoming(nxt, latch)
    builder.branch(handle.header)
    builder.position_at_end(handle.exit)

def emit_reset(registers: Registers, start, length):
    builder = registers.builder
    constants = registers.constants
    for i in range(start, start+length):
        registers[i] = constants[i]

