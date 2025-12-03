import math, sys, hashlib
import struct
from enum import IntEnum, auto

EPSILON = sys.float_info.epsilon

class Operator(IntEnum):
    
    ADD = auto()
    MUL = auto()
    POW = auto()
    DIV = auto()

    SIN = auto()
    COS = auto()
    TAN = auto()
    COT = auto()

    EXP = auto()
    LOG = auto()

PROTOCOL = hashlib.blake2b



