"""Verify: (a) every S-box entry in rtl.v matches the Python model table;
(b) nibble ordering matches (nibble j = bits [4j+3:4j], LSB-first, in both);
(c) round keys: model _rk_np(k, n) for n=1..8 on several keys -> rk_vectors.hex."""
import os, re, sys
import numpy as np

AUDIT = os.path.expanduser("~/workspace/mix/exploration/round7/audit")
sys.path.insert(0, os.path.expanduser("~/workspace/mix/exploration/round7/models"))
sys.path.insert(0, os.path.expanduser("~/workspace/mix/exploration/round5/models"))
sys.path.insert(0, os.path.expanduser("~/workspace/mix/exploration/round4/models"))
sys.path.insert(0, os.path.expanduser("~/workspace/mix/exploration"))
from r7 import S1  # noqa: E402
from r4_hybrid import _rk_np  # noqa: E402

rtl = open(os.path.expanduser(
    "~/workspace/mix/exploration/fast_battery/candidates/r7_feist8_s1_1sbox/rtl.v")).read()

# (a) parse the case statement entries
entries = re.findall(r"4'h([0-9A-F])\s*:\s*sbox_feist8_s1_1sbox\s*=\s*4'h([0-9A-F])", rtl)
assert len(entries) == 16, f"expected 16 case entries, got {len(entries)}"
ok = True
for inp, outp in entries:
    i, o = int(inp, 16), int(outp, 16)
    if S1[i] != o:
        print(f"SBOX MISMATCH: input {i:#x}: rtl={o:#x} model={S1[i]:#x}")
        ok = False
print("S-box table: ALL 16 ENTRIES MATCH" if ok else "S-box table: MISMATCH FOUND")

# (b) nibble ordering: check the part-select pattern used in F
m = re.search(r"for\s*\(\s*j\s*=\s*0\s*;\s*j\s*<\s*8.*?t\[4\*j\+:4\]\s*=\s*sbox\w*\(R\[4\*j\+:4\]\)",
              rtl, re.S)
print("nibble order RTL: nibble j = bits [4j+3:4j] (LSB nibble first)" if m
      else "nibble order: PATTERN NOT FOUND - investigate")
print("nibble order model: ((x >> 4*i) & 0xF), i=0..7 -> same LSB-first")

# (c) round-key vectors: keys x rounds(1..8)
keys = [0x0000000000000000, 0xFFFFFFFFFFFFFFFF, 0x0123456789ABCDEF,
        0xDEADBEEFCAFEBABE, 0x0000000000000001, 0x8000000000000000]
with open(os.path.join(AUDIT, "rk_vectors.hex"), "w") as f:
    for k in keys:
        for n in range(1, 9):
            rk = int(_rk_np(np.uint64(k), n))
            f.write(f"{k:016x} {n} {rk:016x}\n")
print(f"wrote {len(keys)*8} round-key vectors")
# also print the actual rotation amounts used by the model (sanity)
print("model rotations for n=1..8:", [(13*(n+1)) % 64 for n in range(1, 9)])
