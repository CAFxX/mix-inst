"""Wide shallow NAND network: 6 levels of 64-parallel NAND2 with rotations.
Target: 6u total. Each level: t[i] = ~(t[i] & t[(i+r)%64])."""
import numpy as np

def nand_net(x, k, rots=(1, 3, 7, 13, 29, 37)):
    """6-level NAND network. x, k: uint64 arrays."""
    # Level 0: mix x and k
    t = ~(x & k) & np.uint64(0xFFFFFFFFFFFFFFFF)
    for r in rots:
        # rotate t by r, NAND with self
        tr = ((t << np.uint64(r)) | (t >> np.uint64(64-r))) & np.uint64(0xFFFFFFFFFFFFFFFF)
        t = ~(t & tr) & np.uint64(0xFFFFFFFFFFFFFFFF)
    return t

if __name__ == "__main__":
    k = np.uint64(0x123456789ABCDEF0)
    x0 = np.uint64(0x0123456789ABCDEF)
    y0 = nand_net(np.array([x0]), np.array([k]))[0]
    diffs = []
    for i in range(64):
        xi = x0 ^ (np.uint64(1) << np.uint64(i))
        yi = nand_net(np.array([xi]), np.array([k]))[0]
        diffs.append(bin(int(y0) ^ int(yi)).count('1'))
    print(f"6-level NAND: min={min(diffs)} max={max(diffs)} mean={sum(diffs)/len(diffs):.1f}")
    # Bijectivity check (fixed k)
    xs = np.arange(5000, dtype=np.uint64)
    ys = nand_net(xs, np.full_like(xs, k))
    print(f"bijective on 5000-sample: {len(set(ys.tolist())) == 5000}")
