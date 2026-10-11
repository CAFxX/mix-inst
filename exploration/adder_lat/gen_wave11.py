#!/usr/bin/env python3
"""Wave-11 generator: RESONANCE-BREAK after wave-10 falsified resonance-control.

Wave-10 finding: the systematic differential bias (max at bit48, 43-48/115
deltas |z|>9) lives in the and6a TRIPLETS themselves (rotation-schedule +
triple-structure), not the subop choice. Heterostages (and/or, and/chi) on
the known-clean and6a triplets died with the SAME signature. Dual-AND is
dead on speed (4.9u/stage) and quality (all S1-dead).

Wave-11 changes the SCHEDULE STRUCTURE itself (per wave-10 notes direction).
Two prongs, both untested in every track (checked track-6 LEADS.md 2026-10-10):

Prong A -- linear-stage insertion ("lin"): replace ONE of the 6 AND stages
  with a pure-linear stage  x ^= ra ^ rb ^ rc  (no AND). The linear stage
  breaks the AND-differential resonance chain structurally while costing
  ~2.2u vs 3.35u (no AND gate). 5xAND + 1xLIN targets ~19u, UNDER the
  20.1u frontier. Positions: early(0)/mid(2)/late(4).
  - al_lin6a: lin at idx 2, AND stages on and6a triplets (drops (3,11,29))
  - al_lin6b: lin at idx 4 (drops (11,23,37))
  - al_lin6c: lin at idx 0 (drops (1,2,13))

Prong B -- key-linear triplets ("keylin"): change the triplet COMPOSITION.
  Stage:  x ^= (ra & rb) ^ rotl(k,k1) ^ rotl(k,k2).
  The data-linear term rc is replaced by TWO key rotations. Same gate depth
  as "and" (1 AND + 4-input XOR tree), but a fundamentally different
  differential-elevation profile: for fixed key, stage differential is
  Dx ^ D(ra&rb) with NO data-linear term (key terms cancel in differentials).
  This is the "schedule with fundamentally different differential-elevation
  profile" re-test trigger from wave-10 notes.
  - al_keylin6a: 6 stages, and6a (a,b) pairs, k1=13*(i+1), k2=37*(i+1)
  - al_keylin6b: 6 stages, alt key offsets k1=7*(i+1), k2=31*(i+1)
  - al_keylin5a: 5 stages (floor probe), same as 6a first 5

Key schedule: same as al_and6a (pre-whiten x^=k, post x^=rotl(k,13));
no per-stage rk fold (psk=False). Bijectivity: every stage is
x ^= N(x) ^ const(k) with N nonlinear-or-linear in x -> bijective in x.

Skipped with reason: keyed data-AND (ra & rk) -- adds an XOR-tree level
(+1.2u/stage per t6_xc measurement), speed-doomed; staggered triplet ROLE
permutation -- pure rotation reschedule, wave-9's class (falsified);
7-stage+linear -- 5 ANDs were DIFF-dead, linear stages add no nonlinearity.
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gen_wave1 import PY_PREAMBLE, RC, FB, vl_rotl  # noqa: E402

AND6A = [(1, 2, 13), (7, 19, 5), (3, 11, 29), (17, 31, 7), (11, 23, 37), (19, 41, 23)]

def _and_stages(drop_idx):
    return [("and", t) for i, t in enumerate(AND6A) if i != drop_idx]

def _with_lin(drop_idx, lin_triplet):
    st = _and_stages(drop_idx)
    st.insert(drop_idx, ("lin", lin_triplet))
    return st

def _keylin_stages(n, m1, m2):
    out = []
    for i in range(n):
        a, b, _ = AND6A[i]
        k1 = (m1 * (i + 1)) % 64
        k2 = (m2 * (i + 1)) % 64
        assert k1 != k2, f"key offset collision at stage {i}"
        out.append(("keylin", (a, b, k1, k2)))
    return out

LIN6A = _with_lin(2, (9, 27, 45))
LIN6B = _with_lin(4, (15, 33, 51))
LIN6C = _with_lin(0, (21, 39, 57))
KEYLIN6A = _keylin_stages(6, 13, 37)
KEYLIN6B = _keylin_stages(6, 7, 31)
KEYLIN5A = _keylin_stages(5, 13, 37)

SPECS = [
    ("al_lin6a", LIN6A,
     "Wave-11: 5xAND+1xLIN, linear stage at idx 2 (resonance-break)"),
    ("al_lin6b", LIN6B,
     "Wave-11: 5xAND+1xLIN, linear stage at idx 4 (resonance-break)"),
    ("al_lin6c", LIN6C,
     "Wave-11: 5xAND+1xLIN, linear stage at idx 0 (resonance-break)"),
    ("al_keylin6a", KEYLIN6A,
     "Wave-11: 6-stage key-linear triplets x^=(ra&rb)^rk1^rk2 (k1=13i,k2=37i)"),
    ("al_keylin6b", KEYLIN6B,
     "Wave-11: 6-stage key-linear triplets, alt key offsets (k1=7i,k2=31i)"),
    ("al_keylin5a", KEYLIN5A,
     "Wave-11: 5-stage key-linear triplets (floor probe)"),
]


def gen_model(name, stages, desc):
    rc = ", ".join(hex(v) for v in RC[:12])
    s = PY_PREAMBLE % (desc, rc)
    s += "STAGES = %s\n" % (stages,)
    s += "def mix_np(V, K):\n"
    s += "    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)\n"
    s += "    x = (x ^ k) & M64\n"
    s += "    for i, (sop, st) in enumerate(STAGES):\n"
    s += "        ra, rb = _rotl(x, st[0]), _rotl(x, st[1])\n"
    s += "        if sop == 'lin':\n"
    s += "            t = (x ^ ra ^ rb ^ _rotl(x, st[2])) & M64\n"
    s += "        elif sop == 'keylin':\n"
    s += "            t = (x ^ (ra & rb) ^ _rotl(k, st[2]) ^ _rotl(k, st[3])) & M64\n"
    s += "        else:\n"
    s += "            t = (x ^ (ra & rb) ^ _rotl(x, st[2])) & M64\n"
    s += "        x = t\n"
    s += "    x = (x ^ _rotl(k, 13)) & M64\n"
    s += "    return x & M64\n"
    s += "def mix(v, k):\n    return int(mix_np(np.uint64(v), np.uint64(k)))\n"
    return s


def gen_impl(name, stages, desc):
    s = "#include <stdint.h>\n"
    s += "static inline uint64_t rotl64(uint64_t x, int r) {\n    r &= 63;\n    return r ? (x << r) | (x >> (64 - r)) : x;\n}\n"
    s += f"// {desc}\n"
    s += "uint64_t mix_hash(uint64_t val, uint64_t key) {\n"
    s += "    uint64_t x = val ^ key;\n"
    for i, (sop, st) in enumerate(stages):
        a, b = st[0], st[1]
        s += f"    {{ uint64_t ra = rotl64(x,{a}), rb = rotl64(x,{b});\n"
        if sop == "lin":
            s += f"      x ^= ra ^ rb ^ rotl64(x,{st[2]}); }}\n"
        elif sop == "keylin":
            s += f"      x ^= (ra & rb) ^ rotl64(key,{st[2]}) ^ rotl64(key,{st[3]}); }}\n"
        else:
            s += f"      x ^= (ra & rb) ^ rotl64(x,{st[2]}); }}\n"
    s += "    x ^= rotl64(key, 13);\n    return x;\n}"
    return s


def gen_rtl(name, stages, desc):
    s = f"// {name}: {desc} (generated by gen_wave11.py)\n"
    s += f"module {name}(\n    input [63:0] val,\n    input [63:0] key,\n    output [63:0] out\n);\n"
    s += "    wire [63:0] x0 = val ^ key;\n"
    for i, (sop, st) in enumerate(stages):
        a, b = st[0], st[1]
        s += f"    wire [63:0] s{i}a = {vl_rotl('x%d' % i, a)};\n"
        s += f"    wire [63:0] s{i}b = {vl_rotl('x%d' % i, b)};\n"
        if sop == "lin":
            s += f"    wire [63:0] s{i}c = {vl_rotl('x%d' % i, st[2])};\n"
            s += f"    wire [63:0] x{i+1} = x{i} ^ s{i}a ^ s{i}b ^ s{i}c;\n"
        elif sop == "keylin":
            s += f"    wire [63:0] s{i}k1 = {vl_rotl('key', st[2])};\n"
            s += f"    wire [63:0] s{i}k2 = {vl_rotl('key', st[3])};\n"
            s += f"    wire [63:0] x{i+1} = x{i} ^ (s{i}a & s{i}b) ^ s{i}k1 ^ s{i}k2;\n"
        else:
            s += f"    wire [63:0] s{i}c = {vl_rotl('x%d' % i, st[2])};\n"
            s += f"    wire [63:0] x{i+1} = x{i} ^ (s{i}a & s{i}b) ^ s{i}c;\n"
    s += f"    wire [63:0] kr = {vl_rotl('key', 13)};\n"
    s += f"    assign out = x{len(stages)} ^ kr;\n"
    s += "endmodule\n"
    return s


def main():
    only = sys.argv[1:] or None
    for (name, stages, desc) in SPECS:
        if only and name not in only:
            continue
        cdir = os.path.join(FB, name)
        os.makedirs(cdir, exist_ok=True)
        with open(os.path.join(cdir, "model.py"), "w") as f:
            f.write(gen_model(name, stages, desc))
        with open(os.path.join(cdir, "impl.c"), "w") as f:
            f.write(gen_impl(name, stages, desc))
        with open(os.path.join(cdir, "rtl.v"), "w") as f:
            f.write(gen_rtl(name, stages, desc))
        import importlib.util, json
        modname = f"wave11_{name}"
        if modname in sys.modules:
            del sys.modules[modname]
        spec = importlib.util.spec_from_file_location(
            modname, os.path.join(cdir, "model.py"))
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        g1 = m.mix(0x0, 0x123456789ABCDEF0)
        g2 = m.mix(0x123456789ABCDEF0, 0x0)
        meta = {
            "name": name,
            "description": desc,
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "rtl_top": name,
            "goldens": [
                {"val": "0x0", "key": "0x123456789abcdef0", "out": hex(g1)},
                {"val": "0x123456789ABCDEF0", "key": "0x0", "out": hex(g2)},
            ],
        }
        with open(os.path.join(cdir, "meta.json"), "w") as f:
            json.dump(meta, f, indent=1)
        print(f"Created {name}: {desc}", flush=True)


if __name__ == "__main__":
    main()
