#!/usr/bin/env python3
"""Co-design screener: chi/AND-cascade + P-box diffusion analysis.

For hybrid batch 5: co-design a P-box FOR a chi/AND rotation schedule
(or vice versa). Models bit-dependency spread through cascaded stages.

Stage (chi):  x ^= ((~rotl(x,a)) & rotl(x,b)) ^ rotl(x,c)
Stage (and):  x ^= (rotl(x,a) & rotl(x,b)) ^ rotl(x,c)
Optional P-box P between stages: y[i] = stage_out[P^{-1}(i)].

Dependency: out bit i depends on input bits D(i).
  chi/AND stage: D(i) = {i, i-a, i-b, i-c} (mod 64).
  P-box:         D(i) = D_stage(P^{-1}(i)).

Metric (per stage count N, bigger=better):
  min_dep(N)  = min over i of |D_N(i)|          -- worst-case spread
  max_gap(N)  = max over i of largest run of input bits NOT in D_N(i)
  score       = min_dep(3) - max_gap(3)          -- 3-stage co-diffusion

Co-design use: sweep P-boxes for a fixed rotation schedule (or sweep
schedules for a fixed P-box); rank by score; S0+S1+S2 decide.
"""
import sys

N = 64

def rot_deps(a, b, c):
    """Dependency offsets for one chi/AND stage (output bit i <- input bits)."""
    return (0, (-a) % N, (-b) % N, (-c) % N)

def compose(dep_sets, pbox_inv):
    """Apply P-box: new_dep[i] = union of dep_sets[j] for j in preimage.
    For a permutation P, preimage of i is single: P^{-1}(i)."""
    return [set(dep_sets[pbox_inv[i]]) for i in range(N)]

def stage_deps(dep_sets, offs):
    """Apply chi/AND stage: new_dep[i] = union of dep_sets[(i-o)%N] for o in offs."""
    out = []
    for i in range(N):
        s = set()
        for o in offs:
            s |= dep_sets[(i - o) % N]
        out.append(s)
    return out

def max_gap(dep):
    """Largest run of consecutive input bits not in dep (circular)."""
    missing = [b for b in range(N) if b not in dep]
    if not missing:
        return 0
    # longest circular run in `missing`
    s = set(missing)
    best = 0
    for b in missing:
        if (b - 1) % N not in s:  # run start
            run = 0
            cur = b
            while cur in s:
                run += 1
                cur = (cur + 1) % N
            best = max(best, run)
    return best

def analyze(offs_list, pbox=None, stages=None):
    """offs_list: list of (a,b,c) per stage; pbox: perm list or None (identity between stages).
    stages: how many stage-groups to evaluate (default len(offs_list))."""
    stages = stages or len(offs_list)
    pbox_inv = [0] * N
    if pbox:
        for i, d in enumerate(pbox):
            pbox_inv[d] = i
    else:
        pbox_inv = list(range(N))
    dep = [set([i]) for i in range(N)]
    results = []
    for s in range(stages):
        offs = rot_deps(*offs_list[s % len(offs_list)])
        dep = stage_deps(dep, offs)
        if s < stages - 1:  # P-box between stages, not after last
            dep = compose(dep, pbox_inv)
        min_dep = min(len(d) for d in dep)
        mg = max(max_gap(d) for d in dep)
        results.append((min_dep, mg))
    return results

def affine_pbox(a, b):
    return [(a * i + b) % N for i in range(N)]

def score_for(offs_list, pbox):
    r = analyze(offs_list, pbox, stages=3)
    min_dep, mg = r[-1]
    return min_dep - mg, r

if __name__ == "__main__":
    # Baseline: al_cascad-style AND cascade, no P-box (identity)
    # Use al_cascad's actual rotation schedule if known; else representative
    casc = [(1, 2, 13), (7, 19, 5), (3, 11, 29)]
    s0, r0 = score_for(casc, None)
    print(f"no-P-box baseline: score={s0} stages={r0}")

    # Sweep affine P-boxes for the same schedule
    scored = []
    for a in [3, 5, 11, 13, 17, 19, 21, 27, 29, 35, 43, 53, 61]:
        for b in [1, 3, 5, 7]:
            pb = affine_pbox(a, b)
            s, r = score_for(casc, pb)
            scored.append((s, a, b, r))
    scored.sort(reverse=True)
    print("\nTop 10 P-boxes for AND-cascade schedule:")
    for s, a, b, r in scored[:10]:
        print(f"  P=({a:2d},{b}) score={s:3d} stages={r}")
    print("\nBottom 3:")
    for s, a, b, r in scored[-3:]:
        print(f"  P=({a:2d},{b}) score={s:3d} stages={r}")
