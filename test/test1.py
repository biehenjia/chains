from pycr import chainify

cr, symbol_table = chainify("x**2+sin(x)+4")

print(cr)
print(symbol_table)