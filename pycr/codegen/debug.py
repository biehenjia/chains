import sys
from llvmlite import ir
import llvmlite.binding as llvm

from .compile import make_target_machine, parse_module, optimize, jit_link


def compile_fn_debug(
    module: ir.Module,
    func_name: str,
    n_dims: int,
    *,
    cpu: str | None = None,
    features: str = "",
    pto=None,
    dump_ir: bool = True,
    dump_opt_ir: bool = True,
    dump_asm: bool = False,
    skip_optimize: bool = False,
    verify_only: bool = False,
    stream=sys.stderr,
):
    if dump_ir:
        print(f"=== unoptimized IR ({func_name}) ===", file=stream)
        print(str(module), file=stream)

    tm = make_target_machine(cpu=cpu, features=features)
    llvm_mod = parse_module(module, tm)

    if verify_only:
        return None

    if not skip_optimize:
        optimize(llvm_mod, tm, pto)

    if dump_opt_ir:
        print(f"=== optimized IR ({func_name}) ===", file=stream)
        print(str(llvm_mod), file=stream)

    if dump_asm:
        print(f"=== assembly ({func_name}) ===", file=stream)
        print(tm.emit_assembly(llvm_mod), file=stream)

    return jit_link(llvm_mod, tm, func_name, n_dims)
