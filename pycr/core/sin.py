from cr import *


@CRalgebra.defineDefault(SIN)
def defaultSin(u):
    return CREsin(u)

