#!/usr/bin/env python3
"""Generate + verify fast_battery bundles for W3' screen KEEPs.

Reads adder_lat/w3prime/w3prime_screen.jsonl, selects up to 4 KEEPs
(best z_seq, distinct P constants preferred), generates bundles via
wave14/gen_wave14.py's gen_model/gen_c/gen_rtl (identical W3 form),
then verifies:
  - bundle model.py mix() == screen w3_model on 2000 vec x 3 keys
  - compiled C impl == Python model on the same vectors
  - goldens in meta.json (2 vectors, wave-14 bar)

Usage: python3 gen_w3prime.py [--dry]   (dry = select+report only)
"""
import importlib.util
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
AL = "/home/hatch/workspace/mix/exploration/adder_lat"
W14 = os.path.join(AL, "wave14")
FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"
JSONL = os.path.join(HERE, "w3prime_screen.jsonl")

sys.path.insert(0, W14)
sys.path.insert(0, os.path.join(AL, "w3prime"))
from gen_wave14 import gen_model, gen_c, gen_rtl  # noqa: E402

import numpy as np  # noqa: E402

M64 = np.uint64(0xFFFFFFFFFFFFFFFF)
KEYS3 = [0x123456789ABCDEF0, 0x0F0F0F0F0F0F0F0F, 0xAAAAAAAAAAAAAAAA]


def rotl(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x


def gf(a, C):
    res = np.zeros(a.shape, dtype=np.uint64)
    p = a.copy()
    c = int(C)
    while c:
        if c & 1:
            res ^= p
        hi = (p >> np.uint64(63)) & np.uint64(1)
        p = ((p << np.uint64(1)) & M64) ^ (hi * np.uint64(0x1B))
        c >>= 1
    return res


def w3_model(V, key, stages, P):
    """Screen form (must match screen_w3prime.py::w3_model exactly)."""
    K = np.full(np.shape(V), np.uint64(key), dtype=np.uint64)
    x = (np.asarray(V, dtype=np.uint64) ^ K) & M64
    for ands in stages:
        for a, b in ands:
            x = (x ^ (rotl(x, a) & rotl(x, b))) & M64
        x = gf(x, P)
    return (x ^ rotl(K, 13)) & M64


def load_keeps():
    keeps = []
    with open(JSONL) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("verdict") == "KEEP":
                keeps.append(r)
    return keeps


def select(keeps, n=4):
    # best z_seq first, distinct P preferred
    sk = sorted(keeps, key=lambda r: r["z_seq"])
    out, seen_p = [], set()
    for r in sk:
        if r["P"] not in seen_p:
            out.append(r)
            seen_p.add(r["P"])
        if len(out) == n:
            break
    for r in sk:
        if len(out) == n:
            break
        if r not in out:
            out.append(r)
    return out


def verify_bundle(name, stages, P):
    """model.py == screen form (2000 vec x 3 keys); C == Python."""
    spec = importlib.util.spec_from_file_location(
        "m_" + name, os.path.join(FB, name, "model.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    rng = np.random.default_rng(0x23E4 & 0xFFFFFFFF)
    vecs = rng.integers(0, 2**64, size=2000, dtype=np.uint64)
    st = [[(int(a), int(b)) for a, b in ands] for ands in stages]
    for k in KEYS3:
        ref = w3_model(vecs, k, st, P)
        got = np.array([m.mix(int(v), k) for v in vecs], dtype=np.uint64)
        if not np.array_equal(ref, got):
            bad = np.nonzero(ref != got)[0][0]
            return False, "model mismatch at vec %d key %#x" % (bad, k)
    # C == Python
    csrc = os.path.join(FB, name, "impl.c")
    test_c = os.path.join("/tmp", "w3p_test_%s.c" % name)
    with open(test_c, "w") as f:
        f.write('#include <stdio.h>\n#include <stdint.h>\n')
        f.write(open(csrc).read())
        f.write('int main(void){uint64_t vs[]={')
        f.write(','.join('0x%016xULL' % int(v) for v in vecs[:64]))
        f.write('};for(int i=0;i<64;i++){printf("%016llx\\n",'
                '(unsigned long long)mix_hash(vs[i],0x123456789ABCDEF0ULL));}'
                'return 0;}\n')
    exe = test_c + ".exe"
    r = subprocess.run(["gcc", "-O2", "-o", exe, test_c],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return False, "gcc failed: " + r.stderr[:200]
    r = subprocess.run([exe], capture_output=True, text=True)
    for i, line in enumerate(r.stdout.strip().split("\n")):
        if int(line.strip(), 16) != m.mix(int(vecs[i]), 0x123456789ABCDEF0):
            return False, "C mismatch at vec %d" % i
    return True, "ok"


def main():
    dry = "--dry" in sys.argv
    keeps = load_keeps()
    print("KEEPs in JSONL: %d" % len(keeps), flush=True)
    for r in sorted(keeps, key=lambda r: r["z_seq"]):
        print("  idx=%d z_seq=%.2f z_rnd=%.2f rank=%d P=%s stages=%s"
              % (r["idx"], r["z_seq"], r["z_rnd"], r["full_rank"], r["P"],
                 r["stages"]), flush=True)
    sel = select(keeps)
    print("selected %d:" % len(sel), flush=True)
    for i, r in enumerate(sel):
        print("  al_w3p_%s <- idx=%d z_seq=%.2f" % ("abcd"[i], r["idx"], r["z_seq"]),
              flush=True)
    if dry:
        return
    for i, r in enumerate(sel):
        name = "al_w3p_" + "abcd"[i]
        stages = [[(int(a), int(b)) for a, b in ands]
                  for ands in r["stages"]]
        P = int(r["P"], 16)
        d = os.path.join(FB, name)
        os.makedirs(d, exist_ok=True)
        open(os.path.join(d, "model.py"), "w").write(
            gen_model(name, stages, P, r["z_seq"], r["z_rnd"]))
        open(os.path.join(d, "impl.c"), "w").write(
            gen_c(name, stages, P, r["z_seq"]))
        open(os.path.join(d, "rtl.v"), "w").write(
            gen_rtl(name, stages, P, r["z_seq"]))
        spec = importlib.util.spec_from_file_location("m_" + name,
              os.path.join(d, "model.py"))  # noqa: E128
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        goldens = []
        for v, k in [(0x0, 0x123456789ABCDEF0),
                     (0x123456789ABCDEF0, 0x0)]:
            goldens.append({"val": hex(v), "key": hex(k),
                            "out": hex(m.mix(v, k))})
        meta = {
            "name": name,
            "description": "W3' d-constrained 3-stage word-AND, "
                           "P=0x%016x (screen z_seq=%.2f z_rnd=%.2f)" %
                           (P, r["z_seq"], r["z_rnd"]),
            "screen_keys": ["0x123456789abcdef0", "0x0"],
            "practrand_keys": ["0x123456789abcdef0", "0x0"],
            "goldens": goldens,
            "rtl_top": name,
        }
        json.dump(meta, open(os.path.join(d, "meta.json"), "w"), indent=1)
        ok, msg = verify_bundle(name, stages, P)
        print("bundle %s: verify %s (%s)" % (name, "PASS" if ok else "FAIL",
              msg), flush=True)
        if not ok:
            sys.exit(1)
    print("ALL BUNDLES OK", flush=True)


if __name__ == "__main__":
    main()
