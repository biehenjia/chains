import dataclasses, sympy
from .core import CR, CRnum, CRsum, CRprod, CRtrig

@dataclasses.dataclass
class CRconfig:
    cr: CR
    tape_start: int = -1
    suffix_hashes: list[bytes] = dataclasses.field(default_factory=list)
    initialized: bool = False
    # min is monotonic; variable ordering is nondecreasing as you go up the tree.
    # represents if hoisting is required
    least_variable: sympy.Symbol = sympy.Symbol('')
    # axis names whose chain-type shifts mutate any slot in this subtree —
    # used to decide whether a connector's value can change at a given axis
    touched_axes: set[str] = dataclasses.field(default_factory=set)

def initialize_env(root: CR):
    env: dict[CR, CRconfig] = {}

    for cr in root.postorder():
        env[cr] = CRconfig(cr)
        least_variable = cr.variable
        touched: set[str] = set()
        if isinstance(cr, (CRsum, CRprod, CRtrig)):
            touched.add(cr.variable.name)
        if not isinstance(cr, CRnum):
            for child in cr:
                if not isinstance(child, CRnum):
                    least_variable = min(least_variable, child.variable, key=str)
                touched |= env[child].touched_axes
        env[cr].least_variable = least_variable
        env[cr].touched_axes = touched
    return env
