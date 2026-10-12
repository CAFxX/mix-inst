"""3-stage MUXD model (V2, fresh rotations). Bit-exact vectorized numpy."""
import numpy as np

M = np.uint64(0xFFFFFFFFFFFFFFFF)

def rotl(x, r):
    r %= 64
    if r == 0:
        return x
    return ((x << np.uint64(r)) | (x >> np.uint64(64 - r))) & M

def muxd_stage(x, s, a, b, d):
    """One MUXD stage. x: uint64 array. g = (rotl(x,s)&rotl(x,a)) | (~rotl(x,s)&rotl(x,b)); y = x^g^rotl(x,d)."""
    g = ((rotl(x, s) & rotl(x, a)) | ((~rotl(x, s)) & rotl(x, b))) & M
    return (x ^ g ^ rotl(x, d)) & M

def mix_muxd3(x, k, stages):
    """x,k: uint64 arrays/scalars. stages: list of (s,a,b,d), exactly 3."""
    assert len(stages) == 3
    x = (x ^ k) & M
    for (s, a, b, d) in stages:
        x = muxd_stage(x, s, a, b, d)
    x = (x ^ rotl(k, 13)) & M
    return x

def muxd3_scalar(x, k, stages):
    """Scalar reference (pure Python ints) for cross-checking the vectorized model."""
    MM = (1 << 64) - 1
    def rl(v, r):
        r %= 64
        return ((v << r) | (v >> (64 - r))) & MM if r else v
    x ^= k
    x &= MM
    for (s, a, b, d) in stages:
        xs, xa, xb = rl(x, s), rl(x, a), rl(x, b)
        g = ((xs & xa) | ((~xs) & xb)) & MM
        x = (x ^ g ^ rl(x, d)) & MM
    return (x ^ rl(k, 13)) & MM

if __name__ == "__main__":
    import random
    rng = random.Random(0x1234)
    stages = [tuple(rng.randint(0, 63) for _ in range(4)) for _ in range(3)]
    xs = np.array([rng.getrandbits(64) for _ in range(200)], dtype=np.uint64)
    k = np.uint64(rng.getrandbits(64))
    vec = mix_muxd3(xs, k, stages)
    for i, xv in enumerate(xs):
        ref = muxd3_scalar(int(xv), int(k), stages)
        assert int(vec[i]) == ref, f"mismatch at {i}: {int(vec[i]):016x} vs {ref:016x}"
    print(f"model self-check OK: 200/200 vectors match scalar reference, stages={stages}")
