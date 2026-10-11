# Control experiment: non-pow2 reduction artifact (2026-10-02)

**Finding:** PractRand BCFN FAILs on `mod1e9p7`, `lemire1e9p7`, `mod1000`
reductions are a REDUCTION ARTIFACT, not a candidate defect.

**Evidence:** splitmix64 (known-good PRNG, PractRand-clean at 1GB+ in standard
use) reduced via `x % 1000000007` and fed as stdin32 FAILs BCFN identically:
`BCFN(2+0,13-3U) R>+99999 p = 0 FAIL`.

**Mechanism:** values in [0, 1000000007) use only 30 of 32 bits; the top
2 bits of every 32-bit word are structurally zero. PractRand's BCFN
(binary-matrix-rank family) detects constant bit positions catastrophically.
Same for mod1000 ([0,1000), top 6+ bits zero in 16-bit words).

**Implication for Table 2:** FAIL@BCFN on lemire1e9p7/mod1e9p7/mod1000 cells
does NOT discriminate candidate quality — every candidate (and splitmix64)
fails identically. These cells are reported for completeness but excluded
from quality ranking. The discriminating reductions are the pow2 ones
(low8/low16/low32/high32/xor32), where the full word width carries entropy.
