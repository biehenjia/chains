import math, sys, hashlib
import struct

EPSILON = sys.float_info.epsilon
OPERATOR_NAMES = ["ADD", "MUL", "POW", "DIV",
                  "SIN", "COS", "COT", "TAN",
                  "EXP", "LOG", ]

PROTOCOL = hashlib.blake2b

for i, name in enumerate(OPERATOR_NAMES):
    globals()[name] = i + 1


