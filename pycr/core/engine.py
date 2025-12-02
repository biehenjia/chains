from cr import *

def sin(arg):
    if isinstance(arg, CR):
        return arg.sin()
    else:
        return math.sin(arg)

def cos(arg):
    if isinstance(arg, CR ):
        return arg.cos()
    else:
        return math.cos(arg)

def cot(arg):
    if isinstance(arg, CR):
        return arg.cot()
    
    else:
        return math.cot(arg)

def tan(arg):
    if isinstance(arg, CR):
        return arg.tan()
    else:
        return math.tan(arg)

def exp(arg):
    if isinstance(arg, CR):
        return arg.exp()
    else:
        return math.exp(arg)

def log(arg):
    if isinstance(arg, CR):
        return arg.log()
    else:
        return math.log(arg)

