"""Batch-19 co-design search: 5-stage maj/chi hybrids via DIFF proxy.

Co-design (not blind swap): for each stage-order pattern, rotation constants
for BOTH stage types are searched jointly against the DIFF proxy (all 64
single-bit deltas + multi-bit). Calibration: maj5d(fz22 sched) z=250.8,
chi5(al_chi8 sched) z=134.2 -- both proxy-fail; schedules must be searched.
"""
import sys, json, random, time
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/hybrid/batch19')
from s2proxy_mc import s2proxy_mc, cost_est

SEED = 20261010
random.seed(SEED)

N_TRIAGE = 1 << 15   # fast triage (~8s/cand)
N_MID = 1 << 17      # shortlist (~40s/cand)
N_FINE = 1 << 18     # final (~80s/cand)

RES = '/home/hatch/workspace/mix/exploration/hybrid/batch19/search_mc_results.json'


def rand_rot():
    return random.randrange(64)


def rand_stage(kind):
    while True:
        a, b, c = rand_rot(), rand_rot(), rand_rot()
        if len({a, b, c}) == 3:
            return ('maj' if kind == 'M' else 'chi', a, b, c)


PATTERNS = {
    'MCMCM': 'MCMCM',  # 3M+2C 18.8u
    'MMCCM': 'MMCCM',  # 3M+2C 18.8u
    'MCCMM': 'MCCMM',  # 3M+2C 18.8u
    'CMMCM': 'CMMCM',  # 3M+2C 18.8u
    'MCMMC': 'MCMMC',  # 3M+2C 18.8u
    'CCMCM': 'CCMCM',  # 2M+3C 18.0u
    'MCCCM': 'MCCCM',  # 2M+3C 18.0u
    'MMMCM': 'MMMCM',  # 4M+1C 19.7u (latency long shot)
}
DRAWS = 30

results = []
t0 = time.time()
for pname, pat in PATTERNS.items():
    best = None
    for i in range(DRAWS):
        st = tuple(rand_stage(k) for k in pat)
        z, d, b = s2proxy_mc(st, n=N_TRIAGE)
        c = cost_est(st)
        results.append((z, c, pname, st))
        if best is None or z < best[0]:
            best = (z, c, st)
    print(f">> {pname} best triage ({DRAWS} draws): z={best[0]:.1f} "
          f"cost={best[1]:.2f}u {best[2]}", flush=True)
    json.dump([{'z': z, 'cost': c, 'pattern': p, 'stages': s}
               for z, c, p, s in sorted(results)],
              open(RES, 'w'))

print(f"triage done in {(time.time()-t0)/60:.1f} min", flush=True)

# shortlist: top-16 triage -> mid eval
short = sorted(results)[:16]
mid = []
for z, c, pname, st in short:
    z2, d2, b2 = s2proxy_mc(st, n=N_MID)
    mid.append((z2, c, pname, st, d2, b2))
    print(f"MID {pname}: z={z2:.1f} cost={c:.2f}u d={d2:#x}b{b2} {st}", flush=True)

# hill-climb on top-8 mid, 10 steps, triage-speed
def mutate(st):
    st = list(st)
    i = random.randrange(len(st))
    kind = 'M' if st[i][0] == 'maj' else 'C'
    st[i] = rand_stage(kind)
    return tuple(st)

final = []
for z2, c, pname, st, d2, b2 in sorted(mid)[:8]:
    cur, curz = st, z2
    for _ in range(10):
        cand = mutate(cur)
        zc, _, _ = s2proxy_mc(cand, n=N_TRIAGE)
        if zc < curz:
            cur, curz = cand, zc
    zf, df, bf = s2proxy_mc(cur, n=N_FINE)
    final.append((zf, cost_est(cur), pname, cur, df, bf))
    print(f"HILL {pname}: z={zf:.1f} cost={cost_est(cur):.2f}u "
          f"d={df:#x}b{bf} {cur}", flush=True)
    json.dump([{'z': z, 'cost': c, 'pattern': p, 'stages': s, 'd0': d, 'bit': b}
               for z, c, p, s, d, b in sorted(final)],
              open(RES, 'w'))

final.sort()
print("\n=== TOP 8 (n=2^18, hill-climbed) ===")
for z, c, pname, st, d, b in final:
    print(f"z={z:6.1f} cost={c:.2f}u {pname} d={d:#x}b{b}: {st}")
json.dump([{'z': z, 'cost': c, 'pattern': p, 'stages': s, 'd0': d, 'bit': b}
           for z, c, p, s, d, b in final], open(RES, 'w'))
print("saved", RES, flush=True)
