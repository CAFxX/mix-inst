"""Batch-20 triage: fused maj+chi body hypotheses via DIFF proxy.

Hypotheses (co-design: rotation constants searched per hypothesis):
  H1 fm4: 4-stage fused maj+chi (parallel)  ~18.8u est
  H2 fm5: 5-stage fused maj+chi (parallel)  ~23.5u est (quality play)
  H3 dm4: 4-stage dual-maj fused             ~18.8u est (control)
  H4 rf5: 5-stage replacement-form fused     ~23.5u est (diagnostic)
KEEP bar: hill-climbed z < 18 (same as track-3/batch-19).
"""
import sys, json, random, time
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/hybrid/batch20')
from s2proxy_b20 import s2proxy_b20, cost_est

SEED = 20261010
random.seed(SEED)

N_TRIAGE = 1 << 15
N_MID = 1 << 17
N_FINE = 1 << 18

RES = '/home/hatch/workspace/mix/exploration/hybrid/batch20/search_b20_results.json'


def rand_rot():
    return random.randrange(64)


def rand_stage(kind):
    while True:
        r = [rand_rot() for _ in range(6)]
        if len(set(r)) == 6:
            return (kind,) + tuple(r)


HYPS = {
    'fm4': ('fm', 4, 35),
    'fm5': ('fm', 5, 25),
    'dm4': ('dm', 4, 25),
    'rf5': ('rf', 5, 15),
}

results = []
t0 = time.time()
for hname, (kind, nst, draws) in HYPS.items():
    best = None
    for i in range(draws):
        st = tuple(rand_stage(kind) for _ in range(nst))
        z, d, b = s2proxy_b20(st, n=N_TRIAGE)
        c = cost_est(st)
        results.append((z, c, hname, st))
        if best is None or z < best[0]:
            best = (z, c, st)
    print(f">> {hname} best triage ({draws} draws): z={best[0]:.1f} "
          f"cost={best[1]:.2f}u", flush=True)
    json.dump([{'z': z, 'cost': c, 'hyp': h, 'stages': s}
               for z, c, h, s in sorted(results)],
              open(RES, 'w'))

print(f"triage done in {(time.time()-t0)/60:.1f} min", flush=True)

short = sorted(results)[:12]
mid = []
for z, c, hname, st in short:
    z2, d2, b2 = s2proxy_b20(st, n=N_MID)
    mid.append((z2, c, hname, st, d2, b2))
    print(f"MID {hname}: z={z2:.1f} cost={c:.2f}u d={d2:#x}b{b2}", flush=True)


def mutate(st):
    st = list(st)
    i = random.randrange(len(st))
    st[i] = rand_stage(st[i][0])
    return tuple(st)


final = []
for z2, c, hname, st, d2, b2 in sorted(mid)[:8]:
    cur, curz = st, z2
    for _ in range(10):
        cand = mutate(cur)
        zc, _, _ = s2proxy_b20(cand, n=N_TRIAGE)
        if zc < curz:
            cur, curz = cand, zc
    zf, df, bf = s2proxy_b20(cur, n=N_FINE)
    final.append((zf, cost_est(cur), hname, cur, df, bf))
    print(f"HILL {hname}: z={zf:.1f} cost={cost_est(cur):.2f}u "
          f"d={df:#x}b{bf}", flush=True)
    json.dump([{'z': z, 'cost': c, 'hyp': h, 'stages': s, 'd0': d, 'bit': b}
               for z, c, h, s, d, b in sorted(final)],
              open(RES, 'w'))

final.sort()
print("\n=== TOP 8 (n=2^18, hill-climbed) ===")
for z, c, hname, st, d, b in final:
    print(f"z={z:6.1f} cost={c:.2f}u {hname} d={d:#x}b{b}")
json.dump([{'z': z, 'cost': c, 'hyp': h, 'stages': s, 'd0': d, 'bit': b}
           for z, c, h, s, d, b in final], open(RES, 'w'))
print("saved", RES, flush=True)
