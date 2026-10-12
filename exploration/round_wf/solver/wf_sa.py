#!/usr/bin/env python3
"""Wire-friendly P-box search for the r22c SPN family (round_wf, Phase B).

Constrained assignment on n=64:
  minimize  W = sum |P(i) - i|            (wirelength proxy, bit-pitches)
  maximize  S = sum |lane(P(i)) - lane(i)| (spreading, lane units; lane = i//4)
subject to:
  (1) P is a single 64-cycle   -- by construction (tour representation)
  (2) no fixed points          -- by construction (tour has distinct entries)
  (3) D_min = 4: each source lane's 4 bits land in 4 DISTINCT target lanes
      (maximal per-S-box spreading, preserved from the current P-box)

Tour representation: c = permutation of 0..63, P(c[k]) = c[(k+1) % 64].
Every single 64-cycle has such a representation; every tour gives one.
Swap moves on c preserve (1) and (2) exactly. (3) enforced by rejection.

Simulated annealing with incremental delta evaluation (O(1) per move).
Multi-lambda sweep maps the (W, S) Pareto frontier; D_min in {2,3,4} maps
the cost of the maximal-spreading requirement.
"""
import json, math, os, random, sys, time

N = 64
NLANE = 16
OUT = os.path.dirname(os.path.abspath(__file__)) + "/../pareto"

# ---------------------------------------------------------------- metrics
def full_metrics(c):
    """c: tour list. Returns dict with P, W, S, Dmin, maxstretch, cycles."""
    P = [0] * N
    for k in range(N):
        P[c[k]] = c[(k + 1) % N]
    W = sum(abs(P[i] - i) for i in range(N))
    S = sum(abs(P[i] // 4 - i // 4) for i in range(N))
    Dmin = N
    for L in range(NLANE):
        tgt = {P[4 * L + k] // 4 for k in range(4)}
        Dmin = min(Dmin, len(tgt))
    maxstretch = max(abs(P[i] - i) for i in range(N))
    # cycle check
    seen = [False] * N
    cyc = 0
    for i in range(N):
        if not seen[i]:
            cyc += 1
            j = i
            while not seen[j]:
                seen[j] = True
                j = P[j]
    fixed = sum(1 for i in range(N) if P[i] == i)
    return {"P": P, "W": W, "S": S, "Dmin": Dmin,
            "maxstretch": maxstretch, "cycles": cyc, "fixed": fixed}

def ref_metrics(name, P):
    W = sum(abs(P[i] - i) for i in range(N))
    S = sum(abs(P[i] // 4 - i // 4) for i in range(N))
    Dmin = min(len({P[4 * L + k] // 4 for k in range(4)}) for L in range(NLANE))
    maxstretch = max(abs(P[i] - i) for i in range(N))
    seen = [False] * N; cyc = 0
    for i in range(N):
        if not seen[i]:
            cyc += 1; j = i
            while not seen[j]:
                seen[j] = True; j = P[j]
    fixed = sum(1 for i in range(N) if P[i] == i)
    return {"name": name, "W": W, "S": S, "Dmin": Dmin,
            "maxstretch": maxstretch, "cycles": cyc, "fixed": fixed}

# ------------------------------------------------- incremental SA state
class SAState:
    def __init__(self, c):
        self.c = list(c)
        self.pos = [0] * N          # pos[v] = index k with c[k] == v
        for k, v in enumerate(self.c):
            self.pos[v] = k
        # P image of domain d: P[d] = c[(pos[d]+1) % N]
        self.W = 0
        self.S = 0
        # lane target counts: cnt[L][T]
        self.cnt = [[0] * NLANE for _ in range(NLANE)]
        self.distinct = [0] * NLANE
        for d in range(N):
            img = self.c[(self.pos[d] + 1) % N]
            self.W += abs(img - d)
            self.S += abs(img // 4 - d // 4)
            L, T = d // 4, img // 4
            if self.cnt[L][T] == 0:
                self.distinct[L] += 1
            self.cnt[L][T] += 1
        self.Dmin = min(self.distinct)

    def _img(self, d):
        return self.c[(self.pos[d] + 1) % N]

    def try_swap(self, a, b):
        """Swap tour positions a,b. Returns (dW, dS, new_Dmin) for the
        resulting state (exact); does not mutate. Caller enforces Dreq."""
        if a == b:
            return 0, 0, self.Dmin
        c, pos = self.c, self.pos
        x, y = c[a], c[b]
        # domain points whose image may change: first elements of the
        # tour-pairs touching swapped positions
        doms = {c[(a - 1) % N], x, c[(b - 1) % N], y}
        def img_after(d):
            k = pos[d]
            kk = b if k == a else (a if k == b else k)
            nk = (kk + 1) % N
            return y if nk == a else (x if nk == b else c[nk])
        dW = dS = 0
        lane_delta = {}  # (L,T) -> net count delta
        for d in doms:
            old = self._img(d)
            new = img_after(d)
            if old == new:
                continue
            dW += abs(new - d) - abs(old - d)
            dS += abs(new // 4 - d // 4) - abs(old // 4 - d // 4)
            L = d // 4
            key = (L, old // 4)
            lane_delta[key] = lane_delta.get(key, 0) - 1
            key = (L, new // 4)
            lane_delta[key] = lane_delta.get(key, 0) + 1
        # exact new distinct-count per affected lane (grouped simulation)
        per_lane = {}
        for (L, T), dl in lane_delta.items():
            per_lane.setdefault(L, []).append((T, dl))
        new_distinct = {}
        for L, changes in per_lane.items():
            nd = self.distinct[L]
            for T, dl in changes:
                before = self.cnt[L][T]
                after = before + dl
                assert after >= 0, "count went negative"
                if before == 0 and after > 0:
                    nd += 1
                elif before > 0 and after == 0:
                    nd -= 1
            new_distinct[L] = nd
        others = [self.distinct[L] for L in range(NLANE) if L not in new_distinct]
        new_Dmin = min(others + list(new_distinct.values()))
        return dW, dS, new_Dmin

    def do_swap(self, a, b, dW, dS):
        c, pos = self.c, self.pos
        x, y = c[a], c[b]
        doms = {c[(a - 1) % N], x, c[(b - 1) % N], y}
        def img_after(d):
            k = pos[d]
            kk = b if k == a else (a if k == b else k)
            nk = (kk + 1) % N
            return y if nk == a else (x if nk == b else c[nk])
        for d in doms:
            old = self._img(d)
            new = img_after(d)
            if old == new:
                continue
            L = d // 4
            ot, nt = old // 4, new // 4
            self.cnt[L][ot] -= 1
            if self.cnt[L][ot] == 0:
                self.distinct[L] -= 1
            if self.cnt[L][nt] == 0:
                self.distinct[L] += 1
            self.cnt[L][nt] += 1
        c[a], c[b] = y, x
        pos[x], pos[y] = b, a
        self.W += dW
        self.S += dS
        self.Dmin = min(self.distinct)

def anneal(seed, lam, Dreq, iters, t0=6.0, t1=0.005, log=False):
    rng = random.Random(seed)
    c = list(range(N))
    rng.shuffle(c)
    st = SAState(c)
    # greedy repair: hill-climb Dmin until feasible (random tour rarely is)
    for _ in range(100000):
        if st.Dmin >= Dreq:
            break
        a, b = rng.randrange(N), rng.randrange(N)
        dW, dS, new_Dmin = st.try_swap(a, b)
        if new_Dmin >= st.Dmin and rng.random() < 0.7:
            st.do_swap(a, b, dW, dS)
    assert st.Dmin >= Dreq, f"repair failed: Dmin={st.Dmin}"
    best = (st.W, st.S, list(st.c))
    cur_f = st.W - lam * st.S
    for it in range(iters):
        T = t0 * (t1 / t0) ** (it / iters)
        a, b = rng.randrange(N), rng.randrange(N)
        dW, dS, new_Dmin = st.try_swap(a, b)
        if new_Dmin < Dreq:
            continue
        df = dW - lam * dS
        if df <= 0 or rng.random() < math.exp(-df / T):
            st.do_swap(a, b, dW, dS)
            cur_f += df
            if st.W < best[0] or (st.W == best[0] and st.S > best[1]):
                best = (st.W, st.S, list(st.c))
    if log:
        print(f"  lam={lam} Dreq={Dreq} seed={seed}: W={best[0]} S={best[1]}", flush=True)
    return best

def main():
    os.makedirs(OUT, exist_ok=True)
    t_start = time.time()
    # ---- baseline + references
    P_base = [(5 * i + 27) % 64 for i in range(N)]
    base = ref_metrics("r22c_current_P(5i+27)%64", P_base)
    P_present = [(16 * i) % 63 if i < 63 else 63 for i in range(N)]
    present = ref_metrics("PRESENT_pLayer", P_present)
    P_gift = [0,17,34,51,48,1,18,35,32,49,2,19,16,33,50,3,
              4,21,38,55,52,5,22,39,36,53,6,23,20,37,54,7,
              8,25,42,59,56,9,26,43,40,57,10,27,24,41,58,11,
              12,29,46,63,60,13,30,47,44,61,14,31,28,45,62,15]
    gift = ref_metrics("GIFT_PermBits", P_gift)
    refs = [base, present, gift]
    print("Baseline:", {k: base[k] for k in ("W", "S", "Dmin", "maxstretch", "cycles", "fixed")}, flush=True)
    assert base["W"] == 1450, f"baseline W={base['W']} != 1450 (parent figure)"
    assert base["cycles"] == 1 and base["fixed"] == 0 and base["Dmin"] == 4
    # ---- SA sweeps
    results = []
    lam_grid = [0, 1, 2, 4, 8, 16, 32]
    seeds = [11, 22, 33]
    iters = 120000
    for Dreq in (4, 3, 2):
        for lam in lam_grid:
            for s in seeds:
                W, S, c = anneal(s * 1000 + lam, lam, Dreq, iters)
                m = full_metrics(c)
                assert m["cycles"] == 1 and m["fixed"] == 0, "construction violated"
                assert m["Dmin"] >= Dreq
                results.append({"lam": lam, "Dreq": Dreq, "seed": s,
                                "W": W, "S": S, "Dmin": m["Dmin"],
                                "maxstretch": m["maxstretch"], "tour": c})
    # ---- Pareto extraction per Dreq: nondominated in (W min, S max)
    pareto = {}
    for Dreq in (4, 3, 2):
        pts = [(r["W"], r["S"], i) for i, r in enumerate(results) if r["Dreq"] == Dreq]
        nd = []
        for w, s_, i in pts:
            if not any(w2 <= w and s2 >= s_ and (w2 < w or s2 > s_) for w2, s2, _ in pts):
                nd.append(i)
        pareto[str(Dreq)] = sorted(nd)
    out = {"refs": refs, "results": [{k: r[k] for k in ("lam", "Dreq", "seed", "W", "S", "Dmin", "maxstretch")} for r in results],
           "pareto_idx": pareto,
           "tours": {str(i): results[i]["tour"] for i in sum(pareto.values(), [])},
           "elapsed_s": round(time.time() - t_start, 1)}
    with open(OUT + "/frontier.json", "w") as f:
        json.dump(out, f)
    print(f"done in {out['elapsed_s']}s; pareto sizes:", {k: len(v) for k, v in pareto.items()}, flush=True)

if __name__ == "__main__":
    main()
