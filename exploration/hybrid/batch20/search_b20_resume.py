"""Batch-20 resume (post 19:47:25Z reboot): MID + hill-climb from saved triage.

Triage (100 draws) completed 19:36Z -> search_b20_results.json. The MID phase
(11/12 evals done, logged to search_b20.log) died in the reboot and its results
were never dumped (the original script only wrote JSON at end of triage and at
end of hill-climb). This script rebuilds the MID shortlist from the triage
JSON and re-runs MID + hill-climb faithfully. Writes to a NEW results file so
the triage evidence file is preserved.
"""
import sys, json, random, time
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/hybrid/batch20')
from s2proxy_b20 import s2proxy_b20, cost_est

SEED = 20261011  # resume seed (original triage used 20261010)
random.seed(SEED)

N_TRIAGE = 1 << 15
N_MID = 1 << 17
N_FINE = 1 << 18

TRI = '/home/hatch/workspace/mix/exploration/hybrid/batch20/search_b20_results.json'
RES = '/home/hatch/workspace/mix/exploration/hybrid/batch20/search_b20_mid_final.json'


def rand_rot():
    return random.randrange(64)


def rand_stage(kind):
    while True:
        r = [rand_rot() for _ in range(6)]
        if len(set(r)) == 6:
            return tuple([kind] + r)


t0 = time.time()
tri = json.load(open(TRI))
assert len(tri) == 100, f"expected 100 triage records, got {len(tri)}"
rows = sorted(((x['z'], x['cost'], x['hyp'], tuple(map(tuple, x['stages'])))
               for x in tri), key=lambda r: (r[0], r[1]))
print(f"loaded {len(rows)} triage records; shortlist top 12", flush=True)

mid = []
for z, c, hname, st in rows[:12]:
    z2, d2, b2 = s2proxy_b20(st, n=N_MID)
    mid.append((z2, c, hname, st, d2, b2))
    print(f"MID {hname}: z={z2:.1f} cost={c:.2f}u d={d2:#x}b{b2}", flush=True)
print(f"MID done in {(time.time()-t0)/60:.1f} min", flush=True)


def mutate(st):
    st = list(st)
    i = random.randrange(len(st))
    st[i] = rand_stage(st[i][0])
    return tuple(st)


final = []
for z2, c, hname, st, d2, b2 in sorted(mid, key=lambda r: (r[0], r[1]))[:8]:
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
               for z, c, h, s, d, b in sorted(final, key=lambda r: (r[0], r[1]))],
              open(RES, 'w'))

final.sort(key=lambda r: (r[0], r[1]))
print("\n=== TOP 8 (n=2^18, hill-climbed) ===")
for z, c, hname, st, d, b in final:
    print(f"z={z:6.1f} cost={c:.2f}u {hname} d={d:#x}b{b}")
json.dump([{'z': z, 'cost': c, 'hyp': h, 'stages': s, 'd0': d, 'bit': b}
           for z, c, h, s, d, b in final], open(RES, 'w'))
print("saved", RES, flush=True)
