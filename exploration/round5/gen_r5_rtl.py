"""Round 5 RTL generator: flat, unrolled Verilog per candidate.

S-boxes are Quine-McCluskey-minimized DNF (exact minimal SOP for 4 vars),
same treatment as r3_xorlin_qm. Midori M + shuffles are wiring-level.
Style follows round4/gen_hflat.py (function-automatic blocks).
"""
import os
import sys
from itertools import combinations

R5 = "/home/hatch/workspace/mix/exploration/round5"
OUT = os.path.join(R5, "rtl")
os.makedirs(OUT, exist_ok=True)
sys.path.insert(0, os.path.join(R5, "models"))
from r5 import SBOXES  # noqa: E402

# ---- QM (copied from exploration/qm_sbox.py to avoid its print-on-import) ----
def qm_minimize(table, bit):
    minterms = [v for v in range(16) if (table[v] >> bit) & 1]
    def combine(a, b):
        if a[0] != b[0]:
            return None
        diff = a[1] ^ b[1]
        if diff & (diff - 1):
            return None
        if a[0] & diff:
            return None
        return (a[0] | diff, a[1] & ~diff)
    cur = {(0, m) for m in minterms}
    primes = set()
    while cur:
        nxt = set(); used = set(); cl = list(cur)
        for i in range(len(cl)):
            for j in range(i + 1, len(cl)):
                c = combine(cl[i], cl[j])
                if c:
                    used.add(cl[i]); used.add(cl[j]); nxt.add(c)
        primes |= (cur - used); cur = nxt
    primes = list(primes)
    def covers(p, m):
        return (m & ~p[0]) == p[1]
    uncovered = set(minterms); chosen = []
    while True:
        essential = None
        for m in uncovered:
            cov = [p for p in primes if covers(p, m)]
            if len(cov) == 1:
                essential = cov[0]; break
        if essential is None:
            break
        chosen.append(essential)
        uncovered -= {m for m in uncovered if covers(essential, m)}
    rest = [p for p in primes if p not in chosen]
    best = None
    for r in range(len(rest) + 1):
        for combo in combinations(rest, r):
            if all(any(covers(p, m) for p in list(combo) + chosen)
                   for m in uncovered):
                cost = (len(combo),
                        sum(bin(p[0] ^ 0xF).count("1") for p in combo))
                if best is None or cost < best[0]:
                    best = (cost, combo)
        if best is not None and best[0][0] == r:
            break
    chosen += list(best[1]) if best else []
    return chosen


def sbox_fn(name, table):
    L = [f"    function automatic [3:0] sbox_{name}(input [3:0] x);",
         "        reg y0, y1, y2, y3;", "        begin"]
    for bit, yn in enumerate(["y0", "y1", "y2", "y3"]):
        primes = qm_minimize(table, bit)
        terms = []
        for (mask, bits) in primes:
            lits = []
            for j in range(4):
                if not (mask >> j) & 1:
                    lits.append(f"x[{j}]" if (bits >> j) & 1
                                else f"~x[{j}]")
            terms.append("(" + "&".join(lits) + ")" if lits else "1'b1")
        rhs = " | ".join(terms) if terms else "1'b0"
        L.append(f"            {yn} = {rhs};")
    L += [f"            sbox_{name} = {{y3, y2, y1, y0}};",
          "        end", "    endfunction"]
    return L


def sbox16_fn(name):
    L = [f"    function automatic [63:0] sbox16_{name}(input [63:0] x);",
         "        begin"]
    terms = ", ".join(f"sbox_{name}(x[{4*s+3}:{4*s}])"
                      for s in range(15, -1, -1))
    L += [f"            sbox16_{name} = {{{terms}}};", "        end",
          "    endfunction"]
    return L


def sbox8_fn(name):
    L = [f"    function automatic [31:0] sbox8_{name}(input [31:0] x);",
         "        begin"]
    terms = ", ".join(f"sbox_{name}(x[{4*s+3}:{4*s}])"
                      for s in range(7, -1, -1))
    L += [f"            sbox8_{name} = {{{terms}}};", "        end",
          "    endfunction"]
    return L


def midori_fns(perm):
    L = ["    function automatic [63:0] midori_M(input [63:0] x);",
         "        reg [3:0] n0,n1,n2,n3;", "        reg [63:0] y;",
         "        begin"]
    for c in range(4):
        b = 16 * c
        L.append(f"            n0 = x[{b+3}:{b}]; n1 = x[{b+7}:{b+4}];")
        L.append(f"            n2 = x[{b+11}:{b+8}]; n3 = x[{b+15}:{b+12}];")
        L.append(f"            y[{b+3}:{b}]    = n1^n2^n3;")
        L.append(f"            y[{b+7}:{b+4}]   = n0^n2^n3;")
        L.append(f"            y[{b+11}:{b+8}]  = n0^n1^n3;")
        L.append(f"            y[{b+15}:{b+12}] = n0^n1^n2;")
    L += ["            midori_M = y;", "        end", "    endfunction"]
    terms = ", ".join(f"x[{4*perm[i]+3}:{4*perm[i]}]" for i in range(15, -1, -1))
    L += ["    function automatic [63:0] shuffle(input [63:0] x);",
          "        begin", f"            shuffle = {{{terms}}};",
          "        end", "    endfunction"]
    return L


def midori32_fn():
    L = ["    function automatic [31:0] midori32(input [31:0] x);",
         "        reg [3:0] n0,n1,n2,n3;", "        reg [31:0] y;",
         "        begin"]
    for c in range(2):
        b = 16 * c
        L.append(f"            n0 = x[{b+3}:{b}]; n1 = x[{b+7}:{b+4}];")
        L.append(f"            n2 = x[{b+11}:{b+8}]; n3 = x[{b+15}:{b+12}];")
        L.append(f"            y[{b+3}:{b}]    = n1^n2^n3;")
        L.append(f"            y[{b+7}:{b+4}]   = n0^n2^n3;")
        L.append(f"            y[{b+11}:{b+8}]  = n0^n1^n3;")
        L.append(f"            y[{b+15}:{b+12}] = n0^n1^n2;")
    L += ["            midori32 = y;", "        end", "    endfunction"]
    return L


def tchi64_fn():
    L = ["    function automatic [63:0] tchi64(input [63:0] x);",
         "        begin"]
    terms = [f"(x[{i}] ^ ((~x[{i+1}]) & x[{i+2}]))" for i in range(61, -1, -1)]
    body = ", ".join(["x[63]", "x[62]"] + terms)
    L += [f"            tchi64 = {{{body}}};", "        end", "    endfunction"]
    return L


def rk_wires(keyname, idx, yname, rot):
    r = (rot * (idx + 1)) % 64
    c = ((idx + 1) * 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
    rotexpr = f"{{{keyname}[{63-r}:0], {keyname}[63:{64-r}]}}" if r else keyname
    return [f"    wire [63:0] {yname} = {rotexpr} ^ 64'h{c:016X};"]


def xs_wires(xname, a, b, c, yname):
    # y = x ^ (x>>a); y ^= (y<<b); y ^= (y>>c)
    # xname may be an expression: parenthesize every use (Verilog >> binds
    # tighter than ^, so `val ^ key ^ (val ^ key >> 12)` would mis-parse).
    xn = f"({xname})"
    return [
        f"    wire [63:0] {yname}_s1 = {xn} ^ ({xn} >> {a});",
        f"    wire [63:0] {yname}_s2 = {yname}_s1 ^ (({yname}_s1 << {b}) & 64'hFFFFFFFFFFFFFFFF);",
        f"    wire [63:0] {yname} = {yname}_s2 ^ ({yname}_s2 >> {c});",
    ]


PERM_D = [0, 10, 5, 15, 14, 4, 11, 1, 9, 3, 12, 6, 7, 13, 2, 8]
PERM_R = [15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0]

# spec: name -> dict
SPECS = {
    "r5_gift":          dict(sboxes=["gift"]*3, perm=PERM_D, rk_rot=13,
                             pre=("xs", 12, 25, 27), post=None),
    "r5_skinny":        dict(sboxes=["skinny"]*3, perm=PERM_D, rk_rot=13,
                             pre=("xs", 12, 25, 27), post=None),
    "r5_midori":        dict(sboxes=["midori"]*3, perm=PERM_D, rk_rot=13,
                             pre=("xs", 12, 25, 27), post=None),
    "r5_present":       dict(sboxes=["present"]*3, perm=PERM_D, rk_rot=13,
                             pre=("xs", 12, 25, 27), post=None),
    "r5_rotks7":        dict(sboxes=["s1"]*3, perm=PERM_D, rk_rot=7,
                             pre=("xs", 12, 25, 27), post=None),
    "r5_shufrev":       dict(sboxes=["s1"]*3, perm=PERM_R, rk_rot=13,
                             pre=("xs", 12, 25, 27), post=None),
    "r5_xorspn2_gift":  dict(sboxes=["gift"]*2, perm=PERM_D, rk_rot=13,
                             pre=("xs", 12, 25, 27), post=None),
    "r5_xorspn2_skinny": dict(sboxes=["skinny"]*2, perm=PERM_D, rk_rot=13,
                             pre=("xs", 12, 25, 27), post=None),
    "r5_xorspn4":       dict(sboxes=["s1"]*4, perm=PERM_D, rk_rot=13,
                             pre=("xs", 12, 25, 27), post=None),
    "r5_xorspn5":       dict(sboxes=["s1"]*5, perm=PERM_D, rk_rot=13,
                             pre=("xs", 12, 25, 27), post=None),
    "r5_xs2spn3":       dict(sboxes=["s1"]*3, perm=PERM_D, rk_rot=13,
                             pre=("xs2",), post=None),
    "r5_xsaltspn3":     dict(sboxes=["s1"]*3, perm=PERM_D, rk_rot=13,
                             pre=("xs", 13, 7, 17), post=None),
    "r5_xsmul3spn3":    dict(sboxes=["s1"]*3, perm=PERM_D, rk_rot=13,
                             pre=("xsmul3",), post=None),
    "r5_spnxs3":        dict(sboxes=["s1"]*3, perm=PERM_D, rk_rot=13,
                             pre=None, post=("xs", 12, 25, 27)),
    "r5_xsspnxs":       dict(sboxes=["s1"]*3, perm=PERM_D, rk_rot=13,
                             pre=("xs", 12, 25, 27), post=("xs", 12, 25, 27)),
    "r5_hetero":        dict(sboxes=["s1", "gift", "skinny"], perm=PERM_D,
                             rk_rot=13, pre=("xs", 12, 25, 27), post=None),
    "r5_chipost":       dict(sboxes=["s1"]*3, perm=PERM_D, rk_rot=13,
                             pre=("xs", 12, 25, 27), post=("tchi",)),
}


def gen_spn(name, sp):
    sboxes = sp["sboxes"]
    nrounds = len(sboxes)
    uniq = sorted(set(sboxes))
    L = [f"// Round 5 candidate {name}",
         f"module {name}",
         "    (input wire [63:0] val, input wire [63:0] key,",
         "     output wire [63:0] out);"]
    for u in uniq:
        L += sbox_fn(u, SBOXES[u])
        L += sbox16_fn(u)
    L += midori_fns(sp["perm"])
    if sp["post"] == ("tchi",):
        L += tchi64_fn()
    # pre-diffusion
    pre = sp["pre"]
    if pre is None:
        L.append("    wire [63:0] x0 = val ^ key;")
    elif pre[0] == "xs":
        L += xs_wires("val ^ key", pre[1], pre[2], pre[3], "xp")
        L.append("    wire [63:0] x0 = xp;")
    elif pre[0] == "xs2":
        L += xs_wires("val ^ key", 12, 25, 27, "xp1")
        L += xs_wires("xp1", 13, 7, 17, "xp")
        L.append("    wire [63:0] x0 = xp;")
    elif pre[0] == "xsmul3":
        L += xs_wires("val ^ key", 12, 25, 27, "xp1")
        L.append("    wire [63:0] xp = xp1 + (xp1 << 1);  // x3, odd => bijective")
        L.append("    wire [63:0] x0 = xp;")
    cur = "x0"
    for i in range(nrounds):
        sb = sboxes[i]
        L += rk_wires("key", i, f"rk{i}", sp["rk_rot"])
        L.append(f"    wire [63:0] s{i} = shuffle(midori_M(sbox16_{sb}({cur} ^ rk{i})));")
        cur = f"s{i}"
    L += rk_wires("key", nrounds, f"rk{nrounds}", sp["rk_rot"])
    fin = f"{cur} ^ rk{nrounds}"
    post = sp["post"]
    if post is None:
        L.append(f"    assign out = {fin};")
    elif post[0] == "xs":
        L += xs_wires(f"({fin})", post[1], post[2], post[3], "xq")
        L.append("    assign out = xq;")
    elif post[0] == "tchi":
        L.append(f"    assign out = tchi64({fin});")
    L.append("endmodule")
    return L


def gen_feistspn4(name):
    L = [f"// Round 5 candidate {name}: 4-round Feistel, F = 32-bit mini-SPN",
         "module r5_feistspn4",
         "    (input wire [63:0] val, input wire [63:0] key,",
         "     output wire [63:0] out);"]
    L += sbox_fn("s1", SBOXES["s1"])
    L += sbox8_fn("s1")
    L += midori32_fn()
    L.append("    wire [63:0] x0 = val ^ key;")
    L.append("    wire [31:0] L0 = x0[63:32];")
    L.append("    wire [31:0] R0 = x0[31:0];")
    for i in range(5):
        L += rk_wires("key", i, f"rk{i}", 13)
    for i in range(4):
        L.append(f"    wire [31:0] F{i} = midori32(sbox8_s1(R{i} ^ rk{i}[31:0])) ^ rk{i}[31:0];")
        L.append(f"    wire [31:0] L{i+1} = R{i};")
        L.append(f"    wire [31:0] R{i+1} = L{i} ^ F{i};")
    L.append("    assign out = {L4 ^ rk4[63:32], R4 ^ rk4[31:0]};")
    L.append("endmodule")
    return L


if __name__ == "__main__":
    only = sys.argv[1:]
    for name, sp in SPECS.items():
        if only and name not in only:
            continue
        lines = gen_spn(name, sp)
        p = os.path.join(OUT, f"r5_{name}.v")
        open(p, "w").write("\n".join(lines) + "\n")
        print("wrote", p)
    if not only or "r5_feistspn4" in only:
        p = os.path.join(OUT, "r5_r5_feistspn4.v")
        open(p, "w").write("\n".join(gen_feistspn4("r5_feistspn4")) + "\n")
        print("wrote", p)
