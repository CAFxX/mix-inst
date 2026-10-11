#!/usr/bin/env python3
"""Bundles for MU5 keeps ranks 2-4 (rank-1 hyb28_mu5_234 died at S1 marginal PB rej=3)."""
import importlib.util, json, os, sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/hybrid/batch21")
import gen_b28 as G
FB = G.FB
CANDS = [
    ("hyb28_mu5_266a", 2.66, 27, [(24,19,61,46),(20,12,30,22),(4,45,56,31),(53,48,18,32),(46,3,37,49)]),
    ("hyb28_mu5_266b", 2.66, 24, [(56,27,53,29),(48,23,15,20),(7,47,2,37),(31,16,57,30),(2,53,21,43)]),
    ("hyb28_mu5_282",  2.82, 27, [(50,57,56,12),(27,22,62,7),(18,10,19,55),(61,38,36,49),(16,26,35,59)]),
]
for name, z, dd, stages in CANDS:
    G.NAME, G.Z, G.D, G.STAGES = name, z, dd, stages
    d = os.path.join(FB, name); os.makedirs(d, exist_ok=True)
    open(os.path.join(d,"model.py"),"w").write(G.gen_model(name, stages, z))
    open(os.path.join(d,"impl.c"),"w").write(G.gen_c(name, stages, z))
    open(os.path.join(d,"rtl.v"),"w").write(G.gen_rtl(name, stages, z))
    spec = importlib.util.spec_from_file_location("m_"+name, os.path.join(d,"model.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    rng = __import__("random").Random(0xB28)
    for _ in range(2000):
        v,k = rng.getrandbits(64), rng.getrandbits(64)
        assert m.mix(v,k) == G.ref_mix(stages, v, k)
    goldens = [{"val": hex(v), "key": hex(k), "out": hex(m.mix(v,k))} for v,k in [(0x0,0x123456789ABCDEF0),(0x123456789ABCDEF0,0x0)]]
    meta = {"name": name, "description": "batch-28 MU5 MUX-gate 5-stage (triage z=%.2f, D=%d)"%(z,dd),
            "screen_keys": ["0x123456789abcdef0","0x0"], "practrand_keys": ["0x123456789abcdef0","0x0"],
            "goldens": goldens, "rtl_top": name, "triage_z": z, "stages": stages}
    json.dump(meta, open(os.path.join(d,"meta.json"),"w"), indent=1)
    print("wrote bundle %s z=%.2f bit-exact 2000/2000" % (name, z), flush=True)
