#!/usr/bin/env python3
"""Generate impl.c for w4t S0 survivors, from bundle meta.json.
Form (bit-exact with model.py):
  x = val ^ key
  3 stages: 2x (x ^= rotl(x,a) & rotl(x,b)); x ^= rotl(x,p)^rotl(x,q)^rotl(x,r)^rotl(x,s)
  out = x ^ rotl(key,13)
"""
import json, os, sys

BASE = "/home/hatch/workspace/mix/exploration/adder_lat/w4term/bundles"

C_TMPL = """#include <stdint.h>
static inline uint64_t rotl64(uint64_t x, int r) {{
    r &= 63;
    return r ? (x << r) | (x >> (64 - r)) : x;
}}
// {name}: w4t 4-term rotl-xor linear (screen keep idx {idx}, fr={fr})
uint64_t mix_hash(uint64_t val, uint64_t key) {{
    uint64_t x = val ^ key;
{body}
    x ^= rotl64(key, 13);
    return x;
}}
"""

def gen(name):
    bdir = os.path.join(BASE, name)
    with open(os.path.join(bdir, "meta.json")) as f:
        meta = json.load(f)
    stages = meta["stages"]
    p, q, r, s = meta["pqrs"]
    lines = []
    for ands in stages:
        for a, b in ands:
            lines.append(f"    x ^= (rotl64(x,{a}) & rotl64(x,{b}));")
        lines.append(f"    x ^= rotl64(x,{p}) ^ rotl64(x,{q}) ^ rotl64(x,{r}) ^ rotl64(x,{s});")
    body = "\n".join(lines)
    code = C_TMPL.format(name=name, idx=meta["screen_idx"], fr=meta["full_rank"], body=body)
    out = os.path.join(bdir, "impl.c")
    with open(out, "w") as f:
        f.write(code)
    print(f"wrote {out}")

if __name__ == "__main__":
    for name in sys.argv[1:]:
        gen(name)
