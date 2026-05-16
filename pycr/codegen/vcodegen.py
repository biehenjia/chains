from .api import *


EMITTERS = { 
    "CRsum": emit_vcrsum,
    "CRtrig": emit_vcrtrig,
    "CRprod": emit_crprod,
}


'''
GENERAL TODO: 
0. re-implement parallelization 
1. add vectorization (4 lane, etc.) & striding
2. add CSE support

'''