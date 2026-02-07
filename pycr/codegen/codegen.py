from .dsl import *



'''
Generates a code block that fetches from a list of parents. 

'''
def gen_fetch(crterm, register_symbol = "r"):
    block = []
    for write, source, read in crterm.updates:
        location = source.start + read 
        block.append(assign(v(f"{register_symbol}{read}"), v(f"{register_symbol}{location}")))
    return block


def gen_shift():
    pass