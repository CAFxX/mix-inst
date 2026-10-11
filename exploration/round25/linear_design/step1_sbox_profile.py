#!/usr/bin/env python3
"""Step 1: S-box bit profiles from the QM-minimized boolean equations.
Computes per-output-bit boolean depth (unit-delay: AND/OR=1u, NOT=0u),
input dependency sets, and verifies against the S-box table."""
import json

# S-box table
S = [0,1,2,3,4,6,8,11,13,9,7,15,12,10,5,14]

# Boolean equations from rtl.v (nibble 0; identical for all nibbles).
# s[b] in terms of t[0..3]; t[3]=MSB, t[0]=LSB. s[3]=MSB, s[0]=LSB.
# Each equation: list of product terms; each term: list of (var_index, is_negated).
EQS = {
    0: [[(2,True),(3,False)], [(0,False),(2,True)], [(0,True),(1,False),(3,False)], [(0,False),(1,False),(3,True)]],
    1: [[(0,False),(2,False)], [(1,False),(2,True)]],
    2: [[(0,True),(3,False)], [(1,False),(3,False)], [(1,True),(2,False),(3,True)]],
    3: [[(0,False),(3,False)], [(1,False),(2,False),(3,True)], [(1,True),(3,False)]],
}

def eval_eq(terms, t):
    # t: list of 4 bits [t0,t1,t2,t3]
    out = 0
    for term in terms:
        v = 1
        for (vi, neg) in term:
            b = t[vi]
            if neg: b = 1 - b
            v &= b
        out |= v
    return out

def verify():
    for x in range(16):
        t = [(x >> i) & 1 for i in range(4)]  # t0=LSB
        y = 0
        for b in range(4):
            y |= (eval_eq(EQS[b], t) << b)
        assert y == S[x], f"mismatch at {x}: got {y}, want {S[x]}"
    print("equations verified against S-box table: OK")

def sop_depth(terms):
    # unit-delay: AND_k = ceil(log2(k)), OR_m = ceil(log2(m)), NOT = 0
    import math
    and_depths = [math.ceil(math.log2(len(term))) if len(term) > 1 else 0 for term in terms]
    or_depth = math.ceil(math.log2(len(terms))) if len(terms) > 1 else 0
    return max(and_depths) + or_depth, max(and_depths), or_depth

def deps(terms):
    d = set()
    for term in terms:
        for (vi, neg) in term:
            d.add(vi)
    return sorted(d)

if __name__ == "__main__":
    verify()
    import math
    profile = {}
    for b in range(4):
        terms = EQS[b]
        total, ad, od = sop_depth(terms)
        d = deps(terms)
        # count literal occurrences per input (influence weight)
        infl = {i: sum(1 for term in terms for (vi, neg) in term if vi == i) for i in range(4)}
        profile[b] = {"depth_u": total, "and_depth": ad, "or_depth": od,
                      "deps": d, "n_terms": len(terms),
                      "influence": infl}
        print(f"s[{b}]: depth={total}u (AND{ad}+OR{od}), terms={len(terms)}, deps={d}, infl={infl}")
    json.dump(profile, open("sbox_bit_profile.json", "w"), indent=1)
    print("wrote sbox_bit_profile.json")
