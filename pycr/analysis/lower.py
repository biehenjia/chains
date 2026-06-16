import sympy

from ..core import CR
from ..crconfig import initialize_env
from ..program import Program
from .scheduler import construct_tape, vectorize_tape, extract_symbols, partition_orders
from .subexpressions import prepare_cse, cse


def lower(cr: CR, width: int = 1) -> Program:
    """
    Lowers the CR to a program level.

    :type cr: CR
    :type width: int
    :rtype: Program
    """
    env = initialize_env(cr)
    prepare_cse(env, cr)
    cr = cse(env, {}, cr)
    env = initialize_env(cr)

    symbols = extract_symbols(cr)
    tape = construct_tape(env, cr)

    if width > 1:
        inner = max(symbols, key=str)
        tape = vectorize_tape(
            tape,
            sympy.Symbol(f"{inner.name}_0"),
            sympy.Symbol(f"{inner.name}_h"),
            width,
        )

    traces_byorder = partition_orders(env, cr)
    return Program(
        cr=cr,
        env=env,
        symbols=symbols,
        tape=tape,
        traces_byorder=traces_byorder,
        width=width,
    )
