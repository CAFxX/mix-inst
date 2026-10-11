"""Search [t3/and mixes] + dual-last-stage hybrids via extended proxy."""
import sys, itertools, random
sys.path.insert(0, '/home/hatch/workspace/mix/exploration/hybrid/batch18')
from s2proxy_dual import s2proxy_dual, cost_est

random.seed(42)

# danger-zone-free rotations (track-3 wave-9: avoid [28,36], prefer >=54 or spread)
def rand_rot():
    while True:
        r = random.randrange(64)
        if not (28 <= r <= 36):
            return r

def rand_and():
    a, b, c = rand_rot(), rand_rot(), rand_rot()
    # ensure some spread
    if len({a,b,c}) < 3: return rand_and()
    return ('and', a, b, c)

def rand_t3():
    a,b,c,e = rand_rot(), rand_rot(), rand_rot(), rand_rot()
    if len({a,b,c,e}) < 4: return rand_t3()
    return ('t3', a, b, c, e)

def rand_dual():
    a,b,c,d,e = (rand_rot() for _ in range(5))
    if len({a,b,c,d,e}) < 5: return rand_dual()
    return ('dual', a, b, c, d, e)

# fixed structures to test (prefix + dual last)
STRUCTS = {
    'A_t3_and3_dual': lambda: [rand_t3(), rand_and(), rand_and(), rand_and(), rand_dual()],
    'B_and3_t3_dual': lambda: [rand_and(), rand_and(), rand_and(), rand_t3(), rand_dual()],
    'C_and4_dual':    lambda: [rand_and(), rand_and(), rand_and(), rand_and(), rand_dual()],
    'D_t3t3_and2_dual': lambda: [rand_t3(), rand_t3(), rand_and(), rand_and(), rand_dual()],
}

results = []
for name, gen in STRUCTS.items():
    for i in range(30):
        st = gen()
        z, d, b = s2proxy_dual(st)
        c = cost_est(st)
        results.append((z, c, name, st))
        print(f"{name}#{i}: z={z:6.1f} cost={c:.2f}u", flush=True)

results.sort()
print("\n=== TOP 10 ===")
for z, c, name, st in results[:10]:
    print(f"z={z:6.1f} cost={c:.2f}u {name}: {st}")

# save all
import json
json.dump([{'z':z,'cost':c,'name':n,'stages':s} for z,c,n,s in results],
          open('/home/hatch/workspace/mix/exploration/hybrid/batch18/search_dual_results.json','w'))
