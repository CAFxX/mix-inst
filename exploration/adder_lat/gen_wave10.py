#!/usr/bin/env python3
"""Wave-10 generator: NEW directions after wave-9 falsified danger-zone-free
progressive single-AND schedules (all 4 survivors S2-KILLED on broad systematic
differential bias, 34-59/115 deltas |z|>9).

Two prongs, both genuinely new on this track:

Prong A -- dual-AND at 5/6 stages ("dualand" op: x ^= (ra&rb)^(rc&rd)^re).
  Only al_dualand4 (4-stage) was ever tried -> triage KILL (aval 0.1632,
  zmax 162.2), scoped to 4 stages. 5-stage dual-AND carries 10 AND-pairs
  (vs 6 in 6-stage single-AND) at ~5 stages x ~4u = ~20u: directly attacks
  the 19.8u 6-stage floor AND the 5-stage barrier (which was single-pair).
  - al_dualand5a: 5 stages on al_and6a's proven triplets; 2nd AND-pair =
    NEXT stage's (a,b) ("preview pair": rotation multiset stays inside the
    co-designed and6a set; last stage wraps to stage 0).
  - al_dualand5b: 5 stages, fresh independent schedule (not and6a-derived).
  - al_dualand6a: 6 stages on and6a triplets + preview pairs (quality probe:
    does dual-pair structure remove the broad-elevation failure mode?).

Prong B -- heterostage on the KNOWN-CLEAN and6a schedule (control experiment).
  Wave-9's broad elevation might be a resonance of identical repeated stages.
  Same triplets as frontier al_and6a, per-stage op varied:
  - al_het6a: [and,or,and,or,and,or]
  - al_het6b: [and,chi,and,chi,and,chi]  (chi = andnot; al_hybrid6 did
    chi/and alternation at 20.1u with only marginal S1 FLAG)
  If het stays clean -> hetero is safe, free co-design axis. If het shows
  broad elevation too -> the bias is schedule-inherent (but and6a pure-AND
  is clean, so this would be surprising).

Skipped with reason: MAJ3 cascade (track 5 hyb9_maj3_6: 25.8u, too slow;
track 8 fz_majx_5: 29.7u; track 5 batch-11 owns chi/maj3 co-design --
no duplication); 4-stage dual-AND retest (dualand4 kill was decisive,
not marginal); per-stage key fold (O83 killed it).
"""
import os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from gen_wave1 import gen_model, gen_impl, gen_rtl  # noqa: E402

FB = "/home/hatch/workspace/mix/exploration/fast_battery/candidates"

# al_and6a's proven triplets (frontier, all gates clear)
AND6A = [(1, 2, 13), (7, 19, 5), (3, 11, 29), (17, 31, 7), (11, 23, 37), (19, 41, 23)]

def preview_dual(triplets):
    """(a,b,e) triplets -> (a,b,a',b',e) 5-tuples; 2nd pair = next stage's (a,b)."""
    n = len(triplets)
    out = []
    for i, (a, b, e) in enumerate(triplets):
        na, nb, _ = triplets[(i + 1) % n]
        out.append((a, b, na, nb, e))
    return out

DUALAND5A = preview_dual(AND6A[:5])
DUALAND6A = preview_dual(AND6A)
# Fresh 5-stage dual-AND schedule: mixed small/large, all-distinct per stage
DUALAND5B = [(2, 9, 23, 41, 13),
             (5, 17, 31, 53, 7),
             (11, 29, 3, 19, 43),
             (13, 37, 7, 25, 5),
             (19, 47, 11, 33, 17)]

HET6A = [("and", t) if i % 2 == 0 else ("or", t) for i, t in enumerate(AND6A)]
HET6B = [("and", t) if i % 2 == 0 else ("chi", t) for i, t in enumerate(AND6A)]

SPECS = [
    ("al_dualand5a", "dualand", DUALAND5A, False,
     "Wave-10: 5-stage dual-AND on and6a triplets, preview 2nd pair (floor attack)"),
    ("al_dualand5b", "dualand", DUALAND5B, False,
     "Wave-10: 5-stage dual-AND, fresh schedule (floor attack, independent)"),
    ("al_dualand6a", "dualand", DUALAND6A, False,
     "Wave-10: 6-stage dual-AND on and6a triplets, preview 2nd pair (quality probe)"),
    ("al_het6a", "hybrid", HET6A, False,
     "Wave-10: heterostage and/or alternating on and6a triplets (resonance control)"),
    ("al_het6b", "hybrid", HET6B, False,
     "Wave-10: heterostage and/chi alternating on and6a triplets (resonance control)"),
]

def main():
    only = sys.argv[1:] or None
    for (name, op, stages, psk, desc) in SPECS:
        if only and name not in only:
            continue
        cdir = os.path.join(FB, name)
        os.makedirs(cdir, exist_ok=True)
        with open(os.path.join(cdir, "model.py"), "w") as f:
            f.write(gen_model(name, op, stages, psk, desc))
        with open(os.path.join(cdir, "impl.c"), "w") as f:
            f.write(gen_impl(name, op, stages, psk, desc))
        with open(os.path.join(cdir, "rtl.v"), "w") as f:
            f.write(gen_rtl(name, op, stages, psk, desc))
        # meta.json (goldens from model) -- mirrors mk_candidate.py
        import importlib.util, json
        modname = f"wave10_{name}"
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
