"""S-box encoding shootout: which PRESENT S-box circuit maps to lowest delay?

Python expr conventions (must eval correctly on 0/1 ints in verify()):
  & = AND, | = OR, ^ = XOR, (1-x) = NOT.
Verilog conversion: (1-<e>) -> (~<e>); & | ^ pass through.
"""
import os, re, subprocess, sys
from itertools import combinations

EXP = "/home/hatch/workspace/mix/exploration"
SBOX = [0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2]

def qm_minimize(minterms):
    def combine(a, b):
        if a[0] != b[0]: return None  # identical don't-care sets required
        diff = a[1] ^ b[1]
        if diff & (diff - 1): return None
        if a[0] & diff: return None
        return (a[0] | diff, a[1] & ~diff)
    cur = {(0, m) for m in minterms}
    primes = set()
    while cur:
        nxt = set(); used = set()
        cl = list(cur)
        for i in range(len(cl)):
            for j in range(i+1, len(cl)):
                c = combine(cl[i], cl[j])
                if c: used.add(cl[i]); used.add(cl[j]); nxt.add(c)
        primes |= (cur - used); cur = nxt
    primes = list(primes)
    def covers(p, m): return (m & ~p[0]) == p[1]
    uncovered = set(minterms); chosen = []
    while True:
        found = None
        for m in uncovered:
            cov = [p for p in primes if covers(p, m)]
            if len(cov) == 1:
                found = cov[0]; break
        if found is None: break
        chosen.append(found)
        uncovered -= {m for m in uncovered if covers(found, m)}
    rest = [p for p in primes if p not in chosen]
    best = None
    for r in range(len(rest)+1):
        for combo in combinations(rest, r):
            if all(any(covers(p, m) for p in list(combo)+chosen) for m in uncovered):
                cost = (len(combo), sum(bin(p[0]^0xF).count("1") for p in combo))
                if best is None or cost < best[0]: best = (cost, combo)
        if best is not None and best[0][0] == r: break
    return chosen + (list(best[1]) if best else [])

def anf_of(minterms):
    f = [1 if v in minterms else 0 for v in range(16)]
    for j in range(4):
        for v in range(16):
            if (v >> j) & 1: f[v] ^= f[v ^ (1 << j)]
    return [v for v in range(16) if f[v]]

def NOT(x): return f"(1-{x})"

def verify(enc_fn):
    for bit in range(4):
        expr = enc_fn(bit, "b0", "b1", "b2", "b3")
        for v in range(16):
            env = {"b0": (v>>0)&1, "b1": (v>>1)&1, "b2": (v>>2)&1, "b3": (v>>3)&1}
            got = eval(expr, {"__builtins__": {}}, env)
            want = (SBOX[v] >> bit) & 1
            assert int(got) == want, (bit, v, expr, got, want)

def enc_unclean(bit, x0,x1,x2,x3):
    terms = []
    for v in range(16):
        if (SBOX[v] >> bit) & 1:
            xs = [x0,x1,x2,x3]
            lits = [xs[j] if (v>>j)&1 else NOT(xs[j]) for j in range(4)]
            terms.append("(" + "&".join(lits) + ")")
    return "(" + "|".join(terms) + ")"

_QM = {b: qm_minimize([v for v in range(16) if (SBOX[v]>>b)&1]) for b in range(4)}
def enc_qm(bit, x0,x1,x2,x3):
    xs = [x0,x1,x2,x3]
    terms = []
    for (mask,bits) in _QM[bit]:
        lits = [xs[j] if (bits>>j)&1 else NOT(xs[j])
                for j in range(4) if not (mask>>j)&1]
        terms.append("(" + "&".join(lits) + ")" if lits else "1")
    return "(" + "|".join(terms) + ")"

_ANF = {b: anf_of([v for v in range(16) if (SBOX[v]>>b)&1]) for b in range(4)}
def enc_anf(bit, x0,x1,x2,x3):
    xs = [x0,x1,x2,x3]
    mons = []
    for m in _ANF[bit]:
        if m == 0: mons.append("1")
        else: mons.append("(" + "&".join(xs[j] for j in range(4) if (m>>j)&1) + ")")
    return "(" + "^".join(mons) + ")"

def enc_fact(bit, x0,x1,x2,x3):
    n0,n1,n2,n3 = NOT(x0),NOT(x1),NOT(x2),NOT(x3)
    if bit == 0:
        return f"({x0}^{x2}^({x1}&{x2})^{x3})"
    if bit == 1:
        return f"(({n2}&({x1}^{x3}))|({x0}&{x2}&{x3}))"
    if bit == 2:
        return f"(({n1}&{n2})|({x0}&{x1}&{x2}&{n3})|({n1}&{x2}&{x3}))"
    # bit3: x3&((x0&~x2)|(x1&~x2)) | ~x3&((~x0&~x1)|(~x0&x2)|(x0&x1))
    return (f"(({x3}&(({x0}&{n2})|({x1}&{n2})))|"
            f"({n3}&(({n0}&{n1})|({n0}&{x2})|({x0}&{x1}))))")

def to_verilog(e):
    # (1-<expr>) -> (~<expr>); & | ^ pass through. <expr> has no parens at top level here
    # handle nested: repeatedly replace innermost (1-...)
    while True:
        m = re.search(r"\(1-([^()]+)\)", e)
        if not m: break
        e = e[:m.start()] + "(~" + m.group(1) + ")" + e[m.end():]
    return e

def emit(name, enc):
    verify(enc)
    L = [f"module {name}(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);"]
    L.append("  wire [63:0] _k = key; // keep port, no floating input")
    outs = []
    for b in range(16):
        sb = f"sb{b}"
        L.append(f"  wire [3:0] {sb};")
        for bit in range(4):
            e = enc(bit, f"val[{4*b+0}]", f"val[{4*b+1}]", f"val[{4*b+2}]", f"val[{4*b+3}]")
            L.append(f"  assign {sb}[{bit}] = {to_verilog(e)};")
        outs.append(sb)
    L.append(f"  assign out = {{{', '.join(outs[::-1])}}} ^ _k ^ _k;")
    L.append("endmodule")
    path = EXP + f"/rtl/probe3/{name}.v"
    open(path, "w").write("\n".join(L) + "\n")
    return path

def synth(name, path):
    r = subprocess.run(
        [sys.executable, EXP + "/run_synth.py", path, name, EXP + f"/results/probe3/sb_{name}"],
        capture_output=True, text=True, timeout=600, cwd=EXP,
        env={**os.environ, "PATH": EXP + "/bin:" + os.environ["PATH"]})
    m = re.search(r"DUT \S+: cells=\d+ area=\d+ crit=([\d.]+)", r.stdout)
    c = float(m.group(1)) if m else None
    print(f"{name}: crit={c}", flush=True)
    return c

if __name__ == "__main__":
    res = {}
    for name, enc in [("sb_unclean", enc_unclean), ("sb_qm", enc_qm),
                      ("sb_anf", enc_anf), ("sb_fact", enc_fact)]:
        p = emit(name, enc)
        res[name] = synth(name, p)
    print("SHOOTOUT:", res)
