import dataclasses, sympy
from ..core import *

@dataclasses.dataclass
class CRconfig:
    cr: CR
    tape_start: int = -1
    suffix_hashes: list[bytes] = dataclasses.field(default_factory=list)
    initialized: bool = False
    # min is monotonic; variable ordering is nondecreasing as you go up the tree.
    # represents if hoisting is required
    least_variable: sympy.Symbol = sympy.Symbol('')

def initialize_env(root: CR):
    env = {}
    for cr in root.postorder():
        env[cr] = CRconfig(cr)
        least_variable = cr.variable
        for child in cr:
            if not isinstance(child, CRnum):
                least_variable = min(least_variable, child.variable)
        env[cr].least_variable = least_variable
    return env
