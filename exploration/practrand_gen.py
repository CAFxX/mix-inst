"""PractRand driver for the round-3 winner (via numpy model, bit-identical to V_a RTL).

Generates sequential-input keyed hash stream: out[i] = mix(i, key).
Usage: python3 practrand_gen.py <key_hex> <nbytes> | RNG_test stdin
"""
import sys
sys.path.insert(0, "/home/hatch/workspace/mix/exploration/models")
import numpy as np
from spn4_xorlin_1137 import mix_spn4_xorlin_1137_np

def main():
    key = np.uint64(int(sys.argv[1], 16)) if len(sys.argv) > 1 else np.uint64(0x123456789ABCDEF0)
    nbytes = int(sys.argv[2]) if len(sys.argv) > 2 else (1 << 28)  # 256MB default
    nvals = nbytes // 8
    chunk = 1 << 20  # 1M values per chunk
    out = sys.stdout.buffer
    base = 0
    while base < nvals:
        m = min(chunk, nvals - base)
        vals = np.arange(base, base + m, dtype=np.uint64)
        h = mix_spn4_xorlin_1137_np(vals, key)
        out.write(h.tobytes())
        base += m
    out.flush()

if __name__ == "__main__":
    main()
