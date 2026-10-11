#!/usr/bin/env python3
"""Q1: SAC/BIC avalanche spot check (round 13).
Usage: q1_sacbic.py <candidate> <outdir>

Method (matches the 2026-10-02 quality battery):
  N = 2^18, fixed key 0x123456789ABCDEF0.
  For each input bit i in 0..63: V = N random uint64; D = mix(V)^mix(V^2^i).
  p[i][j] = fraction of trials where output bit j flipped.
  SAC: z = (p-0.5)/sqrt(0.25/N); sac_z5 = #{|z|>5} of 4096 cells;
       sac_maxdev = max|p-0.5|, sac_meandev = mean|p-0.5|.
  BIC: per input bit, column correlation matrix of the N x 64 avalanche
       indicator matrix; bic_maxcorr = max |off-diagonal| over all input bits;
       bic_meancorr = mean |off-diagonal| over all input bits.
  avalanche_mean = mean Hamming weight of D over all trials.
Writes q1_<candidate>.json into outdir.
"""
import importlib.util
import json
import os
import sys
import time

import numpy as np

FB = "/home/hatch/workspace/mix/exploration/fast_battery"
N = 1 << 18
KEY = np.uint64(0x123456789ABCDEF0)


def load(cand):
    spec = importlib.util.spec_from_file_location(
        "model_" + cand, f"{FB}/candidates/{cand}/model.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m.mix_np


def main():
    cand, outdir = sys.argv[1], sys.argv[2]
    os.makedirs(outdir, exist_ok=True)
    mix_np = load(cand)
    rng = np.random.default_rng(0x51AC)
    t0 = time.time()

    p = np.zeros((64, 64))
    maxcorr = 0.0
    sumcorr = 0.0
    tot_w = 0
    tot_n = 0
    for i in range(64):
        V = rng.integers(0, 2**64, size=N, dtype=np.uint64)
        Vf = V ^ np.uint64(1 << i)
        K = np.full(N, KEY, dtype=np.uint64)
        D = np.bitwise_xor(mix_np(V, K).astype(np.uint64),
                           mix_np(Vf, K).astype(np.uint64))
        bits = ((D[:, None] >> np.arange(64, dtype=np.uint64)) & np.uint64(1))
        bits = bits.astype(np.float64)
        p[i] = bits.mean(axis=0)
        # BIC: correlation of the 64 avalanche columns
        c = np.corrcoef(bits, rowvar=False)
        np.fill_diagonal(c, 0.0)
        ac = np.abs(c)
        maxcorr = max(maxcorr, ac.max())
        sumcorr += ac.sum()
        tot_w += bits.sum()
        tot_n += bits.size
        if i % 16 == 15:
            print(f"  bit {i+1}/64 done ({time.time()-t0:.0f}s)", flush=True)

    dev = np.abs(p - 0.5)
    z = (p - 0.5) / np.sqrt(0.25 / N)
    out = {
        "candidate": cand,
        "key": hex(int(KEY)),
        "N": N,
        "sac_maxdev": float(dev.max()),
        "sac_meandev": float(dev.mean()),
        "sac_z5": int((np.abs(z) > 5).sum()),
        "bic_maxcorr": float(maxcorr),
        "bic_meancorr": float(sumcorr / (64 * 64 * 63)),
        "avalanche_mean": float(tot_w / (tot_n / 64)),
        "wall_s": round(time.time() - t0, 1),
    }
    with open(os.path.join(outdir, f"q1_{cand}.json"), "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
