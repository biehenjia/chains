from ..core import *
import hashlib 

from sympy import srepr


# PARENT READS FROM CHILD LOCATION. DON'T NEED TO STORE PARENT INFORMATION.
# LET CRE have an update position in the tape.
class CRterm:

    def __init__(self, cr):
        self.cr = cr
        self.dependencies = {cr.order, }
    
        
    def postorder(self):
        
