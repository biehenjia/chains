import dataclasses
from ..core import *

@dataclasses.dataclass
class CRconfig:
    cr: CR
    tape_start: int = -1
    suffix_hashes: list[bytes] = dataclasses.field(default_factory=list)
    initialized: bool = False

def initialize_env(root: CR):
    env = {}
    for cr in root.postorder():
        env[cr] = CRconfig(root)
    return env