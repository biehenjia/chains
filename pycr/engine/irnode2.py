from ..core import *

class IR:

    def __init__(self, cr, st ):
        self.cr = cr
        self.st = st
        
        self.starts = {}
        self.orders = []

    def postorder(self):
        return self.cr.postorder()
    
    def cse(self):
        pass