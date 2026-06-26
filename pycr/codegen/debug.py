from llvmlite import ir

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
):
    parts: list[str] = []

    if dump_ir:
        parts.append(f"=== unoptimized IR ({func_name}) ===")
        parts.append(str(module))

    tm = make_target_machine(cpu=cpu, features=features)
    llvm_mod = parse_module(module, tm)

    if verify_only:
        return None, "\n".join(parts)

    if not skip_optimize:
        optimize(llvm_mod, tm, pto)

    if dump_opt_ir:
        parts.append(f"=== optimized IR ({func_name}) ===")
        parts.append(str(llvm_mod))

    if dump_asm:
        parts.append(f"=== assembly ({func_name}) ===")
        parts.append(tm.emit_assembly(llvm_mod))

    return jit_link(llvm_mod, tm, func_name, n_dims), "\n".join(parts)
