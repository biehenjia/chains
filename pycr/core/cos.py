from cr import *


@CRalgebra.defineDefault(COS)
def defaultCos(u):
    return CREcos(u )
