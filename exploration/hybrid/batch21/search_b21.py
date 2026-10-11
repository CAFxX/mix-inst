#!/usr/bin/env python3
"""Batch-21: Feistel-AND hybrid screen (track 5).

F2  = (ra&rb)^(rc&rd)^rk        (2-AND, NO linear term -- primary)
F3a = (ra&rb)^(rc&rd)^(re&rf)^rk (3-AND, no linear)
F1  = (ra&rb)^rk                 (1-AND diagnostic, expect weak-diffusion death)
FLIN= (ra&rb)^(rc&rd)^rotl(b,e)^rk (positive control, expect skeleton death)

Round: (L,R) -> (R, L^F(R)); rk_i = low32(rotl64(k,s_i)).
Pre: x=val^k split; Post: out=(L<<32|R)^rotl64(k,13).
Triage = EXACT S1 DIFF (diff_cell_logps, all 10 keys). KEEP bar max|z|<10.
Co-design: AND pairs sampled dense-biased (|a-b|<=9 fires on 18-bit S1 domain)
vs uniform; hit rates compared.
"""
import sys, json, time
import numpy as np
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration")
from lin_diff import diff_cell_logps
from screen_lib import KEYS, N
M64 = np.uint64(0xFFFFFFFFFFFFFFFF); M32 = np.uint32(0xFFFFFFFF)
KEYS10 = [int(k) for k in KEYS]
def rotl32(x, r):
    r %= 32
    return ((x << np.uint32(r)) | (x >> np.uint32(32 - r))) & M32 if r else x
def rotl64(x, r):
    r %= 64
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M64 if r else x

def feis_np(V, K, spec):
    form, nrounds, rounds, subrots = spec["form"], spec["nrounds"], spec["rounds"], spec["subrots"]
    x = np.asarray(V, dtype=np.uint64); k = np.asarray(K, dtype=np.uint64)
    x = (x ^ k) & M64
    L = (x >> np.uint64(32)).astype(np.uint32); R = (x & np.uint64(0xFFFFFFFF)).astype(np.uint32)
    for ri in range(nrounds):
        rk = (rotl64(k, subrots[ri]) & np.uint64(0xFFFFFFFF)).astype(np.uint32)
        rp = rounds[ri]
        if form == "F1":
            a, b = rp; F = (rotl32(R, a) & rotl32(R, b)) ^ rk
        elif form == "F2":
            a, b, c, d = rp; F = (rotl32(R, a) & rotl32(R, b)) ^ (rotl32(R, c) & rotl32(R, d)) ^ rk
        elif form == "F3a":
            a, b, c, d, e, f = rp; F = (rotl32(R, a) & rotl32(R, b)) ^ (rotl32(R, c) & rotl32(R, d)) ^ (rotl32(R, e) & rotl32(R, f)) ^ rk
        elif form == "FLIN":
            a, b, c, d, e = rp; F = (rotl32(R, a) & rotl32(R, b)) ^ (rotl32(R, c) & rotl32(R, d)) ^ rotl32(R, e) ^ rk
        L, R = R, ((L ^ F) & M32)
    out = ((L.astype(np.uint64) << np.uint64(32)) | R.astype(np.uint64)) & M64
    return ((out ^ rotl64(k, 13)) & M64).astype(np.uint64)

def eval_spec(spec):
    V = np.arange(N, dtype=np.uint64)
    worst, wkey = 0.0, None
    for key in KEYS10:
        K = np.full(N, np.uint64(key), dtype=np.uint64)
        S = feis_np(V, K, spec)
        _, wz, _, _ = diff_cell_logps(S, key)
        if wz > worst: worst, wkey = wz, key
    return worst, wkey

def sample_pair(rng, dense):
    while True:
        if dense and rng.random() < 0.7:
            a = int(rng.integers(1, 32)); b = a + int(rng.integers(1, 10)) * (1 if rng.random()<0.5 else -1)
            b = ((b - 1) % 31) + 1
            if a == b: continue
        else:
            a = int(rng.integers(1, 32)); b = int(rng.integers(1, 32))
            if a == b: continue
        return (a, b)

def sample_spec(rng, form, nrounds):
    rounds, subrots = [], []
    for _ in range(nrounds):
        if form == "F1": rp = sample_pair(rng, True)
        elif form == "F2": rp = sample_pair(rng, True) + sample_pair(rng, True)
        elif form == "F3a": rp = sample_pair(rng, True) + sample_pair(rng, True) + sample_pair(rng, True)
        elif form == "FLIN": rp = sample_pair(rng, True) + sample_pair(rng, True) + (int(rng.integers(0, 32)),)
        rounds.append(rp); subrots.append(int(rng.integers(0, 64)))
    return {"form": form, "nrounds": nrounds, "rounds": rounds, "subrots": subrots}

def main():
    seed = int(sys.argv[1], 0) if len(sys.argv) > 1 else 0xB21
    rng = np.random.default_rng(seed)
    plan = [("F2", 3, 40), ("F2", 4, 40), ("F3a", 3, 30), ("F1", 4, 20), ("FLIN", 4, 10)]
    results = []
    t0 = time.time()
    for form, nr, n in plan:
        for t in range(n):
            spec = sample_spec(rng, form, nr)
            wz, wkey = eval_spec(spec)
            keep = wz < 10
            print("try %-4s R%d %3d maxworst|z|=%12.1f killkey=%#x %s" % (form, nr, t, wz, wkey if wkey is not None else 0, "KEEP" if keep else "kill"), flush=True)
            results.append({"form": form, "nrounds": nr, "z": float(wz), "killkey": wkey, "keep": bool(keep),
                            "rounds": spec["rounds"], "subrots": spec["subrots"]})
    keeps = [r for r in results if r["keep"]]
    print("=== %d/%d KEEP (%.1fs) ===" % (len(keeps), len(results), time.time()-t0), flush=True)
    for r in sorted(keeps, key=lambda r: r["z"]):
        print("KEEP %-4s R%d z=%.2f %s subrots=%s" % (r["form"], r["nrounds"], r["z"], r["rounds"], r["subrots"]), flush=True)
    # hit-rate by form
    for form, nr, n in plan:
        sub = [r for r in results if r["form"] == form and r["nrounds"] == nr]
        hk = sum(1 for r in sub if r["keep"])
        zs = sorted(r["z"] for r in sub)
        print("SUMMARY %-4s R%d: %d/%d keep, min z=%.1f, median z=%.1f" % (form, nr, hk, len(sub), zs[0], zs[len(zs)//2]), flush=True)
    json.dump(results, open("search_b21_results.json", "w"))

if __name__ == "__main__":
    main()
