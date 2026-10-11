"""Round 3, priority 1: shave 0.5u off spn4_xorlin_1137 (44.8 -> <=44.3).

Function-preserving levers (NO re-screening needed; verify by RTL-vs-original-model):
  V_a : QM-minimal SOP for the PRESENT S-box (replaces unoptimized 8-minterm SOP).
  V_b : V_a + final whitening absorbed via L^{-1} (out = L(sy3 ^ L^{-1}(rk4)));
        key-only precompute runs in parallel with the rounds.
  V_c : V_b + initial val^key merged into rk[0] xor (single 4-input xor tree).

Each variant: emit RTL -> check_rtl.py vs ORIGINAL spn4_xorlin_1137 model
(function must be identical) -> run_synth.py.
"""
import os, subprocess, sys
from itertools import combinations

EXP = "/home/hatch/workspace/mix/exploration"
M64 = (1 << 64) - 1
GOLDEN = 0x9E3779B97F4A7C15
PRESENT = [0xC,0x5,0x6,0xB,0x9,0x0,0xA,0xD,0x3,0xE,0xF,0x8,0x4,0x7,0x1,0x2]
LR, LS = 11, 37  # xorlin rotation pair of _1137

# ---------------- QM minimization (exact, 4 vars) ----------------
def qm_minimize(minterms):
    def combine(a, b):
        if a[0] != b[0]:  # must have identical don't-care sets to be adjacent
            return None
        diff = a[1] ^ b[1]
        if diff & (diff - 1):  # differ in more than one care position
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
    primes = list(primes)
    def covers(p, m):
        return (m & ~p[0]) == p[1]
    uncovered = set(minterms)
    chosen = []
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
    return chosen + (list(best[1]) if best else [])

def cube_terms(p, sig):
    """Return Verilog product term for prime implicant p=(mask,bits) on sig[3:0]."""
    mask, bits = p
    lits = []
    for j in range(4):
        if not (mask >> j) & 1:
            nm = "%s[%d]" % (sig, j)
            lits.append(nm if (bits >> j) & 1 else "(~%s)" % nm)
    return "&".join(lits) if lits else "1'b1"

# precompute minimal SOP cubes per output bit (bit j of SBOX[v])
_QM = {}
for _bit in range(4):
    _mt = [v for v in range(16) if (PRESENT[v] >> _bit) & 1]
    _QM[_bit] = qm_minimize(_mt)

def sbox_qm_assigns(sb, sx):
    """QM-minimal SOP assigns for one nibble: sb[3:0] from sx (a wire [63:0], use sx[0..3] local)."""
    # we pass a 4-bit slice signal name; build per-bit OR of cubes
    L = []
    for bit in range(4):
        cubes = _QM[bit]
        # rewrite cube_terms to use the slice signal's bits
        terms = []
        for (mask, bits) in cubes:
            lits = []
            for j in range(4):
                if not (mask >> j) & 1:
                    nm = "%s[%d]" % (sx, j)
                    lits.append(nm if (bits >> j) & 1 else "(~%s)" % nm)
            terms.append("(" + "&".join(lits) + ")" if lits else "1'b1")
        rhs = " | ".join(terms) if terms else "1'b0"
        L.append("  assign %s[%d] = %s;" % (sb, bit, rhs))
    return L

# ---------------- L^{-1} for whitening absorption (lever b) ----------------
def mat_inv_64(mat):
    """Invert 64x64 binary matrix (rows as ints, row i = output i's input mask)."""
    n = 64
    a = [mat[i] | (1 << (64 + i)) for i in range(n)]  # augment
    for col in range(n):
        piv = next(i for i in range(col, n) if (a[i] >> col) & 1)
        a[col], a[piv] = a[piv], a[col]
        for i in range(n):
            if i != col and (a[i] >> col) & 1:
                a[i] ^= a[col]
    return [a[i] >> 64 for i in range(n)]

def Linv_row_masks():
    # RTL rotl(sig,r) = {sig[63-r:0], sig[63:64-r]} is a LEFT rotate:
    # rotl(x,r)[i] = x[(i-r) % 64]. Hence L(x)[i] = x[i]^x[(i-11)%64]^x[(i-37)%64].
    mat = [(1 << i) | (1 << ((i - LR) % 64)) | (1 << ((i - LS) % 64)) for i in range(64)]
    return mat_inv_64(mat)

_LINV = Linv_row_masks()

def rc4_val():
    return (5 * GOLDEN) & M64

def emit_k4p():
    """k4p = L^{-1}(rk4); rk4[j] = ROTL(key,1)[j] ^ RC4[j] = key[(j-1)%64] ^ RC4[j]."""
    RC4 = rc4_val()
    L = ["  // lever b: k4p = L^{-1}(rk4), key-only, computed in parallel with rounds"]
    for i in range(64):
        row = _LINV[i]
        kbits = [j for j in range(64) if (row >> j) & 1]
        const = 0
        terms = []
        for j in kbits:
            terms.append("key[%d]" % ((j - 1) % 64))
            const ^= (RC4 >> j) & 1
        rhs = " ^ ".join(terms)
        if const:
            rhs += " ^ 1'b1"
        L.append("  assign k4p[%d] = %s;" % (i, rhs))
    return L

# ---------------- design emitters ----------------
def rotl(sig, r):
    r %= 64
    return "{%s[%d:0], %s[63:%d]}" % (sig, 63-r, sig, 64-r) if r else sig

def rk_expr(i):
    # rk[i] = ROTL(key,13*(i+1)) ^ RC[i], RC[i]=(i+1)*GOLDEN
    return "%s ^ 64'h%016x" % (rotl("key", 13*(i+1)), ((i+1)*GOLDEN) & M64)

def selftest_Linv():
    import random
    random.seed(1)
    def L(x):
        return (x ^ ((x << LR) | (x >> (64-LR))) ^ ((x << LS) | (x >> (64-LS)))) & M64 \
            if False else None
    # proper rotl-based L and Linv application
    def rotl64(x, r):
        r %= 64
        return (((x << r) | (x >> (64-r))) & M64) if r else x & M64
    def L64(x):
        return (x ^ rotl64(x, LR) ^ rotl64(x, LS)) & M64
    def Linv64(x):
        y = 0
        for i in range(64):
            row = _LINV[i]
            # y[i] = parity(row & x)
            if bin(row & x).count("1") & 1:
                y |= (1 << i)
        return y
    for _ in range(200):
        x = random.getrandbits(64)
        assert L64(Linv64(x)) == x, "Linv wrong"
        assert Linv64(L64(x)) == x, "Linv wrong"
    print("Linv self-test: OK (200 random vectors)")

def build_variant(name, levers):
    """Rebuild cleanly with correct wire ordering."""
    L = []
    L.append("  wire [63:0] k4p;" if "b" in levers else "  // no k4p")
    if "b" in levers:
        L.extend(emit_k4p())
    if "d" in levers:
        L.append("  wire [63:0] sx0 = val ^ key ^ %s;" % rk_expr(0))
    else:
        L.append("  wire [63:0] s0 = val ^ key;")
        L.append("  wire [63:0] sx0 = s0 ^ %s;" % rk_expr(0))
    for i in range(4):
        sx = "sx%d" % i
        sbnames = []
        for b in range(16):
            sl = "sl%d_%d" % (i, b)
            sb = "sb%d_%d" % (i, b)
            L.append("  wire [3:0] %s = %s[%d:%d];" % (sl, sx, 4*b+3, 4*b))
            L.append("  wire [3:0] %s;" % sb)
            L.extend(sbox_qm_assigns(sb, sl))
            sbnames.append(sb)
        sy = "sy%d" % i
        L.append("  wire [63:0] %s = {%s};" % (sy, ", ".join(sbnames[::-1])))
        sn = "s%d" % (i+1)
        L.append("  wire [63:0] %s = %s ^ %s ^ %s;" % (sn, sy, rotl(sy, LR), rotl(sy, LS)))
        if i < 3:
            L.append("  wire [63:0] sx%d = %s ^ %s;" % (i+1, sn, rk_expr(i+1)))
    if "b" in levers:
        L.append("  wire [63:0] z3 = sy3 ^ k4p;")
        L.append("  assign out = z3 ^ %s ^ %s;" % (rotl("z3", LR), rotl("z3", LS)))
    else:
        L.append("  assign out = s4 ^ %s;" % rk_expr(4))
    body = "\n".join(L)
    desc = "spn4_xorlin_1137 function-identical variant %s (levers %s)" % (name, levers)
    rtl = ("// %s\n// QM-minimal PRESENT S-box SOP; %s\nmodule %s(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);\n%s\nendmodule\n"
           % (name, desc, name, body))
    path = EXP + "/rtl/r3/%s.v" % name
    os.makedirs(EXP + "/rtl/r3", exist_ok=True)
    open(path, "w").write(rtl)
    return path

def check_equiv(name, rtl_path):
    """RTL vs ORIGINAL spn4_xorlin_1137 numpy model (function must be identical)."""
    r = subprocess.run(
        [sys.executable, EXP + "/check_rtl.py",
         "models.spn4_xorlin_1137.mix_spn4_xorlin_1137_np",
         rtl_path, name, EXP + "/results/r3/_%s" % name, "200"],
        capture_output=True, text=True, timeout=600, cwd=EXP,
        env={**os.environ, "PATH": EXP + "/bin:" + os.environ["PATH"]})
    # check_rtl.py raises (nonzero exit) on any mismatch; PASS prints RTLCHECK ... PASS
    ok = (r.returncode == 0 and "RTLCHECK" in (r.stdout + r.stderr)
          and "PASS" in (r.stdout + r.stderr))
    print(("EQUIV-OK " if ok else "EQUIV-FAIL ") + name)
    if not ok:
        print(r.stdout[-2000:], r.stderr[-2000:])
    return ok

def synth(name, rtl_path):
    r = subprocess.run(
        [sys.executable, EXP + "/run_synth.py",
         rtl_path, name, EXP + "/results/r3/s_%s" % name],
        capture_output=True, text=True, timeout=900, cwd=EXP,
        env={**os.environ, "PATH": EXP + "/bin:" + os.environ["PATH"]})
    for line in r.stdout.splitlines():
        if line.startswith("RESULT") or line.startswith("DUT"):
            print(line)
    if r.returncode != 0:
        print("SYNTH-FAILED", name, r.stdout[-1500:], r.stderr[-1500:])
        return None
    import re
    m = re.search(r"crit=([\d.]+)", r.stdout)
    return float(m.group(1)) if m else None

if __name__ == "__main__":
    selftest_Linv()
    # sanity: QM cubes
    for bit in range(4):
        print(f"bit{bit}: {len(_QM[bit])} cubes")
    variants = [
        ("r3_xorlin_qm", set()),            # V_a: QM SOP only
        ("r3_xorlin_qm_b", {"b"}),          # V_b: + Linv whitening
        ("r3_xorlin_qm_bd", {"b", "d"}),    # V_c: + merged initial
    ]
    for name, levers in variants:
        p = build_variant(name, levers)
        print("built", name)
        if not check_equiv(name, p):
            print("STOPPING: equivalence failed for", name)
            break
        c = synth(name, p)
        print(f"--> {name}: crit={c} (bar 44.3, need <={44.3})")
