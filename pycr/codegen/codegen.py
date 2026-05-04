from core import *

def generate_shift(cr):
    
    if isinstance(CRsum):
        pass

    elif isinstance(CRprod):
        pass


def generate_shift_vectorized(crterm):
    pass

def generate_parallel_shift(crterm):
    pass

def generate_initialize(crterm):
    pass


def begin_fn(self, arg_types, name="kernel", ret_type=None, arg_names=None):
    return self.setup_function(arg_types, name=name, ret_type=ret_type, arg_names=arg_names)


class Reg:
    def __init__(self, kb, slot, name):
        self.kb = kb
        self.slot = slot
        self.name = name

    def load(self):
        return self.kb.builder.load(self.slot, name=f"{self.name}_v")

    def store(self, val):
        self.kb.builder.store(val, self.slot)