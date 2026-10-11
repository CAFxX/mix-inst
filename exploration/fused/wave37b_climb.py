#!/usr/bin/env python3
"""Wave-37b guided schedule hill-climb (b33c / batch-24b playbook).

Starts from a near-miss random draw (KEEP bar z<10) and hill-climbs the
rotation schedule to minimize SEQ exact-DIFF maxworst|z| (all 10 keys --
the exact gate, not a proxy). marg proxy is a feasibility constraint:
a mutant that fails marg is rejected (objective = +inf).

Moves: resample exactly one rotation field, respecting structural
constraints (r1 odd, m even nonzero, a!=b, h!=i, p!=q). Strict improvement
only; first-improvement scan order randomized per iteration.

Logs per-eval JSONL to wave37b_climb_t<TR>_s<SEED>.jsonl. A new best with
z<10 is ALSO echoed LOUD + appended to wave37b_climb_HITS.jsonl (the
escalation trigger -- do not wait for the climb to finish).

Usage: wave37b_climb.py <START_TRY> <N_EVAL> [SEED]
"""
import copy
import json
import random
import sys
import time

sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fused")
from wave37_lib import make_mix37, _ODD_R1, _EVEN_M
from wave35_lib import _marg_proxy, seq_exact_diff

START_TRY = int(sys.argv[1])
N_EVAL = int(sys.argv[2])
SEED = int(sys.argv[3], 0) if len(sys.argv) > 3 else 0xC1B
JSONL = "wave37_3st_L3_diag.jsonl"
OUTP = f"wave37b_climb_t{START_TRY}_s{SEED:x}"

src = None
for line in open(JSONL):
    r = json.loads(line)
    if r["try"] == START_TRY:
        src = r
        break
assert src is not None, f"fail-loud: try {START_TRY} not found"
assert src["marg_ok"], "fail-loud: start must be marg-feasible"
assert "n_lin" in src["cand"] and src["cand"]["n_lin"] == 3, "fail-loud: not L=3"


def _dpair(rng):
    a = rng.randint(1, 63)
    b = rng.randint(1, 63)
    while b == a:
        b = rng.randint(1, 63)
    return a, b


def mutate(cand, rng):
    """Resample exactly one rotation field, respecting constraints."""
    c = copy.deepcopy(cand)
    fields = ["r1", "r2", "p", "q", "m"]
    for si in range(len(c["stages"])):
        nl = len(c["stages"][si][2])
        fields += [(si, "a"), (si, "b")] + [(si, "cx", k) for k in range(nl)]
        fields += [(si, "f"), (si, "g"), (si, "h"), (si, "i")]
        fields += [(si, "cy", k) for k in range(nl)]
        fields += [(si, "mx"), (si, "ny")]
    pick = rng.choice(fields)
    if pick == "r1":
        c["r1"] = rng.choice(_ODD_R1)
    elif pick == "r2":
        c["r2"] = rng.randint(1, 63)
    elif pick == "m":
        c["m"] = rng.choice(_EVEN_M)
    elif pick in ("p", "q"):
        v = rng.randint(0, 63)
        other = c["q"] if pick == "p" else c["p"]
        while v == other:
            v = rng.randint(0, 63)
        c[pick] = v
    else:
        si, name = pick[0], pick[1]
        st = list(c["stages"][si])
        # stage tuple: (a,b,cx,f,g,h,i,cy,mx,ny); cx/cy are lists post-JSON
        if name == "a":
            a, b = _dpair(rng)
            st[0], st[1] = a, b
        elif name == "b":
            a, b = _dpair(rng)
            st[0], st[1] = a, b
        elif name == "h" or name == "i":
            h, i = _dpair(rng)
            st[5], st[6] = h, i
        elif name == "cx":
            k = pick[2]
            cx = list(st[2])
            cx[k] = rng.randint(0, 63)
            st[2] = cx
        elif name == "cy":
            k = pick[2]
            cy = list(st[7])
            cy[k] = rng.randint(0, 63)
            st[7] = cy
        else:  # f, g, mx, ny
            idx = {"f": 3, "g": 4, "mx": 8, "ny": 9}[name]
            st[idx] = rng.randint(0, 63)
        c["stages"][si] = st
    return c


def evaluate(cand):
    """(marg_ok, seq_z). marg is the feasibility gate."""
    mix = make_mix37(cand)
    ok_m, _ = _marg_proxy(mix)
    if not ok_m:
        return False, float("inf")
    z, _ = seq_exact_diff(mix)
    return True, z


def main():
    rng = random.Random(SEED)
    t0 = time.time()
    cur = copy.deepcopy(src["cand"])
    # JSON round-trip normalizes tuples->lists; keep that form (bundle gen handles it)
    cur = json.loads(json.dumps(cur))
    ok, best = evaluate(cur)
    assert ok, "fail-loud: start candidate must evaluate marg-feasible"
    print(f"[climb t{START_TRY}] start z={best:.1f} ({time.time()-t0:.0f}s)", flush=True)
    n_acc = 0
    with open(f"{OUTP}.jsonl", "w") as jf:
        jf.write(json.dumps({"eval": 0, "z": best, "acc": True, "cand": cur}) + "\n")
        jf.flush()
        for ev in range(1, N_EVAL + 1):
            cand = mutate(cur, rng)
            ok_m, z = evaluate(cand)
            acc = ok_m and z < best
            if acc:
                best = z
                cur = cand
                n_acc += 1
            rec = {"eval": ev, "z": z if ok_m else None, "marg_ok": bool(ok_m),
                   "acc": bool(acc), "best": best}
            if acc:
                rec["cand"] = copy.deepcopy(cur)
            jf.write(json.dumps(rec) + "\n")
            jf.flush()
            if acc:
                print(f"[climb t{START_TRY}] eval {ev}: NEW BEST z={best:.2f} "
                      f"({time.time()-t0:.0f}s)", flush=True)
                if best < 10.0:
                    hit = {"start_try": START_TRY, "eval": ev, "z": best,
                           "cand": copy.deepcopy(cur)}
                    with open("wave37b_climb_HITS.jsonl", "a") as hf:
                        hf.write(json.dumps(hit) + "\n")
                    print(f"[climb t{START_TRY}] *** KEEP z={best:.2f} *** "
                          f"logged to wave37b_climb_HITS.jsonl", flush=True)
            elif ev % 20 == 0:
                print(f"[climb t{START_TRY}] eval {ev}: best z={best:.2f} "
                      f"({time.time()-t0:.0f}s)", flush=True)
    print(f"DONE [climb t{START_TRY}]: {N_EVAL} evals, {n_acc} accepts, "
          f"best z={best:.2f}", flush=True)
    print(f"  raw: {OUTP}.jsonl", flush=True)


if __name__ == "__main__":
    main()
