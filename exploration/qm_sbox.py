"""QM minimization + ANF analysis of the PRESENT 4-bit S-box (round 3, lever a).

PRESENT S-box: C 5 6 B 9 0 A D 3 E F 8 4 7 1 2
Computes exact minimal SOP (Quine-McCluskey, 4 vars = trivial) and the ANF
(Moebius) for each output bit, then prints candidate Verilog encodings.
"""
from itertools import combinations

SBOX = [0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2]

def minterms_of(bit):
    return [v for v in range(16) if (SBOX[v] >> bit) & 1]

def qm_minimize(minterms):
    """Exact minimal SOP (fewest product terms, then fewest literals) for 4-var function."""
    # prime implicants via QM
    def combine(a, b):
        # a,b are (mask, bits); mask=1 means don't-care position
        if a[0] != b[0]:  # identical don't-care sets required for adjacency
            return None
        diff = a[1] ^ b[1]
        if diff & (diff - 1):  # more than one bit differs
            return None
        if a[0] & diff:  # differ in a don't-care position
            return None
        return (a[0] | diff, a[1] & ~diff)
    cur = {(0, m) for m in minterms}
    primes = set()
    while cur:
        nxt = set(); used = set()
        cl = list(cur)
        for i in range(len(cl)):
            for j in range(i+1, len(cl)):
                c = combine(cl[i], cl[j])
                if c:
                    used.add(cl[i]); used.add(cl[j]); nxt.add(c)
        primes |= (cur - used)
        cur = nxt
    # essential prime implicant cover (exact, brute force over primes)
    primes = list(primes)
    def covers(p, m):
        return (m & ~p[0]) == p[1]
    # greedily essential, then brute-force the rest
    uncovered = set(minterms)
    chosen = []
    # essential primes
    while True:
        essential = None
        for m in uncovered:
            cov = [p for p in primes if covers(p, m)]
            if len(cov) == 1:
                essential = cov[0]; break
        if essential is None: break
        chosen.append(essential)
        uncovered -= {m for m in uncovered if covers(essential, m)}
    rest = [p for p in primes if p not in chosen]
    best = None
    for r in range(len(rest)+1):
        for combo in combinations(rest, r):
            if all(any(covers(p, m) for p in list(combo)+chosen) for m in uncovered):
                cost = (len(combo), sum(bin(p[0]^0xF).count("1") for p in combo))
                if best is None or cost < best[0]:
                    best = (cost, combo)
        if best is not None and best[0][0] == r:
            break
    chosen += list(best[1]) if best else []
    return chosen

def cube_str(p, names):
    mask, bits = p
    lits = []
    for j in range(4):
        if not (mask >> j) & 1:
            lits.append(names[j] if (bits >> j) & 1 else "(~%s)" % names[j])
    return "&".join(lits) if lits else "1'b1"

def anf_of(minterms):
    """ANF coefficients via Moebius over GF(2); returns list of monomial masks."""
    f = [1 if v in minterms else 0 for v in range(16)]
    # Moebius: for each var j, for each v with bit j set: f[v] ^= f[v ^ (1<<j)]
    for j in range(4):
        for v in range(16):
            if (v >> j) & 1:
                f[v] ^= f[v ^ (1 << j)]
    return [v for v in range(16) if f[v]]

def mon_str(m, names):
    if m == 0: return "1'b1"
    return "&".join(names[j] for j in range(4) if (m >> j) & 1)

names = ["x0", "x1", "x2", "x3"]
for bit in range(4):
    mt = minterms_of(bit)
    primes = qm_minimize(mt)
    sop = " | ".join("(%s)" % cube_str(p, names) for p in primes)
    nlit = sum(bin(p[0] ^ 0xF).count("1") for p in primes)
    anf = anf_of(mt)
    anf_s = " ^ ".join(mon_str(m, names) for m in anf) if anf else "1'b0"
    deg = max(bin(m).count("1") for m in anf) if anf else 0
    print(f"bit{bit}: minterms={mt}")
    print(f"  min-SOP ({len(primes)} cubes, {nlit} lits): {sop}")
    print(f"  ANF ({len(anf)} monomials, deg {deg}): {anf_s}")
    print()
