#!/usr/bin/env python3
"""Parse literature_lowlatency_add2.txt, verify, emit pool_add2.json"""
import json

def du_of(sb):
    mx = 0
    for da in range(1, 16):
        cnt = {}
        for x in range(16):
            db = sb[x] ^ sb[x ^ da]
            cnt[db] = cnt.get(db, 0) + 1
        mx = max(mx, max(cnt.values()))
    return mx

def nl_of(sb):
    mx = 0
    for a in range(1, 16):
        for b in range(1, 16):
            s = 0
            for x in range(16):
                px = bin(a & x).count('1') & 1
                py = bin(b & sb[x]).count('1') & 1
                s += 1 if px == py else -1
            mx = max(mx, abs(s))
    return 8 - mx // 2

pool = []
with open('/home/hatch/workspace/mix/exploration/round24/sbox_pool/literature_lowlatency_add2.txt') as f:
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        name = parts[0]
        sb = [int(x, 16) for x in parts[1:]]
        assert len(sb) == 16, name
        assert sorted(sb) == list(range(16)), f"{name} not bijective"
        du, nl = du_of(sb), nl_of(sb)
        assert du == 4 and nl == 4, f"{name}: DU={du} NL={nl}"
        pool.append({'name': name, 'table': sb, 'du': du, 'nl': nl})

# dedupe against existing pool tables
existing = {}
import os
for fn in ['pool_broad.json']:
    p = f'/home/hatch/workspace/mix/exploration/round25/{fn}'
    if os.path.exists(p):
        for r in json.load(open(p)):
            t = r['table']
            hs = ''.join(f"{v:x}" for v in t) if isinstance(t, list) else t
            existing[hs] = r['name']
# also check sbox_screen_broad ranked
rp = '/home/hatch/workspace/mix/exploration/round25/sbox_screen_broad/ranked.json'
if os.path.exists(rp):
    for r in json.load(open(rp))['all']:
        if r.get('table'):
            existing[r['table']] = r['name']

for p in pool:
    hexstr = ''.join(f'{v:x}' for v in p['table'])
    if hexstr in existing:
        print(f"SKIP {p['name']}: duplicates {existing[hexstr]} (already measured)")
        continue
    # keep only non-colliding
pool = [p for p in pool if ''.join(f'{v:x}' for v in p['table']) not in existing]

print(f"{len(pool)} verified, all DU=4/NL=4, zero collisions with existing pool")
json.dump(pool, open('/home/hatch/workspace/mix/exploration/round25/pool_add2.json', 'w'), indent=1)
for p in pool:
    print(f"  {p['name']:20s} {''.join(f'{v:x}' for v in p['table'])}")
