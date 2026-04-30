from llvmlite import ir, binding
import ctypes 



i64 = ir.IntType(64)
f64 = ir.DoubleType()

class LLVMKernelBuilder:

    def __init__(self, name, scalar_type=f64, vector_width=None):
        self.scalar_type = scalar_type
        self.vector_width = vector_width
        self.dtype = ir.VectorType(scalar_type, vector_width) if vector_width else scalar_type
        self.module = ir.Module(name=name)
        self.fn = None
        self.builder = None
        self.val_table = {}
        

    def setup_function(self, arg_types, name="kernel"):
        fn_type = ir.FunctionType(ir.VoidType(), arg_types)
        self.fn = ir.Function(self.module, fn_type, name=name)
        entry = self.fn.append_basic_block("entry")
        self.builder = ir.IRBuilder(entry)
        return self.fn.args
    
    def emit_for(self, start, stop, body_fn, carried= None):
        carried = carried or []
        entry_block = self.builder.block

        header = self.fn.append_basic_block("loop_header")
        body = self.fn.append_basic_block("loop_body")
        latch = self.fn.append_basic_block("loop_latch")
        exit_b = self.fn.append_basic_block("loop_exit")

        self.builder.branch(header)
        self.builder.position_at_end(header)
        i = self.builder.phi(i64, name="i")
        i.add_incoming(start, entry_block)

        carried_phis = []
        for init_val, phi_name in carried:
            phi = self.builder.phi(init_val.type, name=phi_name)
            phi.add_incoming(init_val, entry_block)
            carried_phis.append(phi)
        
        cond = self.builder.icmp_signed("<",i,stop)
        self.builder.cbranch(cond, body, exit_b)

        self.builder.position_at_end(body)
        updated = body_fn(i,carried_phis)
        self.builder.branch(latch)

        self.builder.position_at_end(latch)
        i_next = self.builder.add(i,ir.Constant(i64,1))
        i.add_incoming(i_next, latch)

        for phi, updated_val in zip(carried_phis, updated):
            phi.add_incoming(updated_val, latch)
        self.builder.branch(header)

        self.builder.position_at_end(exit_b)
        return carried_phis

    # can we use magic here? how to lower friction
    def emit_binop(self, op, lhs, rhs):
        return { 
            "+": self.builder.fadd,
            "*": self.builder.fmul,
            "-": self.builder.fsub,
            "/": self.builder.fdiv
        }[op](lhs,rhs)


    def add(self, a, b ):
        return self.builder.fadd(a,b)
    
    def mul(self, a,b):
        return self.builder.fmul(a,b)
    
    def sub(self, a, b):
        return self.builder.fsub(a,b)
    
    def div(self, a, b):
        return self.builder.fdiv(a,b)
    
    def sin(self, a):
        return self.emit_intrinsic("sin", [a])
    
    def cos(self, a):
        return self.emit_intrinsic("cos", [a])
    
    def emit_intrinsic(self, name, args):
        dtype = args[0].type
        suffix = f"v{self.vector_width}f64" if self.vector_width else "f64"
        intr_name = f"llvm.{name}.{suffix}"
        fntype = ir.FunctionType(dtype, [dtype])
        if intr_name not in self.module.globals:
            fn = ir.Function(self.module, fntype, name=intr_name)
        else:
            fn = self.module.globals[intr_name]
        return self.builder.call(fn, args)
    
    def emit_load(self, ptr, idx):
        if self.vector_width:
            scaled_idx = self.builder.mul(idx, ir.Constant(i64, self.vector_width))
        else:
            scaled_idx = idx
        gep = self.builder.gep(ptr, [scaled_idx], inbounds=True)
        return self.builder.load(gep)

    def emit_store(self, ptr, idx, val):
        if self.vector_width:
            scaled_idx = self.builder.mul(idx, ir.Constant(i64, self.vector_width))
        else:
            scaled_idx = idx
        gep = self.builder.gep(ptr, [scaled_idx], inbounds=True)
        self.builder.store(val, gep)

    def emit_constants_static(self, tape_vals):
        for i, val in enumerate(tape_vals):
            self.val_table[i] = self.emit_const(val)

    def emit_constants_dynamic(self, tape_args):
        for i, arg in enumerate(tape_args):
            self.val_table[i] = arg
    
    def emit_const_i(self, val):
        return ir.Constant(i64, val)
    
    def ret(self, val=None):
        if val is None:
            self.builder.ret_void()
        else:
            self.builder.ret(val)

    def compile(self):
        binding.initialize_native_target()
        binding.initialize_native_asmprinter()
        target = binding.Target.from_default_triple()
        target_machine = target.create_target_machine()
        mod = binding.parse_assembly(str(self.module))
        mod.verify()
        engine = binding.create_mcjit_compiler(mod, target_machine)
        engine.finalize_object()
        engine.run_static_constructors()
        self._engine = engine
        return self
    
    def get_fn_ptr(self, name, cfunc_type):
        addr = self._engine.get_function_address(name)
        return cfunc_type(addr)
    
    def dump(self):
        print(self.module)

    def fma(self, a, b, c):
        suffix = f"v{self.vector_width}f64" if self.vector_width else "f64"
        intr_name = f"llvm.fmuladd.{suffix}"
        fntype = ir.FunctionType(self.dtype, [self.dtype, self.dtype, self.dtype])
        if intr_name not in self.module.globals:
            fn = ir.Function(self.module, fntype, name=intr_name)
        else:
            fn = self.module.globals[intr_name]
        return self.builder.call(fn, [a, b, c])
    
