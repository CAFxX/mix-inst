"""Differential trail search for r7_feist8_s1_1sbox.
G(R) = lin32(sboxlayer(R))  (round-key-independent part of F; rk cancels in differentials)
Feistel round on differences: (dL,dR) -> (dR, dL ^ Gdiff(dR))
"""
import math, pickle, os
from itertools import combinations

S1 = [0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10]

# --- DDT transitions per nibble: a -> [(e, prob)] sorted desc ---
DDT = [[0]*16 for _ in range(16)]
for x in range(16):
    for a in range(16):
        DDT[a][S1[x] ^ S1[x ^ a]] += 1
TRANS = {}
for a in range(16):
    t = [(e, DDT[a][e]/16) for e in range(16) if DDT[a][e] > 0]
    t.sort(key=lambda z: -z[1])
    TRANS[a] = t
print("avg transitions per nonzero row:", sum(len(TRANS[a]) for a in range(1,16))/15)

def lin32(x):
    x &= 0xFFFFFFFF
    return (x ^ (((x << 7) | (x >> 25)) & 0xFFFFFFFF) ^ (((x << 13) | (x >> 19)) & 0xFFFFFFFF)) & 0xFFFFFFFF

def nibwt64(x):
    w = 0
    for i in range(16):
        if (x >> (4*i)) & 0xF: w += 1
    return w

def active32(x):
    return [i for i in range(8) if (x >> (4*i)) & 0xF]

# per-round: given dR (32-bit), yield (f_out_diff, logprob, active_sboxes, e)
def round_transitions(dR, topk=6):
    act = active32(dR)
    if not act:
        yield (0, 0.0, 0, 0)
        return
    lists = []
    for i in act:
        a = (dR >> (4*i)) & 0xF
        lists.append([(i, e, math.log(p)) for (e, p) in TRANS[a][:topk]])
    # product
    def rec(idx, e_val, lp, nact):
        if idx == len(lists):
            yield (lin32(e_val), lp, nact, e_val)
            return
        for (i, e, l) in lists[idx]:
            yield from rec(idx+1, e_val | (e << (4*i)), lp + l, nact + 1)
    yield from rec(0, 0, 0.0, 0)

def beam_search(nrounds=8, init_max_wt=2, beam=4000, topk=6, rkdiff_lo=None, init_states=None,
               keep_history=False):
    """rkdiff_lo: list of 8 round-key low32 diffs (related-key mode) or None."""
    states = {}  # (dL,dR) -> [logprob, prev, einfo, nact]
    if init_states is None:
        init_states = []
        for w in range(1, init_max_wt+1):
            for pos in combinations(range(16), w):
                # iterate values; for w=2 this is 120*225=27k, ok
                def rec(idx, val):
                    if idx == w:
                        init_states.append(val); return
                    for v in range(1, 16):
                        rec(idx+1, val | (v << (4*pos[idx])))
                rec(0, 0)
    for s in init_states:
        dL = (s >> 32) & 0xFFFFFFFF; dR = s & 0xFFFFFFFF
        states[(dL, dR)] = [0.0, None, None, 0]
    history = [states]
    for r in range(nrounds):
        rk = (rkdiff_lo[r] & 0xFFFFFFFF) if rkdiff_lo else 0
        new = {}
        for (dL, dR), (lp, prev, ei, nact) in states.items():
            wt = nibwt64(dR)
            tk = topk if wt <= 3 else 2
            for (f, llp, na, e) in round_transitions(dR, topk=tk):
                f ^= rk
                ns = (dR, (dL ^ f) & 0xFFFFFFFF)
                nlp = lp + llp
                if ns not in new or new[ns][0] < nlp:
                    new[ns] = [nlp, (dL, dR), (r, e, f), nact + na]
        # prune to beam
        if len(new) > beam:
            items = sorted(new.items(), key=lambda z: -z[1][0])[:beam]
            new = dict(items)
        states = new
        if keep_history:
            history.append(states)
    if keep_history:
        return states, history
    return states

def recover_trail(history, final):
    """history: list of state dicts per round (0..nrounds); final: state key at last round."""
    trail = [final]
    cur = final
    for r in range(len(history)-1, 0, -1):
        lp, prev, ei, nact = history[r][cur]
        cur = prev
        trail.append(cur)
    trail.reverse()
    return trail  # state keys from round 0 (input diff) to round nrounds (output diff)

def backtrack(states, final):
    trail = []
    cur = final
    while cur is not None:
        lp, prev, ei, nact = states[cur]
        trail.append((cur, lp, ei, nact))
        # need parent's record: we stored prev state key; look up in previous round states — not kept.
        cur = None
    return trail

if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "single"
    if mode == "single":
        print("== single-key best 8-round differential trail ==")
        states = beam_search()
        best = max(states.items(), key=lambda z: z[1][0])
        (dL, dR), (lp, prev, ei, nact) = best
        print(f"best trail: P = 2^{lp/math.log(2):.2f}, active S-boxes = {nact}, out diff = (0x{dL:08x}, 0x{dR:08x})")
        with open("trail_single.pkl", "wb") as fh:
            pickle.dump({"best": ((dL, dR), lp, nact), "nstates": len(states)}, fh)
        # best zero-output trail
        zc = [(s, v) for s, v in states.items() if s == (0, 0)]
        if zc:
            (dL, dR), (lp, prev, ei, nact) = zc[0]
            print(f"best ZERO-output trail: P = 2^{lp/math.log(2):.2f}, active = {nact}")
        else:
            print("no zero-output trail survived the beam (prob below beam cutoff)")
        # distribution: how many states within 2^-64?
        cnt = sum(1 for v in states.values() if v[0] >= -64*math.log(2))
        print(f"states with P >= 2^-64: {cnt}/{len(states)}")
    elif mode == "related":
        print("== related-key trails, single-bit key differences ==")
        res = {}
        for bit in [0, 13, 31, 32, 63]:
            delta = 1 << bit
            rkdiff = []
            for i in range(8):
                rot = (13*(i+1)) % 64
                rkdiff.append((((delta << rot) | (delta >> ((64-rot) % 64))) & 0xFFFFFFFFFFFFFFFF) & 0xFFFFFFFF)
            # initial state after whitening cancels: (0,0)
            states = beam_search(init_states=[0], rkdiff_lo=rkdiff, beam=2000)
            best = max(states.items(), key=lambda z: z[1][0])
            (dL, dR), (lp, prev, ei, nact) = best
            print(f"  delta=bit{bit}: best P = 2^{lp/math.log(2):.2f}, active={nact}, out=(0x{dL:08x},0x{dR:08x})")
            zc = [(s, v) for s, v in states.items() if s == (0, 0)]
            if zc:
                (lp2, nact2) = zc[0][1][0], zc[0][1][3]
                print(f"    zero-output related-key trail: P = 2^{lp2/math.log(2):.2f}, active={nact2}")
            res[bit] = lp / math.log(2)
        with open("trail_related.pkl", "wb") as fh:
            pickle.dump(res, fh)
