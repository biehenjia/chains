# init PURPOSE:
# given an AST from api, and core algebra,
# we construct the CR tree, 

from .crmake import *
from .term import *

__all__ = ['crmake', 'CRterm']
