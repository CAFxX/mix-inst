#!/usr/bin/env python3
"""SAT bijectivity test for F(x) = L(x) ^ N(x).
Encodes two copies, constrains F(x)=F(y) and x!=y. UNSAT => bijective.
Uses python-sat (Glucose3).
"""
import sys
from pysat.solvers import Glucose3

# L offsets (weight-5 circulant): l_i = x_i ^ x_{i+14} ^ x_{i+27} ^ x_{i+40} ^ x_{i+52}
L_OFF = [0, 14, 27, 40, 52]
# N offsets: n_i = (x_{i+6}&x_{i+37}) ^ (x_{i+14}&x_{i+44}) ^ (x_{i+23}&x_{i+52}) ^ (x_{i+30}&x_{i+62})
N_PAIRS = [(6,37),(14,44),(23,52),(30,62)]

class Encoder:
    def __init__(self):
        self.clauses = []
        self.var_count = 0
    def new_var(self):
        self.var_count += 1
        return self.var_count
    def add(self, clause):
        self.clauses.append(clause)
    def AND(self, a, b):
        """c = a & b. Returns c."""
        c = self.new_var()
        self.add([-a, -b, c]); self.add([a, -c]); self.add([b, -c])
        return c
    def XOR2(self, a, b):
        """c = a ^ b. Returns c."""
        c = self.new_var()
        self.add([-a, -b, -c]); self.add([a, b, -c])
        self.add([a, -b, c]); self.add([-a, b, c])
        return c
    def XOR_list(self, vs):
        r = vs[0]
        for v in vs[1:]:
            r = self.XOR2(r, v)
        return r

def build_F(enc, x):
    """x: list of 64 input vars. Returns list of 64 output vars for F."""
    # L
    l = []
    for i in range(64):
        terms = [x[(i+o) % 64] for o in L_OFF]
        l.append(enc.XOR_list(terms))
    # N
    n = []
    for i in range(64):
        ands = [enc.AND(x[(i+a) % 64], x[(i+b) % 64]) for (a,b) in N_PAIRS]
        n.append(enc.XOR_list(ands))
    # F = L ^ N
    f = [enc.XOR2(l[i], n[i]) for i in range(64)]
    return f

def main():
    enc = Encoder()
    x = [enc.new_var() for _ in range(64)]
    y = [enc.new_var() for _ in range(64)]
    fx = build_F(enc, x)
    fy = build_F(enc, y)
    # F(x) = F(y)
    for i in range(64):
        v = enc.XOR2(fx[i], fy[i])
        enc.add([-v])  # fx[i] == fy[i]
    # x != y : OR_i (x_i ^ y_i)
    diffs = [enc.XOR2(x[i], y[i]) for i in range(64)]
    enc.add(diffs)  # at least one differs
    print(f"CNF: {enc.var_count} vars, {len(enc.clauses)} clauses", flush=True)
    with Glucose3() as solver:
        for c in enc.clauses:
            solver.add_clause(c)
        sat = solver.solve()
        print("SAT (collision exists => NOT bijective)" if sat else "UNSAT (bijective!)", flush=True)
        return 0 if not sat else 1

if __name__ == "__main__":
    sys.exit(main())
