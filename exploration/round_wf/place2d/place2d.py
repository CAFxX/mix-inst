#!/usr/bin/env python3
"""2D placement-aware P-box evaluation (round_wf, corrected objective 2026-10-04).

CORRECTION vs the 1D phase: index-space locality (short hops in bit-index,
what S2 kills) and physical locality (wirelength after 2D placement, what the
placer sees) are SEPARATE metrics. This module computes the second:
for a candidate P-box, build the lane-communication graph (16 S-box lanes as
nodes, 64 directed bit-wires as weighted edges) and estimate placeable
wirelength by simulated annealing over 4x4 grid assignments of lanes,
Manhattan objective. Diffusion is NOT optimized here -- it is measured by
the real S2 screen on placeability-ranked finalists.

Geometry model (stated assumptions):
  - 16 lanes on a 4x4 grid; each grid cell holds one lane's S-box+L cloud.
  - Horizontal grid step = 4 bit-pitches (lane is 4 bits wide).
  - Vertical grid step   = V_PITCH bit-pitches (default 4: square lane slots).
  - Wire a->b cost = w[a][b] * (4*|dx| + V_PITCH*|dy|), summed over all edges.
  - One shared placement for all 4 rounds (identical P-box each round).
"""
import json, math, os, random

N = 64
NLANE = 16
V_PITCH = 4          # vertical lane pitch in bit-pitches (sensitivity: 2, 8)
GRID = 4             # 4x4 lane grid

HERE = os.path.dirname(os.path.abspath(__file__))

# ------------------------------------------------------------ P-box pool
def baseline_P():
    return [(5 * i + 27) % 64 for i in range(N)]

def _o34_ok(P):
    """O34 validity: permutation, single 64-cycle, no fixed points,
    Dmin=4 both directions (per-nibble spread)."""
    if sorted(P) != list(range(N)):
        return False
    if any(P[i] == i for i in range(N)):
        return False
    seen = [False] * N
    ncy = 0
    for i in range(N):
        if not seen[i]:
            ncy += 1
            j = i
            while not seen[j]:
                seen[j] = True
                j = P[j]
    if ncy != 1:
        return False
    for L in range(NLANE):
        if len({P[4 * L + k] // 4 for k in range(4)}) != 4:
            return False
    # inverse direction
    Q = [0] * N
    for i, d in enumerate(P):
        Q[d] = i
    for L in range(NLANE):
        if len({Q[4 * L + k] // 4 for k in range(4)}) != 4:
            return False
    return True

def affine_pool():
    """O37-style validated pool: P(i)=(a*i+b)%64, a odd, O34 criteria."""
    pool = []
    for a in range(1, 64, 2):
        for b in range(64):
            P = [(a * i + b) % 64 for i in range(N)]
            if _o34_ok(P):
                S = sum(abs(P[i] // 4 - i // 4) for i in range(N))
                pool.append({"name": f"aff_a{a:02d}_b{b:02d}", "P": P,
                             "S": S, "src": "affine"})
    return pool

def sa_highS_pool(frontier_path, s_min=320):
    """Diffusion-optimized SA tours (Dreq=4, high S) from the old grid."""
    fr = json.load(open(frontier_path))
    pool = []
    for idx, t in fr["tours"].items():
        r = fr["results"][int(idx)]
        if r["Dreq"] != 4 or r["S"] < s_min:
            continue
        c = t
        P = [0] * N
        for k in range(N):
            P[c[k]] = c[(k + 1) % N]
        if not _o34_ok(P):
            continue
        pool.append({"name": f"sa_S{r['S']}_s{r['seed']}_l{r['lam']}",
                     "P": P, "S": r["S"], "src": "sa_highS"})
    # dedupe by P tuple
    seen, out = set(), []
    for e in pool:
        tp = tuple(e["P"])
        if tp not in seen:
            seen.add(tp)
            out.append(e)
    return out

# ------------------------------------------------------------ lane graph
def lane_graph(P):
    """16x16 directed weight matrix: w[a][b] = # bits i with lane(i)=a,
    lane(P(i))=b. Row sums = 4 (each lane emits 4 bits)."""
    w = [[0] * NLANE for _ in range(NLANE)]
    for i in range(N):
        w[i // 4][P[i] // 4] += 1
    return w

# ------------------------------------------------------------ 2D placement SA
def grid_xy(cell):
    return (cell % GRID, cell // GRID)

def place_cost(assign, w, v_pitch=V_PITCH):
    """assign[lane] = grid cell. Manhattan wirelength in bit-pitches."""
    xy = [grid_xy(assign[L]) for L in range(NLANE)]
    tot = 0
    for a in range(NLANE):
        xa, ya = xy[a]
        row = w[a]
        for b in range(NLANE):
            qab = row[b]
            if qab:
                xb, yb = xy[b]
                tot += qab * (4 * abs(xa - xb) + v_pitch * abs(ya - yb))
    return tot

def place_sa(w, seed=1, iters=40000, t0=40.0, t1=0.02, v_pitch=V_PITCH):
    """SA over lane->cell assignments (swap moves), O(deg) incremental delta.
    Returns (best_cost, assign). w: 16x16 directed weights (Dmin=4 pool:
    exactly 4 out-neighbors per lane)."""
    rng = random.Random(seed)
    # adjacency lists
    out_nbrs = [[b for b in range(NLANE) if w[a][b]] for a in range(NLANE)]
    in_nbrs = [[a for a in range(NLANE) if w[a][b]] for b in range(NLANE)]
    assign = list(range(NLANE))
    rng.shuffle(assign)
    # cell_of[lane], lane_at[cell]
    cell_of = assign
    xy = [grid_xy(cell_of[L]) for L in range(NLANE)]

    def edist(ca, cb):
        xa, ya = grid_xy(ca)
        xb, yb = grid_xy(cb)
        return 4 * abs(xa - xb) + v_pitch * abs(ya - yb)

    def full_cost():
        s = 0
        for a in range(NLANE):
            ca = cell_of[a]
            for b in out_nbrs[a]:
                s += w[a][b] * edist(ca, cell_of[b])
        return s

    cur = full_cost()
    best = (cur, list(cell_of))
    for it in range(iters):
        T = t0 * (t1 / t0) ** (it / iters)
        x, y = rng.randrange(NLANE), rng.randrange(NLANE)
        if x == y:
            continue
        cx, cy = cell_of[x], cell_of[y]
        # delta over edges incident to x or y (as source or target)
        d = 0
        # out-edges of x and y
        for a, ca, cb_new, cb_old in ((x, cx, cy, cx), (y, cy, cx, cy)):
            for b in out_nbrs[a]:
                if b == x or b == y:
                    continue
                qab = w[a][b]
                d += qab * (edist(cb_new, cell_of[b]) - edist(cb_old, cell_of[b]))
        # in-edges of x and y (from a not in {x,y}; x<->y edges handled below)
        for b, cb_old, cb_new in ((x, cx, cy), (y, cy, cx)):
            for a in in_nbrs[b]:
                if a == x or a == y:
                    continue
                qab = w[a][b]
                d += qab * (edist(cell_of[a], cb_new) - edist(cell_of[a], cb_old))
        # edges among {x,y}: (x,y),(y,x),(x,x),(y,y)
        for a, b in ((x, y), (y, x), (x, x), (y, y)):
            qab = w[a][b]
            if qab:
                ca_old = cx if a == x else cy
                cb_old = cx if b == x else cy
                ca_new = cy if a == x else cx
                cb_new = cy if b == x else cx
                d += qab * (edist(ca_new, cb_new) - edist(ca_old, cb_old))
        if d <= 0 or rng.random() < math.exp(-d / T):
            cell_of[x], cell_of[y] = cy, cx
            cur += d
            if cur < best[0]:
                best = (cur, list(cell_of))
    return best

def placeability(P, seeds=(1, 2), iters=8000, v_pitch=V_PITCH):
    """Min estimated 2D wirelength (bit-pitches) over SA restarts.
    Screening params: 8k iters x 2 seeds converges to the optimum on the
    baseline (424, verified vs 40k x 4). Use refine() for finalists."""
    w = lane_graph(P)
    best = min(place_sa(w, seed=s, iters=iters, v_pitch=v_pitch)[0]
               for s in seeds)
    return best

def refine(P, seeds=(1, 2, 3, 4), iters=40000, v_pitch=V_PITCH):
    """High-effort placeability for finalists. Returns (best_cost, assign)."""
    w = lane_graph(P)
    best_c, best_a = None, None
    for s in seeds:
        c, a = place_sa(w, seed=s, iters=iters, v_pitch=v_pitch)
        if best_c is None or c < best_c:
            best_c, best_a = c, a
    return best_c, best_a

# ------------------------------------------------------------ S2 metrics (index space)
def index_metrics(P):
    S = sum(abs(P[i] // 4 - i // 4) for i in range(N))
    W1d = sum(abs(P[i] - i) for i in range(N))
    return {"S": S, "W1d": W1d}
