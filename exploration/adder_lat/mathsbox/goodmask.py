"""Principled affine search via the 'good mask' table.
G[a][m] = True iff m.D_a(inv) is balanced (as Boolean function of x).
SAC for S'=C.inv(Ax+b)+d needs: rows(C) subset of good[Ae_i] for all i.
BIC needs: pairwise row-sums also good. So find 8 lin.indep. directions with
8 lin.indep. masks in common good-set whose pairwise sums are also good."""
import numpy as np, pickle
from sbox_math import INV

def build_good():
    # D_a(x) = S[x]^S[x^a] for all a (1..255): shape (255,256) uint8
    xs = np.arange(256, dtype=np.uint8)
    # bits of D_a: (255, 8, 256)
    D = INV[None, :] ^ INV[(xs[None, :] ^ np.arange(1, 256, dtype=np.uint8)[:, None]).astype(np.uint8)]
    bits = ((D[:, None, :] >> np.arange(8)[None, :, None]) & 1).astype(np.uint8)  # (255,8,256)
    # for each mask m (1..255): m.D_a = parity over j of m_j * bits[a,j]
    # compute via tensordot over j
    masks = np.arange(1, 256, dtype=np.uint8)
    MB = ((masks[:, None] >> np.arange(8)[None, :]) & 1).astype(np.uint8)  # (255,8)
    # P[a,m,x] = sum_j MB[m,j]*bits[a,j,x] mod 2
    P = np.tensordot(bits.astype(np.int32), MB.T.astype(np.int32), axes=([1], [0])) % 2  # (255,256,255)
    bal = (P.sum(axis=1) == 128)  # (255,255) : G[a-1, m-1]
    return bal

def lin_indep_vecs(cands, chosen, n=8):
    """greedy: pick from cands (list of uint8) linearly independent from chosen"""
    basis = []
    for v in chosen:
        basis.append(int(v))
    # orthogonalize basis
    def rank_add(basis, v):
        b = list(basis)
        v = int(v)
        for bv in b:
            hb = bv.bit_length() - 1
            if (v >> hb) & 1:
                v ^= bv
        return b, v
    # build current basis in row-echelon
    eb = []
    for v in basis:
        eb, v = rank_add(eb, v)
        if v:
            # insert keeping echelon: simpler to rebuild
            pass
    # simpler: maintain list, do full elimination each pick
    picked = list(chosen)
    def is_indep(picked, v):
        rows = [int(x) for x in picked] + [int(v)]
        r = 0
        rows = rows[:]
        for c in range(8):
            piv = None
            for i in range(r, len(rows)):
                if (rows[i] >> c) & 1:
                    piv = i
                    break
            if piv is None:
                continue
            rows[r], rows[piv] = rows[piv], rows[r]
            for i in range(len(rows)):
                if i != r and ((rows[i] >> c) & 1):
                    rows[i] ^= rows[r]
            r += 1
        return r == len(picked) + 1
    for v in cands:
        if len(picked) >= n:
            break
        if is_indep(picked, v):
            picked.append(int(v))
    return picked

def main():
    print("building good-mask table...", flush=True)
    G = build_good()  # (255,255) bool
    print("done. mean good per direction:", G.sum(axis=1).mean(), flush=True)
    # perfect directions: good for all 255 masks
    perfect = np.flatnonzero(G.all(axis=1)) + 1
    print("perfect directions (good for all masks):", perfect.tolist(), flush=True)

    counts = G.sum(axis=1)
    order = np.argsort(-counts)
    # greedy 8 lin.indep. directions maximizing common intersection
    dirs = []
    common = np.ones(255, dtype=bool)
    for a1 in order:
        a = int(a1) + 1
        # check lin indep
        tmp = dirs + [a]
        # rank check
        rows = tmp[:]
        r = 0
        rr = list(rows)
        for c in range(8):
            piv = None
            for i in range(r, len(rr)):
                if (rr[i] >> c) & 1:
                    piv = i
                    break
            if piv is None:
                continue
            rr[r], rr[piv] = rr[piv], rr[r]
            for i in range(len(rr)):
                if i != r and ((rr[i] >> c) & 1):
                    rr[i] ^= rr[r]
            r += 1
        if r != len(tmp):
            continue
        new_common = common & G[a - 1]
        # accept if intersection still can yield 8 indep masks (need >=8 and rank 8)
        dirs.append(a)
        common = new_common
        if len(dirs) == 8:
            break
    print("chosen directions:", dirs, flush=True)
    print("common good masks:", int(common.sum()), flush=True)
    # find 8 lin.indep. masks in common, with pairwise sums also in common (for BIC)
    cand_masks = [int(m) + 1 for m in np.flatnonzero(common)]
    # prefer masks whose pairwise sums stay in common: greedy with constraint
    picked = []
    for m in cand_masks:
        if len(picked) == 8:
            break
        ok = True
        for p in picked:
            if not common[(p ^ m) - 1]:
                ok = False
                break
        if not ok:
            continue
        # lin indep check
        tmp = picked + [m]
        rr = list(tmp)
        r = 0
        for c in range(8):
            piv = None
            for i in range(r, len(rr)):
                if (rr[i] >> c) & 1:
                    piv = i
                    break
            if piv is None:
                continue
            rr[r], rr[piv] = rr[piv], rr[r]
            for i in range(len(rr)):
                if i != r and ((rr[i] >> c) & 1):
                    rr[i] ^= rr[r]
            r += 1
        if r == len(tmp):
            picked.append(m)
    print("picked masks:", picked, "(need 8)", flush=True)
    with open('good_table.pkl', 'wb') as f:
        pickle.dump({'dirs': dirs, 'masks': picked,
                     'common_count': int(common.sum())}, f)

if __name__ == '__main__':
    main()
