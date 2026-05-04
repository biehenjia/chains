from llvmlite import ir, binding
import ctypes


i64 = ir.IntType(64)
f64 = ir.DoubleType()


class LLVMKernelBuilder:

    def __init__(self, name, scalar_type=f64, vector_width=None):
        self.scalar_type = scalar_type
        self.vector_width = vector_width
        self.dtype = (
            ir.VectorType(scalar_type, vector_width) if vector_width else scalar_type
        )
        self.module = ir.Module(name=name)
        self.fn = None
        self.builder = None
        self.val_table = {}


    def setup_function(self, arg_types, name="kernel", ret_type=None, arg_names=None):
        ret_type = ret_type or ir.VoidType()
        fn_type = ir.FunctionType(ret_type, arg_types)
        self.fn = ir.Function(self.module, fn_type, name=name)
        if arg_names:
            for arg, nm in zip(self.fn.args, arg_names):
                arg.name = nm
        entry = self.fn.append_basic_block("entry")
        self.builder = ir.IRBuilder(entry)
        return self.fn.args


    def emit_for(self, start, stop, body_fn, carried=None, step=1):

        carried = carried or []
        entry_block = self.builder.block

        header = self.fn.append_basic_block("loop_header")
        body = self.fn.append_basic_block("loop_body")
        exit_b = self.fn.append_basic_block("loop_exit")

        self.builder.branch(header)

        self.builder.position_at_end(header)
        i_phi = self.builder.phi(i64, name="i")
        i_phi.add_incoming(start, entry_block)

        carried_phis = []
        for init_val, phi_name in carried:
            phi = self.builder.phi(init_val.type, name=phi_name)
            phi.add_incoming(init_val, entry_block)
            carried_phis.append(phi)

        cond = self.builder.icmp_signed("<", i_phi, stop, name="loop_cond")
        self.builder.cbranch(cond, body, exit_b)

        self.builder.position_at_end(body)
        updated = body_fn(i_phi, carried_phis) or []
        if len(updated) != len(carried_phis):
            raise ValueError(
                f"body_fn returned {len(updated)} values but {len(carried_phis)} were carried"
            )
        i_next = self.builder.add(i_phi, ir.Constant(i64, step), name="i_next")

        body_end = self.builder.block
        i_phi.add_incoming(i_next, body_end)
        for phi, updated_val in zip(carried_phis, updated):
            phi.add_incoming(updated_val, body_end)
        self.builder.branch(header)

        self.builder.position_at_end(exit_b)
        return carried_phis

    _BINOPS = {
        "+": "fadd",
        "-": "fsub",
        "*": "fmul",
        "/": "fdiv",
    }

    def emit_binop(self, op, lhs, rhs, name=""):
        return getattr(self.builder, self._BINOPS[op])(lhs, rhs, name=name)

    def add(self, a, b, name=""):
        return self.builder.fadd(a, b, name=name)

    def sub(self, a, b, name=""):
        return self.builder.fsub(a, b, name=name)

    def mul(self, a, b, name=""):
        return self.builder.fmul(a, b, name=name)

    def div(self, a, b, name=""):
        return self.builder.fdiv(a, b, name=name)

    def neg(self, a, name=""):
        return self.builder.fneg(a, name=name)


    def _intrinsic_suffix(self, dtype):
        if isinstance(dtype, ir.VectorType):
            scalar = dtype.element
            if scalar == ir.DoubleType():
                return f"v{dtype.count}f64"
            if scalar == ir.FloatType():
                return f"v{dtype.count}f32"
        else:
            if dtype == ir.DoubleType():
                return "f64"
            if dtype == ir.FloatType():
                return "f32"
        raise NotImplementedError(f"intrinsic suffix for {dtype}")

    def _get_or_declare(self, intr_name, fntype):
        if intr_name in self.module.globals:
            return self.module.globals[intr_name]
        return ir.Function(self.module, fntype, name=intr_name)

    def emit_intrinsic(self, name, args, name_hint=""):
        dtype = args[0].type
        intr_name = f"llvm.{name}.{self._intrinsic_suffix(dtype)}"
        fntype = ir.FunctionType(dtype, [a.type for a in args])
        fn = self._get_or_declare(intr_name, fntype)
        return self.builder.call(fn, args, name=name_hint)

    def sin(self, a, name=""):
        return self.emit_intrinsic("sin", [a], name_hint=name)

    def cos(self, a, name=""):
        return self.emit_intrinsic("cos", [a], name_hint=name)

    def fma(self, a, b, c, name=""):
        return self.emit_intrinsic("fmuladd", [a, b, c], name_hint=name)

    def emit_load(self, ptr, idx, vector=False, name=""):
        if vector:
            if not self.vector_width:
                raise ValueError("emit_load(vector=True) needs a vector_width")
            scaled = self.builder.mul(
                idx, ir.Constant(i64, self.vector_width), name="vec_idx"
            )
            scalar_gep = self.builder.gep(ptr, [scaled], inbounds=True)
            vec_ptr_ty = ir.PointerType(self.dtype)
            vec_ptr = self.builder.bitcast(scalar_gep, vec_ptr_ty)
            return self.builder.load(vec_ptr, name=name)
        gep = self.builder.gep(ptr, [idx], inbounds=True)
        return self.builder.load(gep, name=name)

    def emit_store(self, ptr, idx, val, vector=False):
        if vector:
            if not self.vector_width:
                raise ValueError("emit_store(vector=True) needs a vector_width")
            scaled = self.builder.mul(
                idx, ir.Constant(i64, self.vector_width), name="vec_idx"
            )
            scalar_gep = self.builder.gep(ptr, [scaled], inbounds=True)
            vec_ptr_ty = ir.PointerType(val.type)
            vec_ptr = self.builder.bitcast(scalar_gep, vec_ptr_ty)
            self.builder.store(val, vec_ptr)
            return
        gep = self.builder.gep(ptr, [idx], inbounds=True)
        self.builder.store(val, gep)

    def emit_const(self, val, dtype=None):
        return ir.Constant(dtype or self.dtype, val)

    def emit_const_i(self, val):
        return ir.Constant(i64, val)

    def emit_constants_static(self, tape_vals):
        for i, val in enumerate(tape_vals):
            self.val_table[i] = self.emit_const(val)

    def emit_constants_dynamic(self, tape_args):
        for i, arg in enumerate(tape_args):
            self.val_table[i] = arg


    def ret(self, val=None):
        if val is None:
            self.builder.ret_void()
        else:
            self.builder.ret(val)


    def compile(self, opt_level=2):
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine(opt=opt_level)
        mod = binding.parse_assembly(str(self.module))
        mod.verify()
        engine = binding.create_mcjit_compiler(mod, target_machine)
        engine.finalize_object()
        engine.run_static_constructors()
        self._engine = engine
        self._target_machine = target_machine
        self._compiled_mod = mod
        return self

    def get_fn_ptr(self, name, cfunc_type):
        addr = self._engine.get_function_address(name)
        return cfunc_type(addr)

    def dump(self):
        print(self.module)

    def dump_asm(self):
        print(self._target_machine.emit_assembly(self._compiled_mod))