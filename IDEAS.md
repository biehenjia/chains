Architecture/ layout:

Input is some string + symbol table or some python code. 

1. String -> SymPy parsing + simplification
2. Walk the SymPy syntax tree and evaluate under CR algebra
3. CSE the CR
4. Lower the CR into an ICR version that contains metainfo such as register regions, order, etc.
5. 
6. Generate LLVM of the ICR, then optimize with O2/O3, return.


Symbol table was previously passed along, there is not much to do with the symbol table really, 

ordering can be done automatically by lexicographic comparison. 

EXPERIMENTS:

1. investigate impact of reordering order of computation within variables, we know that this matters, but to what degree does it matter in the CR paradigm
2. Investigate the difference in generated LLVM via numba and hand roll, hope is that we can maybe achieve order of magnitude in comparison against numba 

hello hello i am talking from the other window right now is this thing live editing? or is it opening a copy type thing 
