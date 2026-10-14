# Test Report — RV64 `mix` 10-round SPN statistical validation

Date: 2026-10-01. All numbers measured. Logs: [`tests_final.log`](tests_final.log),
[`tests_final_v2.log`](tests_final_v2.log), [`tests_adversarial.log`](tests_adversarial.log), [`keyscan.log`](keyscan.log), [`keyscan12.log`](keyscan12.log).

## 1. Method

- Candidates: SplitMix64, Murmur3-fmix64 (baselines), SPN-8, SPN-10
  (`x = val^key; 10× x=P(S(x^rk[i])); out=x^rk[10]`, PRESENT S-box/pLayer).
- Battery ([`tests_final.py`](tests_final.py)): SAC avalanche (4096 trials, value+key),
  BIC (8192 trials), sequential uniformity (N=2^20, m=4..14), sequence
  battery on 6 input configs × 22–23 tests (raw monobit, per-bit monobit
  screen, low-bit χ², nibble pairs, exact Lemire X∈{2,3,10,1000,2^32,2^64−1},
  masks m∈{1,2,4,8,12}, exact mod-y y∈{3,7,10,100,1000}).
- Null distributions are EXACT (preimage counts, not uniform bins):
  Lemire `#{s:(sX)>>64∈[lo,hi)} = ceil(hi·2^64/X) − ceil(lo·2^64/X)`;
  mod-y `#{s:s mod y=r} = ((2^64−1−r)//y)+1`. Independently verified by
  brute force on toy widths (peer review).
- Flag threshold |z|>4; flags reported with p-value scale noted
  (|z|>4 ⟺ p≈0.01 at df=1, p≈6×10⁻⁵ at df=1023).

## 2. Results — main battery ([tests_final_v2.log](tests_final_v2.log), per-bit screen included)

| Candidate | SAC val max|dev| | BIC max|corr| | Seq χ² (m≤14) | Battery flags |
|---|---|---|---|---|
| SplitMix64 | 0.03027 | 1.0000* | |z|≤1.08 | 0 |
| Murmur3-fmix64 | 0.02686 | 0.9653* | |z|≤0.95 | 0 |
| SPN-8 | 0.02661 | 0.0354 | |z|≤1.03 | 17 (z up to +212) |
| SPN-10 | 0.02783 | 0.0439 | |z|≤1.09 | 2 (both investigated) |

\* Structural: Murmur out[1]≈¬out[34] on input-bit-0 flips (phi=−0.964);
SplitMix perfect correlation on bit pairs (j,j+31) for high input-bit
flips — integer multiply diffuses only upward, final xorshift mirrors it.
Both reproduced independently; not test artifacts.

SPN-10's two flags:
1. `stride-big mask-m=1 z=+4.49` — 16× follow-up z=+0.21, neighbors clean.
   At df=1 this is a p≈0.01 event; ≈28% likely somewhere in the battery.
   Classified fluctuation.
2. `seq64-oddkey perbit-max|z| z=+4.37` (bit 37, key 0xDEADBEEFDEADBEEF,
   sequential inputs) — REAL small bias, see §4.

## 3. Round-count decision

- SPN-8: REJECTED. Lemire-X=2 z=+212, X=10 z=+77 on sequential inputs;
  MSB fraction 0.483 (z=−17.3). Key-dependent (some keys clean).
- SPN-9: REJECTED. Worst key z=+5.3→+9.1→+29.6 at N=2^16→2^18→2^20
  (grows ∝√N — genuine bias).
- SPN-10: selected. Clean on all 6 configs × 23 tests except §2 items;
  adversarial battery (7 worst-case configs): 0 flags, worst |z|=2.32.

## 4. Known small-bias phenomenon (disclosed, not hidden)

Independent per-bit screening found genuine small key-dependent
single-bit biases on *sequential* inputs:

- SPN-10: ~20% of keys show some bit with |z|>4 at N=2^18
  (32-key scan: 7/32 flags, worst z=+5.53, i.e. δ≈0.004–0.005).
  Example: key 0xDEADBEEFDEADBEEF bit 37, δ≈+0.002 persistent across
  V-blocks (z=+4.4→+6.3→+8.3 at N=2^18→2^20→2^22).
- Third instance: key 0x1234, stride-3 inputs, bit 23 — strong local bias
  at small V (block 0 z=−4.57) plus weak persistent bias across all blocks
  (blocks 1–15 combined z≈−3.9), overall δ≈−0.0012 at N=2^22. The
  non-monotonic N-scaling (z=−4.57→−0.77→−4.94) is explained by this
  two-component structure, not by noise.
- SplitMix64 shows the same phenomenon (bit 31, δ≈+0.0033 at N=2^18;
  32-key scan: 0/32 flags, worst z=3.49 — rarer/smaller, not absent).
- SPN-12: 0/32 flags, worst z=3.42 — the effect attenuates away.

Impact assessment:
- Undetectable after every reduction the use case applies: all Lemire /
  mask / mod-y tests pass for SPN-10 on the affected configs.
- A single-bit δ=0.004 bias shifts hash-bucket probabilities by
  O(δ·2^b·X/2^64) — negligible for any practical X.
- The literal "passes for every key on raw output" requirement is not
  met by SPN-10 — nor by SplitMix64/Murmur3-fmix64. Honest claim:
  parity-or-better vs baselines on the tested battery.

## 5. Key sweeps

- 128 random keys, SPN-10, sequential N=2^16, MSB/LSB: 1 flag
  (key 0x21ce242cfbb06b3c MSB z=+4.53); 4× follow-up z=+1.53, 16× z=−1.10,
  neighbors clean — fluctuation.
- Crypto-reviewer 24-key sweep: max|z|=2.91, zero flags.

## 6. What was NOT tested

- Standard batteries (PractRand/Dieharder/TestU01) — not installed.
- ~40 distinct keys of 2^64; 6 Lemire X values; 5 mod-y values;
  single key in PART C uniformity.
- Key-sequenced inputs, related-key behavior, X>2^64−1 impossible by
  construction (X is 64-bit).
- Finite testing cannot certify all keys/strides; key-dependent
  weaknesses (§4) prove sampling can miss things.

## 7. Peer review (2026-10-01, reports in [`reviews/`](reviews/))

- RTL: PASS, no logic bugs (independent model, 400+400 vectors,
  exhaustive S-box/pLayer/key-schedule checks). Test-hygiene fixes
  applied (missing-file FATAL guards, explicit verdicts).
- Statistics: exact nulls verified by brute force; all headline
  findings confirmed; found the §4 phenomenon (per-bit coverage gap now
  closed in the battery).
- Crypto: S-box DDT=2⁻²/LAT=2⁻² verified; ≥20 active S-boxes ⇒
  ≤2⁻⁴⁰ differential / ≤2⁻²⁰ linear per characteristic, key-independent;
  no related-key resistance by design (stated, not hidden);
  14/55 round pairs admit 2–4 exact-collision weak keys (≤2⁻⁶² — negligible).
- Synthesis/ISA: all six relative numbers reproduced; `-fast` flow
  fairly applied; doc fixes F1–F9 applied.

## 8. Reproduction

```
python3 tests_final.py        # main battery (~2 min)
python3 tests_adversarial.py  # adversarial configs (~40 s)
```
Golden RTL vectors: [`golden_vectors.txt`](golden_vectors.txt) (8/8 in [`rtl/tb_golden.v`](rtl/tb_golden.v)).
