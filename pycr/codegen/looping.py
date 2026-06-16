from llvmlite import ir
from typing import NamedTuple
from .registers import Registers
from .intrinsics import i64

class LoopHandle(NamedTuple):
    idx: ir.PhiInstr
    header: ir.Block
    exit: ir.Block
    stride: int

def begin_loop(regs: Registers, n: ir.Value, stride: int = 1) -> LoopHandle:
    """
    Constructs a loop given a registers object and returns the exit latch.

    :type regs: Registers
    :type n: ir.Value
    :type stride: int
    :rtype: LoopHandle
    """
    builder = regs.builder
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
    regs.indices.append(idx)
    return LoopHandle(idx, h, x, stride)

def end_loop(regs: Registers, handle: LoopHandle) -> None:
    """
    Closes the loop at a given LoopHandle latch.
    
    :type regs: Registers
    :type handle: LoopHandle
    """
    builder = regs.builder
    latch = builder.block
    nxt = builder.add(handle.idx, ir.Constant(i64, handle.stride))
    handle.idx.add_incoming(nxt, latch)
    builder.branch(handle.header)
    builder.position_at_end(handle.exit)
    regs.indices.pop()

