#!/usr/bin/env python3
"""Bundles for remaining MU5 reserve keeps (after 234/266a/266b/282), z-ordered.
Schedules verbatim from search_b28_results.json (rerun-complete JSON)."""
import importlib.util, json, os, sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/hybrid/batch21")
import gen_b28 as G
FB = G.FB
CANDS = [
    ("hyb28_mu5_304a", 3.04, 28, [(39,27,37,26),(15,33,52,28),(37,33,7,10),(56,2,58,50),(53,24,37,9)]),
    ("hyb28_mu5_304b", 3.04, 28, [(33,48,16,39),(54,60,51,44),(34,37,30,3),(48,19,43,26),(42,33,61,32)]),
    ("hyb28_mu5_323",  3.23, 26, [(30,57,51,25),(6,9,47,23),(33,60,9,58),(8,5,36,31),(27,16,51,37)]),
    ("hyb28_mu5_324",  3.24, 27, [(62,50,55,2),(48,58,23,30),(44,45,7,40),(49,26,32,35),(46,51,43,44)]),
    ("hyb28_mu5_325",  3.25, 22, [(39,61,24,4),(57,43,58,6),(36,24,20,40),(53,23,47,12),(17,60,49,18)]),
    ("hyb28_mu5_326",  3.26, 23, [(15,17,6,21),(44,12,19,8),(15,1,31,18),(7,36,46,55),(32,13,52,25)]),
    ("hyb28_mu5_328",  3.28, 30, [(21,19,31,24),(43,22,32,4),(22,30,34,5),(52,23,60,37),(58,62,48,11)]),
    ("hyb28_mu5_339",  3.39, 22, [(20,10,14,12),(49,13,53,33),(43,38,45,24),(60,17,62,25),(46,52,8,32)]),
    ("hyb28_mu5_351",  3.51, 27, [(3,63,49,36),(23,17,51,55),(53,38,14,9),(20,2,35,25),(5,50,59,52)]),
    ("hyb28_mu5_443",  4.43, 21, [(36,29,27,48),(32,8,56,50),(50,25,27,63),(24,56,2,54),(43,51,16,5)]),
    ("hyb28_mu5_471",  4.71, 22, [(45,39,27,54),(41,18,60,20),(56,32,20,61),(62,28,5,23),(44,62,41,10)]),
    ("hyb28_mu5_480",  4.80, 25, [(46,42,28,52),(15,56,50,25),(18,41,32,24),(50,26,35,46),(12,16,4,21)]),
    ("hyb28_mu5_568",  5.68, 24, [(4,60,54,56),(38,46,13,21),(38,29,40,6),(26,1,49,56),(51,30,44,61)]),
    ("hyb28_mu5_570",  5.70, 18, [(10,29,11,6),(6,37,54,21),(56,62,48,1),(26,39,46,13),(1,38,53,32)]),
    ("hyb28_mu5_621",  6.21, 23, [(29,13,17,8),(46,33,51,2),(62,17,32,35),(19,3,29,9),(37,30,36,35)]),
]
for name, z, dd, stages in CANDS:
    G.NAME, G.Z, G.D, G.STAGES = name, z, dd, [tuple(s) for s in stages]
    d = os.path.join(FB, name); os.makedirs(d, exist_ok=True)
    open(os.path.join(d,"model.py"),"w").write(G.gen_model(name, G.STAGES, z))
    open(os.path.join(d,"impl.c"),"w").write(G.gen_c(name, G.STAGES, z))
    open(os.path.join(d,"rtl.v"),"w").write(G.gen_rtl(name, G.STAGES, z))
    spec = importlib.util.spec_from_file_location("m_"+name, os.path.join(d,"model.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    rng = __import__("random").Random(0xB28)
    for _ in range(2000):
        v,k = rng.getrandbits(64), rng.getrandbits(64)
        assert m.mix(v,k) == G.ref_mix(G.STAGES, v, k)
    goldens = [{"val": hex(v), "key": hex(k), "out": hex(m.mix(v,k))} for v,k in [(0x0,0x123456789ABCDEF0),(0x123456789ABCDEF0,0x0)]]
    meta = {"name": name, "description": "batch-28 MU5 MUX-gate 5-stage reserve keep (triage z=%.2f, D=%d)"%(z,dd),
            "screen_keys": ["0x123456789abcdef0","0x0"], "practrand_keys": ["0x123456789abcdef0","0x0"],
            "goldens": goldens, "rtl_top": name, "triage_z": z, "stages": [list(s) for s in stages]}
    json.dump(meta, open(os.path.join(d,"meta.json"),"w"), indent=1)
    print("wrote bundle %s z=%.2f bit-exact 2000/2000" % (name, z), flush=True)
print("RESERVE BUNDLES DONE: %d" % len(CANDS))
