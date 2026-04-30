from ..core import *

# purpose
'''
After constructing the CR tree, they each have CRterm wrappers that hold 
metadata about the CR before we convert it it into the relevant code generation


''' 
class CRterm:

    def __init__(self,cr):
        self.cr = cr
        self.trunc = len(cr)
    
    
    