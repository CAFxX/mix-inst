"""Screen 2-stage MUXD candidates with Fisher triage. Target: <10u, pass Fisher."""
import sys, numpy as np, random
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/fast_battery/src")
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/adder_lat/sub10")
from lin_diff import screen_lin_diff

M = np.uint64(0xFFFFFFFFFFFFFFFF)
def rotl(x, r):
    r %= 64
    if r == 0: return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64-r))) & M

def mix_muxd2(x, k, stages):
    """x,k: uint64 arrays. stages: list of (s,a,b,d)."""
    x = (x ^ k) & M
    for (s,a,b,d) in stages:
        g = ((rotl(x,s) & rotl(x,a)) | ((~rotl(x,s)) & rotl(x,b))) & M
        x = (x ^ g ^ rotl(x,d)) & M
    x = (x ^ rotl(k,13)) & M
    return x

def trial(stages, seed=0):
    rng = random.Random(seed)
    keys = [rng.getrandbits(64), rng.getrandbits(64)]
    seq = {}
    for k in keys:
        xs = np.arange(1<<18, dtype=np.uint64)
        seq[k] = mix_muxd2(xs, np.uint64(k), stages)
    res = screen_lin_diff(seq, verbose=False)
    return res['lin_verdict'] == 'PASS' and res['diff_verdict'] == 'PASS', res

if __name__ == "__main__":
    import json
    rng = random.Random(0x5EED)
    N = 200
    keeps = []
    print(f"screening {N} random 2-stage MUXD...", flush=True)
    for i in range(N):
        stages = [tuple(rng.randint(0,63) for _ in range(4)) for _ in range(2)]
        # Avoid trivial (s==a==b etc.)
        ok, res = trial(stages, seed=i)
        status = "KEEP" if ok else "REJECT"
        print(f"[{i}] {status} stages={stages}", flush=True)
        if ok:
            keeps.append(stages)
            with open("muxd2_screen.jsonl", "a") as f:
                f.write(json.dumps({"i": i, "stages": stages}) + "\n")
    print(f"DONE keeps={len(keeps)}/{N}")
