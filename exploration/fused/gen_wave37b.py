#!/usr/bin/env python3
"""Wave-37b bundle generator: candidate JSONL record -> fast_battery bundle.

Reads fused/wave37_3st_L3_diag.jsonl, takes a KEEP try number, and writes
fast_battery/candidates/w37b_<try>/{model.py,impl.c,rtl.v,meta.json}.
Verifies bit-exactness: generated model.py vs triage mix_fn on 2000 random
vectors (fail-loud).

Usage: gen_wave37b.py <TRY> [--hits N]   (reads wave37_3st_L3_diag.jsonl in cwd,
   or with --hits N reads hit N from wave37b_climb_HITS.jsonl)
"""
import importlib.util
import json
import os
import sys

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from wave37_lib import make_mix37

if "--hits" in sys.argv:
    i = sys.argv.index("--hits")
    N = int(sys.argv[i + 1])
    hits = [json.loads(l) for l in open("wave37b_climb_HITS.jsonl")]
    assert 0 <= N < len(hits), f"fail-loud: hit {N} not in HITS file ({len(hits)} hits)"
    h = hits[N]
    rec = {"try": f"h{N}", "status": "KEEP", "cand": h["cand"]}
    NAME = f"w37b_keep{N}"
    LABEL = f"hit{N} (z={h['z']:.2f})"
    assert h["z"] < 10.0, "fail-loud: hit z not < 10"
else:
    TRY = int(sys.argv[1])
    JSONL = "wave37_3st_L3_diag.jsonl"
    rec = None
    for line in open(JSONL):
        r = json.loads(line)
        if r["try"] == TRY:
            rec = r
            break
    assert rec is not None, f"fail-loud: try {TRY} not in {JSONL}"
    assert rec["status"] == "KEEP", f"fail-loud: try {TRY} status={rec['status']}, not KEEP"
    NAME = f"w37b_t{TRY}"
    LABEL = f"try {TRY}"

cand = json.loads(json.dumps(rec["cand"]))  # normalize tuples->lists
assert cand.get("n_lin") == 3, "fail-loud: bundle generator is L=3-only"
POST_WHITEN = "--no-post-whiten" not in sys.argv
cand["post_whiten"] = POST_WHITEN
if not POST_WHITEN:
    NAME += "_npw"
    LABEL += " (no post-whiten)"
OUTD = f"/home/hatch/workspace/mix/exploration/fast_battery/candidates/{NAME}"
os.makedirs(OUTD, exist_ok=True)

r1, r2, p, q, m = cand["r1"], cand["r2"], cand["p"], cand["q"], cand["m"]
stages = cand["stages"]  # lists after JSON: [a,b,[cx..],f,g,h,i,[cy..],mx,ny]


def rl64(x, r):
    """C/RTL rotation expression fragment."""
    return x if r == 0 else f"rotl64({x},{r})"


def rtl_rot(sig, r):
    if r == 0:
        return sig
    return "{%s[%d:0], %s[63:%d]}" % (sig, 63 - r, sig, 64 - r)


# ---------------- model.py ----------------
L = []
L.append('"""Wave-37b two-lane repair (L=3): intra-linear + AND-cross. KEEP %s."""' % LABEL)
L.append("import numpy as np")
L.append("M64 = np.uint64(0xFFFFFFFFFFFFFFFF)")
L.append("R1,R2,P,Q,M = %d,%d,%d,%d,%d" % (r1, r2, p, q, m))
L.append("def _rotl(x, r):")
L.append("    r %= 64")
L.append("    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x")
for si, st in enumerate(stages):
    a, b, cx, f, g, h, i, cy, mx, ny = st
    L.append("S%d = (%d,%d,%s,%d,%d,%d,%d,%s,%d,%d)" % (
        si, a, b, tuple(cx), f, g, h, i, tuple(cy), mx, ny))
L.append("STAGES = [%s]" % ", ".join("S%d" % si for si in range(len(stages))))
L.append("def mix_np(V, K):")
L.append("    v = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)")
L.append("    x = (v ^ k) & M64")
L.append("    y = (_rotl(v, R1) ^ _rotl(k, R2) ^ (_rotl(v, P) & _rotl(k, Q))) & M64")
L.append("    for (a,b,cx,f,g,h,i,cy,mx,ny) in STAGES:")
L.append("        xn = x ^ (_rotl(x,a) & _rotl(x,b)) ^ (_rotl(x,f) & _rotl(y,g))")
L.append("        for c in cx: xn ^= _rotl(x, c)")
L.append("        yn = y ^ (_rotl(y,h) & _rotl(y,i)) ^ (_rotl(x,mx) & _rotl(y,ny))")
L.append("        for c in cy: yn ^= _rotl(y, c)")
L.append("        x, y = xn & M64, yn & M64")
if POST_WHITEN:
    L.append("    return (x ^ _rotl(y, M) ^ _rotl(k, 13)) & M64")
else:
    L.append("    return (x ^ _rotl(y, M)) & M64")
L.append("def mix(v, k):")
L.append("    return int(mix_np(np.uint64(v), np.uint64(k)))")
open(os.path.join(OUTD, "model.py"), "w").write("\n".join(L) + "\n")

# ---------------- impl.c ----------------
C = []
C.append("#include <stdint.h>")
C.append("static inline uint64_t rotl64(uint64_t x, int r) {")
C.append("    r &= 63;")
C.append("    return r ? (x << r) | (x >> (64 - r)) : x;")
C.append("}")
C.append("// wave-37b two-lane repair (L=%d), KEEP try %s" % (len(stages[0][2]), LABEL))
C.append("uint64_t mix_hash(uint64_t val, uint64_t key) {")
C.append("    uint64_t x = val ^ key;")
C.append("    uint64_t y = %s ^ %s ^ (%s & %s);" % (
    rl64("val", r1), rl64("key", r2), rl64("val", p), rl64("key", q)))
C.append("    uint64_t xn, yn;")
for st in stages:
    a, b, cx, f, g, h, i, cy, mx, ny = st
    terms_x = ["(rotl64(x,%d) & rotl64(x,%d))" % (a, b),
               "(rotl64(x,%d) & rotl64(y,%d))" % (f, g)] + \
              ["rotl64(x,%d)" % c for c in cx]
    terms_y = ["(rotl64(y,%d) & rotl64(y,%d))" % (h, i),
               "(rotl64(x,%d) & rotl64(y,%d))" % (mx, ny)] + \
              ["rotl64(y,%d)" % c for c in cy]
    C.append("    xn = x ^ %s;" % " ^ ".join(terms_x))
    C.append("    yn = y ^ %s;" % " ^ ".join(terms_y))
    C.append("    x = xn; y = yn;")
if POST_WHITEN:
    C.append("    return x ^ %s ^ rotl64(key, 13);" % rl64("y", m))
else:
    C.append("    return x ^ %s;" % rl64("y", m))
C.append("}")
open(os.path.join(OUTD, "impl.c"), "w").write("\n".join(C) + "\n")

# ---------------- rtl.v ----------------
V = []
V.append("// %s: wave-37b two-lane repair (L=%d), KEEP %s" % (NAME, len(stages[0][2]), LABEL))
V.append("module %s(" % NAME)
V.append("    input  [63:0] val,")
V.append("    input  [63:0] key,")
V.append("    output [63:0] out")
V.append(");")
V.append("    wire [63:0] x0 = val ^ key;")
V.append("    wire [63:0] y0 = %s ^ %s ^ (%s & %s);" % (
    rtl_rot("val", r1), rtl_rot("key", r2), rtl_rot("val", p), rtl_rot("key", q)))
for si, st in enumerate(stages):
    a, b, cx, f, g, h, i, cy, mx, ny = st
    ex = ["(%s & %s)" % (rtl_rot("x%d" % si, a), rtl_rot("x%d" % si, b)),
          "(%s & %s)" % (rtl_rot("x%d" % si, f), rtl_rot("y%d" % si, g))] + \
         [rtl_rot("x%d" % si, c) for c in cx]
    ey = ["(%s & %s)" % (rtl_rot("y%d" % si, h), rtl_rot("y%d" % si, i)),
          "(%s & %s)" % (rtl_rot("x%d" % si, mx), rtl_rot("y%d" % si, ny))] + \
         [rtl_rot("y%d" % si, c) for c in cy]
    V.append("    wire [63:0] x%d = x%d ^ %s;" % (si + 1, si, " ^ ".join(ex)))
    V.append("    wire [63:0] y%d = y%d ^ %s;" % (si + 1, si, " ^ ".join(ey)))
ns = len(stages)
if POST_WHITEN:
    V.append("    assign out = x%d ^ %s ^ %s;" % (ns, rtl_rot("y%d" % ns, m), rtl_rot("key", 13)))
else:
    V.append("    assign out = x%d ^ %s;" % (ns, rtl_rot("y%d" % ns, m)))
V.append("endmodule")
open(os.path.join(OUTD, "rtl.v"), "w").write("\n".join(V) + "\n")

# ---------------- meta.json ----------------
import numpy as np
tri = make_mix37(cand)
gold = []
for v, k in [(0x0, 0x123456789ABCDEF0), (0x123456789ABCDEF0, 0x0)]:
    o = int(tri(np.array([np.uint64(v)]), np.array([np.uint64(k)]))[0])
    gold.append({"val": hex(v), "key": hex(k), "out": hex(o)})
meta = {
    "name": NAME,
    "description": "wave-37b two-lane repair (L=%d intra-linear/lane, AND-cross), KEEP try %s" % (len(stages[0][2]), LABEL),
    "screen_keys": ["0x123456789abcdef0", "0x0"],
    "practrand_keys": ["0x123456789abcdef0", "0x0"],
    "goldens": gold,
    "rtl_top": NAME,
}
open(os.path.join(OUTD, "meta.json"), "w").write(json.dumps(meta, indent=1) + "\n")

# ---------------- bit-exactness check ----------------
spec = importlib.util.spec_from_file_location("w37b_model", os.path.join(OUTD, "model.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
import numpy as np
rng = np.random.default_rng(0x37B)
V = rng.integers(0, 2**64, size=2000, dtype=np.uint64)
K = rng.integers(0, 2**64, size=2000, dtype=np.uint64)
a = np.asarray(tri(V, K), dtype=np.uint64)
b = np.asarray(mod.mix_np(V, K), dtype=np.uint64)
assert (a == b).all(), "fail-loud: bundle model.py != triage mix_fn"
# goldens cross-check
for gd in gold:
    go = mod.mix(int(gd["val"], 16), int(gd["key"], 16))
    assert go == int(gd["out"], 16), "fail-loud: golden mismatch"
print(f"bundle {NAME} written to {OUTD}; bit-exact 2000/2000, goldens OK")
