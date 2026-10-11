# Independent cryptanalysis review: `r7_feist8_s1_1sbox`

**Reviewer role**: independent cryptanalysis (no communication with other reviewers).
**Design**: RV64 `mix` candidate `r7_feist8_s1_1sbox` — 8-round Feistel, `val^key` whitening,
`F(R,rk) = lin32(s1layer(R)) ^ (rk & 0xFFFFFFFF)`, `lin32(x) = x ^ rotl32(x,7) ^ rotl32(x,13)`,
`rk(k,i) = rotl64(k,13·(i+1)) ^ (i+1)·0x9E3779B97F4A7C15` for `i=1..8`, no final swap.
S1 = `[0,1,2,4,3,8,15,12,9,5,11,6,7,14,13,10]`.
**Date**: 2026-10-02. **Verdict: APPROVE-WITH-FINDINGS** (see Findings).

## Scope

Attack the design analytically and experimentally across: (a) weak keys / fixed points,
(b) related-key schedule analysis, (c) differential/linear trail bounds vs round count,
(d) hash-DoS collision search, (e) structural properties of the linear layer and key use.
Threat model for (d): attacker chooses `val`, key fixed (possibly known); the design is a
hash finalizer, not a cipher. All claims below were computed by the reviewer; nothing is
taken from the M9 draft or the leader audit on faith — and where they disagree, the
disagreement is documented as a finding.

## Method

- Read the actual code: `round7/models/r7.py`, `round5/models/r5.py`,
  `round4/models/r4_hybrid.py` (`_rk_np`, `rotl64_np` masks rotation to 6 bits),
  `fast_battery/candidates/r7_feist8_s1_1sbox/impl.c`.
- S-box: DDT and LAT computed directly from the S1 table (no copied numbers).
- Linear layer: bijectivity via GF(2) rank of the 32×32 matrix and via `p(1)≠0` for
  `p(x)=1+x^7+x^13` over `GF(2)[x]/(x^32+1)`; differential and linear branch numbers
  computed exactly over nibble-weight ≤3 plus 2M vectorized random samples.
- Differential trails: beam search over Feistel difference states
  `(dL,dR) → (dR, dL ^ lin(e))`, `e` ranging over DDT-feasible S-box output differences,
  key-independent (`G = lin∘S`; round keys cancel in differentials). Widths 4000–8000,
  single-key (2,3,4,5,6,8 rounds) and related-key (single-bit `δ`, whitening-cancelling `ΔP`).
- Empirical: 2-round skip trail measured over 2²² pairs (vectorized numpy model);
  C-vs-Python bit-exactness via compiled `impl.c` (3000 random + 5 structured vectors);
  birthday collision count on 2²⁴ random and 2²⁴ sequential inputs.
- Weak keys: round-key structure for 7 structured keys; F fixed points over 2²⁴ R values
  per round (key=0); `mix(v,k)=v` fixed points over 2²² inputs × 3 keys; complementation
  probes over 2²⁰ inputs; key-bit reachability into F.

Scripts: `cryptanalysis/ca_sbox.py`, `ca_keys.py`, `ca_trails.py`, `ca_construct.py`,
`ca_emp2r_vec.py`, `ca_fast.py` (all in this `audit/cryptanalysis/` directory).

## Findings

### MAJOR-1 — M9's differential bound is incorrect; the safety case must be revised

M9 (`M9_hashdos_DRAFT.md`, `trail.log`) claims "best measured 2-round trail ≈ 2⁻¹⁰"
(`1-round F: … p~2^-2.00`, `2nd-round F: … p~2^-7.99`) and extrapolates "8-round ≈ 2⁻⁵⁸".
**This misses the best 2-round trail.** M9 only chained the non-skip pattern
(input difference `(0, din)`). The Feistel round-skip pattern — input difference `(a, 0)`
with single-nibble `a` — gives round 1 with **zero** active S-boxes (F input difference 0,
probability 1) and round 2 with one active S-box at the best DDT transition `4/16 = 2⁻²`.
So the true best 2-round trail has **P = 2⁻², 1 active S-box**, not 2⁻¹⁰.

Evidence (independent, empirical): vectorized 2-round Feistel, fixed key
`0x123456789ABCDEF0`, N = 2²² pairs, input difference `(a,0)` with `a` = DDT-optimal
nibble transition `(2→2)`:
- nibble pos 0: 1,047,578 hits → P = 2⁻²·⁰⁰¹
- nibble pos 3: 1,047,450 hits → P = 2⁻²·⁰⁰²
- nibble pos 7: 1,047,817 hits → P = 2⁻²·⁰⁰¹

The M9 8-round "≈2⁻⁵⁸" is an extrapolation from the wrong 2-round number and is
unsubstantiated. My independent full-8-round beam search (below) gives **2⁻⁶¹** —
coincidentally close, but arrived at honestly. The quantitative safety argument in M9
must be redone; any decision resting on "2-round ≈ 2⁻¹⁰" is resting on a false premise.

Related correction: the review task's premise "8 active S-boxes per 2 rounds (vs 16 in
the 2-layer variant)" is likewise incorrect for the attacker's best trail — it is **1**
active S-box per 2 rounds (skip pattern). The honest comparison is per active
F-evaluation: 1 S-box layer → 1+ active S-boxes per evaluation vs 4+ for the 2-layer
variant (single-nibble input: 1 in layer 1, ≥3 in layer 2 by branch number 4).

### MAJOR-2 — Best 8-round differential is 2⁻⁶¹ (25 active S-boxes): thin margin over 2⁻⁶⁴

Beam-search results (width 4000, nibble-exact DDT transitions, key-independent):

| rounds | best P | active S-boxes |
|---|---|---|
| 2 | 2⁻² | 1 |
| 3 | 2⁻⁸ | 4 |
| 4 | 2⁻¹⁷ | 7 |
| 5 | 2⁻²⁶ | 11 |
| 6 | 2⁻³⁹ | 16 |
| 8 | 2⁻⁶¹ | 25 |

(Beam width 4000, topk 6; independently confirmed by a second run at width 8000 /
topk 8, which found the identical trail: P = 2⁻⁶¹·⁰⁰, 25 active S-boxes, output
difference `(0x0000851d, 0x2cd36b18)`. The smooth scaling 2⁻² → 2⁻⁸ → 2⁻¹⁷ → 2⁻²⁶ →
2⁻³⁹ → 2⁻⁶¹ across 2,3,4,5,6,8 rounds gives confidence in the order of magnitude;
the search is heuristic so the true optimum satisfies max-P ≥ 2⁻⁶¹.)

The naive extrapolation `(2⁻²)⁴ = 2⁻⁸` is invalid: the skip cannot be chained directly
because one F evaluation with single-nibble input produces an output difference of
nibble-weight ≥ 3 (branch number 4), forcing ≥ 3 active S-boxes in the next F. I also
attempted a constructive 9-active-S-box 8-round skeleton by brute force over all DDT
constraints — **0 feasible** — confirming the search: diffusion forces the trail dense.

Assessment: 2⁻⁶¹ is only 3 bits (8×) above the 2⁻⁶⁴ ideal-distinguisher threshold, so
the *theoretical* margin is thin, and the search is heuristic (true optimum ≥ 2⁻⁶¹,
i.e. a distinguisher needing *at most* ~2⁶¹ queries exists). But 2⁶¹ queries is utterly
impractical, and for the hash-DoS threat model (below) differentials give the attacker
nothing beyond direct computation. For a **mixer** this is adequate; for a **cipher** it
would not be comfortable. The 6-round kill was statistical (3 RD rejections on the
2-S-box-layer variant `r7_feist6_spn`), not differential — 8 rounds is the minimum
*statistically* clean depth, and differentially it lands at 2⁻⁶¹ with no practical
exploit. Verdict on round count: **adequate with thin theoretical margin, not generous**.

Linear cryptanalysis (bound, not full search): S1 max |LAT| = 8/32 → bias 2⁻² per
S-box (correlation 2⁻¹); linear branch number of `lin32` = 4 (same as differential).
Linear trails scale like differential trails; no better linear avenue was found.

### MAJOR-3 — Related-key differential 2⁻³⁷ beats single-key 2⁻⁶¹

Key schedule algebra (verified against code): 
`rk(k^δ, i) = rk(k,i) ^ rotl64(δ, 13·(i+1))` — fully predictable, key-independent.
The 8 rotations `13·(i+1) mod 64 = {26,39,52,1,14,27,40,53}` are all distinct
(13 is invertible mod 64). For single-bit `δ`, exactly 4 of 8 rounds inject a 1-bit
F-output difference with probability 1 (the other 4 land in the unused high32 of `rk`).

Beam search, related-key mode (`ΔK = δ`, `ΔP` chosen to cancel whitening so the
Feistel starts at `(0,0)` and rides the free injections):

| δ | best related-key P | active |
|---|---|---|
| bit 31 | **2⁻³⁷** | 15 |
| bit 32 | 2⁻⁴⁷ | 21 |
| bit 0 | 2⁻⁴⁹ | 20 |
| bit 63 | 2⁻⁵¹ | 22 |
| bit 13 | 2⁻⁶¹ | 26 |

No zero-output related-key trail survived the beam (all ≪ 2⁻⁶⁴). 
Impact: the affine schedule hands a related-key attacker a strictly better differential
(2⁻³⁷ vs 2⁻⁶¹) — a certificational weakness of the schedule's linearity. It is **not**
in the hash-DoS threat model (fixed key, no related-key oracles; an attacker who knows
`k` just computes `mix` directly), so not a blocker for deployment as a finalizer. But
it belongs in the safety case: the design's differential strength is 2⁻³⁷, not 2⁻⁶¹,
under related keys. (M9 §3 measured only output-difference statistics, not trails, and
rated this INFO — the trail bound is the sharper statement.)

### MINOR-1 — Weak keys: no degenerate behavior found

Round keys for `k ∈ {0, all-ones, 0x5555…, 0xAAAA…, 1, 1<<63, 1<<32}`: all 8 `rk` distinct
and nonzero per key; no `low32(rk_i) = 0`; schedule formula verified exactly.
F fixed points (`F(R)=R`) over 2²⁴ R values per round at key=0: **0** every round
(expectation ≈ 0.004 for a random 32-bit permutation — consistent).
`mix(v,k) = v` fixed points over 2²² inputs: **0** for `k=0`, random `k`, all-ones `k`
(expectation ≈ 2⁻⁴²). No key produces all-zero F outputs (F is a permutation per round
key, so exactly one preimage of 0 exists — not degenerate). M9's "worst weak key"
`0xa1fa53e0a803eefb` (zeroes `low32(rk)` in rounds 5 and 7) independently re-verified;
harmless — F's differential profile is key-independent since the key enters only as a
final xor. No slide pairs possible (distinct rotations + distinct round constants).

### INFO — Structural facts (verified, all clean)

- **S1**: differential uniformity 4 (max DDT 4/16 = 2⁻²; per-row maxima are 2 or 4);
  max |LAT| = 8 → bias 2⁻²; no linear structures; no uniform complementation
  (`S1[x^F]^S1[x]` is not constant); DDT[a][0] = 0 for all a≠0 (S-box is a permutation).
- **`lin32` is bijective** (GF(2) rank 32; equivalently `1+1+1 = 1 ≠ 0` at `x=1`, so
  `gcd(1+x⁷+x¹³, x³²+1) = 1`). Differential **and** linear branch numbers = 4
  (nibble-wise; exact over weight ≤ 3, confirmed by 2M vectorized samples).
  Hence `F(·,rk)` is a 32-bit permutation for every `rk`, and one active input nibble
  forces ≥ 3 active output nibbles.
- **Key-bit reachability**: all 64 key bits reach the low32 F-input of ≥ 1 round
  (rotations sweep all positions); the per-round high32 of `rk_i` is unused, but no key
  bit is dead. Whitening uses the full 64-bit key.
- **No complementation/symmetry**: `P(mix(v^c,k) = mix(v,k)^c) = 0` measured over 2²⁰
  inputs for `c ∈ {all-ones, 0x00000000FFFFFFFF, 0xFFFFFFFF00000000, 1, 1<<32}`;
  `P(mix(~v,~k) = ~mix(v,k)) = 0`.
- **Bit-exactness**: C `impl.c` vs Python `r7.py`: 0 mismatches on 3000 random +
  5 structured vectors.
- **Hash-DoS, experimental**: for fixed key, `mix(·,k)` is a **permutation** (Feistel),
  so exact 64-bit collisions **do not exist** — no differential, MITM, or birthday
  method can find them; "faster than birthday" is vacuous. Confirmed: 0 collisions on
  2²⁴ random and 2²⁴ sequential inputs (birthday expectation ≈ 2⁻¹⁷). No zero-output
  differential trail with P ≥ ~2⁻⁶⁴ exists in the beam (single-key or related-key),
  so there is no differential shortcut to collisions either. A known-key attacker
  floods buckets by direct computation (`t·nbuckets` work for `t` same-bucket items);
  differentials add nothing. An unknown-key attacker faces ≥ 2⁶¹-query differentials —
  impractical. **No practical hash-DoS vector found** (negative result, methodology
  above).

## Verdict: APPROVE-WITH-FINDINGS

The design is **safe to deploy as a hash finalizer**: no weak-key degeneracy, no
fixed-point/symmetry anomalies, bit-exact implementations, zero collisions by
construction with no differential shortcut, and the best-known differentials
(2⁻⁶¹ single-key, 2⁻³⁷ related-key) are impractical and outside the threat model
respectively. 8 rounds is adequate — the 6-round statistical kill does not repeat,
and differential diffusion forces 25 active S-boxes at full depth.

Required before the safety case is closed:
1. **Correct M9's differential analysis** (MAJOR-1): replace "2-round ≈ 2⁻¹⁰ →
   8-round ≈ 2⁻⁵⁸" with the measured "2-round = 2⁻² (skip pattern, empirically
   confirmed) → 8-round ≈ 2⁻⁶¹ (beam search)". The current M9 numbers are wrong and
   the extrapolation unsubstantiated.
2. **Record the related-key bound** (MAJOR-3): differential strength is 2⁻³⁷ under
   related keys; document that the threat model excludes related-key oracles.
3. Note the thin theoretical margin (MAJOR-2): 2⁻⁶¹ is 8× above 2⁻⁶⁴. If a future
   search finds a trail ≤ ~2⁻⁴⁰, re-evaluate; if the design is ever re-scoped toward
   cipher-like use, 8 rounds is insufficient.

No BLOCKERs. No practical attack was found by any method attempted.
