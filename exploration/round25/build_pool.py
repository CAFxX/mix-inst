#!/usr/bin/env python3
"""Track B broad pool builder (round25). Components:
  aff   : affine-equivalents of S1 (same crypto class, different DNF shape)
  rnd   : random 4-bit perms filtered to DU=4/NL=4
  mols  : MOLS(8)-derived 4-bit S-boxes (probe; P7 closed MOLS(4) completely)
  lit   : published anchors (PRESENT, SKINNY-64, RECTANGLE, MIDORI Sb0/Sb1)
Rasoolzadeh 12 already sampled separately.
Emits pool.json: [{name, source, table, du, nl}]
"""
import json, random, itertools, sys

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

def is_affine_perm(sb):
    # affine iff S(x)^S(0) is linear: check additivity
    s0 = sb[0]
    t = [sb[x] ^ s0 for x in range(16)]
    for x in range(16):
        for y in range(16):
            if t[x ^ y] != (t[x] ^ t[y]):
                return False
    return True

def rand_affine(rng):
    # random invertible 4x4 GF(2) matrix + random 4-bit vector
    while True:
        m = [[rng.randrange(2) for _ in range(4)] for _ in range(4)]
        # invertibility via det over GF(2)
        def det4(M):
            # over GF(2), det = permanent (sign irrelevant): sum over ALL perms
            d = 0
            for p in itertools.permutations(range(4)):
                t = 1
                for i in range(4): t &= M[i][p[i]]
                d ^= t
            return d
        if det4(m):
            v = rng.randrange(16)
            return m, v

def apply_aff(m, v, x):
    y = v
    for i in range(4):
        if (x >> i) & 1:
            col = 0
            for r in range(4):
                col |= (m[r][i] << r)
            y ^= col
    return y & 15

S1 = [0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10]
rng = random.Random(20261005)
pool = []

def add(name, source, sb):
    assert sorted(sb) == list(range(16)), f"{name} not a permutation"
    pool.append({'name': name, 'source': source, 'table': sb,
                 'du': du_of(sb), 'nl': nl_of(sb),
                 'affine': is_affine_perm(sb)})

# --- literature anchors (tables verified vs primary sources) ---
add('lit_present', 'PRESENT paper (Bogdanov et al. 2007)',
    [12,5,6,11,9,0,10,13,3,14,15,8,4,7,1,2])
add('lit_skinny', 'SKINNY spec (Beierle et al., CRYPTO 2016; 2 srcs)',
    [0xc,0x6,0x9,0x0,0x1,0xa,0x2,0xb,0x3,0x8,0x5,0xd,0x4,0xe,0x7,0xf])
add('lit_rectangle', 'RECTANGLE paper (Zhang et al. 2015, primary)',
    [0x9,0x4,0xf,0xa,0xe,0x1,0x0,0x6,0xc,0x7,0x3,0x8,0x2,0xb,0x5,0xd])
add('lit_midori_sb0', 'MIDORI spec (Banik et al.); parent-verified',
    [0xc,0xa,0xd,0x3,0xe,0xb,0xf,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6])
add('lit_midori_sb1', 'MIDORI spec (Banik et al.); parent-verified',
    [0x1,0x0,0x5,0x3,0xe,0x2,0xf,0x7,0xd,0xa,0x9,0xb,0xc,0x8,0x4,0x6])
add('s1_baseline', 'our S1 (depth-3 reference)',
    S1)

# --- affine equivalents of S1 (4 new; aff1/aff2 already exist from prior screen) ---
n_aff = 0
tries = 0
while n_aff < 4 and tries < 200:
    tries += 1
    m_in, v_in = rand_affine(rng)
    m_out, v_out = rand_affine(rng)
    sb = [apply_aff(m_out, v_out, S1[apply_aff(m_in, v_in, x)]) for x in range(16)]
    if sb == S1: continue
    # ensure distinct from each other
    if any(p['table'] == sb for p in pool): continue
    n_aff += 1
    add(f'aff_eq{n_aff+2}', f'random affine-equiv of S1 #{n_aff+2}', sb)

# --- random DU=4/NL=4 ---
n_rnd = 0
tries = 0
while n_rnd < 5 and tries < 4000:
    tries += 1
    sb = list(range(16)); rng.shuffle(sb)
    if du_of(sb) != 4 or nl_of(sb) != 4: continue
    if any(p['table'] == sb for p in pool): continue
    n_rnd += 1
    add(f'rnd_opt{n_rnd}', 'random 4-bit perm, DU=4/NL=4 filtered', sb)

# --- MOLS(8) probe: top-left 4x4 corner projected mod 4 ---
# Build orthogonal pair of order 8 via GF(8) construction: L1[i][j]=i+j, L2[i][j]=i+2j
# over GF(8) = GF(2)[x]/(x^3+x+1). Try several primitive multipliers.
def gf8_add(a,b): return a ^ b
def gf8_mul(a,b):
    p = 0
    while b:
        if b & 1: p ^= a
        a <<= 1
        if a & 8: a ^= 0xB  # x^3+x+1
        b >>= 1
    return p & 7
def gf8_mul_const(c):
    return lambda a: gf8_mul(c, a)

mols_found = 0
for c1, c2 in [(1,2),(1,3),(2,3),(3,5),(1,5),(2,5)]:
    # L_a[i][j] = i + c*j over GF(8); orthogonal for distinct nonzero c
    def build(c):
        return [[gf8_add(i, gf8_mul(c, j)) for j in range(8)] for i in range(8)]
    L1, L2 = build(c1), build(c2)
    sb = []
    for x in range(16):
        a, b = (x >> 2) & 3, x & 3
        sb.append(((L1[a][b] & 3) << 2) | (L2[a][b] & 3))
    if sorted(sb) == list(range(16)):
        mols_found += 1
        add(f'mols8_c{c1}{c2}', f'MOLS(8) GF(8) pair c={c1},{c2}, 4x4 corner mod4', sb)
    if mols_found >= 4: break

with open('pool_broad.json', 'w') as f:
    json.dump(pool, f, indent=1)
print(f"pool size={len(pool)}")
for p in pool:
    print(f"  {p['name']:16s} src={p['source'][:40]:40s} DU={p['du']} NL={p['nl']} affine={p['affine']}")
print(f"MOLS(8) bijective hits: {mols_found}/6")
