# Direction 3: Toffoli / Reversible Nonlinear Gates (REPAIRED)

## Status (2026-10-12)

**The as-specified design is KILLED — it is not bijective.** The repair (bipartite /
alternating-parity Toffoli) restores genuine structural bijectivity. Details below.

## 1. The single-Toffoli involution (correct)

Toffoli on bits `(i; j, k)` with `j, k` **frozen**:
`T(x)[i] = x[i] XOR (x[j] AND x[k])`, `T(x)[m] = x[m]` for `m ≠ i`.

`T` is an involution:
`T(T(x))[i] = T(x)[i] XOR (T(x)[j] AND T(x)[k])`
`= [x[i] XOR (x[j] AND x[k])] XOR (x[j] AND x[k])` (controls untouched, so `T(x)[j]=x[j]`)
`= x[i]`. ∎

A network of Toffolis is bijective **only if every control bit is frozen within the
network** (not a target of any gate in the same network).

## 2. KILL: the specified 64-parallel stage is NOT bijective

Specified stage: `S(x)[i] = x[i] XOR (x[(i+a)%64] AND x[(i+b)%64])` for all `i`.

**Explicit collision (analytic, any `a`, `b`, any `n`):**
- `S(0^n)[i] = 0 XOR (0 AND 0) = 0` → `S(0^64) = 0^64`.
- `S(1^n)[i] = 1 XOR (1 AND 1) = 0` → `S(1^64) = 0^64`.
- Hence `S(0^64) = S(1^64)`: not injective. ∎

Brute-force confirmation (`bij_check.py`): collisions at n=3,4,5 for offsets (1,2);
analytic collision verified at n=64.

**Root cause:** the involution proof (§1) requires controls `j,k` to be unmodified,
but in the parallel stage every bit is simultaneously a target (of its own gate)
and a control (of two others). "Disjoint targets" is not sufficient — controls must
be disjoint from targets too. The task's "bijectivity is FREE (structural)" does not
transfer from one Toffoli to the parallel network.

**Cost correction:** the task estimates 1 AND2 (1u) + 1 XOR2 (1.8u) = 2.8u/stage.
Measured genlib (`~/workspace/mix/synth/mini.genlib`): AND2 = 1.5u, XOR2 = 2.0u →
**3.5u/stage nominal** (AND→XOR serial is the floor; no AND-XOR complex gate exists
in the genlib). 3 stages = 10.5u nominal — over the 10u budget before measuring.

## 3. Repair A (adopted): bipartite / alternating-parity Toffoli

Partition bits by parity. Offsets `a, b` **odd**, so targets and controls never mix.

- **Stage E** (even targets, odd controls frozen):
  `out[2i] = in[2i] XOR (in[(2i+a)%64] AND in[(2i+b)%64])`, `out[2i+1] = in[2i+1]`.
- **Stage O** (odd targets, even controls frozen): mirror image.

**Bijectivity proof:** Stage E is 32 disjoint Toffolis whose 32 control bits (odd)
are not targets of the stage. By §1 each is an involution on the full 64-bit state
(apply twice: controls unchanged → the AND term repeats → target XORed twice);
32 commuting involutions compose to an involution. Hence Stage E is bijective
(its own inverse). Same for Stage O. ∎

Brute-force confirmation (`bij_check.py`): bijective at n=4,6,8 for (1,3); proof is
general in `n`.

**Cost:** 3.5u/stage nominal (same primitive). Full round E+O = **7.0u nominal** —
all 64 bits nonlinearly updated, under the 10u budget with margin.

## 4. Repair B (noted, not pursued): Feistel-Toffoli

Split 64 → L,R (32 bits). Round: `L' = L`, `R' = R XOR F(L)` with
`F(L)[i] = L[(i+a)&31] AND L[(i+b)&31]`; bijective for *any* `F` (standard Feistel).
This is Direction 2's construction, so it belongs to that lane.

## 5. Repair C (rejected): Keccak-χ form

`out[i] = in[i] XOR ((NOT in[i+a]) AND in[i+b])` avoids the §2 collision, but
brute force shows it is bijective **iff n is odd** (n=3,5,7 bijective; n=4,6 not).
n=64 is even → broken. Rejected.

## 6. Influence / diffusion analysis (Repair A)

**KILL (structural):** Repair A cannot pass the DIFF screen within <10u.

DIFF requires: for each input delta `2^k` (`k<18`), each output bit `j<8` must be
influenced by input `k` — else the low-8-bit chi2 is catastrophic (a never-flipping
bit zeroes 128/256 bins). So each low output needs **backward influence ≥18**.

But bijectivity forces frozen controls (a partition). The optimal 2-partition
(parity) gives an output backward fanout from only ⌈s/2⌉ of the s stages. With
per-output read `r` (r=3 for Toffoli): backward ≤ r^⌈s/2⌉.
- s=2 (7.0u): r^1 = 3 < 18. DEAD.
- s=3 (10.5u): over budget. DEAD.

Empirical confirmation (`struct_check`): 2-stage gives 1-3/8 low bits flipping
per delta; 3-stage gives ≤6/8. The parity structure is a dead end.

Cheaper gates don't help: NAND2-Toffoli (`out[i]=in[i]^~(in[j]&in[k])`, 3.0u/stage,
still an involution) has the same influence bound. NAND4-Toffoli (r=5, 3.4u/stage):
s=3 gives 5^2=25≥18 structurally, but 3×3.4=10.2u nominal — over budget, and the
parity halving still applies (even outputs see only 2 of 3 stages).

## 7. Lead (not killed): partitioned (C1/C2) NAND4-Toffoli

A non-parity partition escapes the halving: 
- Stage 1: controls C1={0..8} (frozen), targets T1={9..63}.
- Stage 2: controls C2={9..17} (frozen), targets T2={0..8}∪{18..63}.
Each stage is an involution (controls ∩ targets = ∅) → bijective. 2 stages × 3.4u
(NAND4) = **6.8u nominal < 10u**.

Backward for output j<8: {j} ∪ C2 ∪ C1 = {0..17} (19 ≥ 18) — full 2-stage fanout,
no halving. Measured (`c1c2_test.py`): 7-8/8 low bits flip for deltas k<9
(vs 1-3/8 for parity). Deltas k≥9 get 3-4/8 — a **control-slot bottleneck**
(8 outputs × 4 slots = 32 < 9×8 = 72 pairs); needs wiring co-design (expander
graph over the control slots) plus uniformity validation. **Recorded as a lead,
not a concrete design.**

## 8. Measurement plan

1. `toffoli.py`/`toffoli_fast.py`: bit-sliced + word-level functional models (n=64),
   offset search with cheap proxies, then `lin_diff.screen_lin_diff` **verbatim**
   on top candidates (N=2^18 sequential). **DONE**: 2-stage E(1,3)+O(5,13) →
   LIN FLAG (D=4096/4096), DIFF FLAG (worst|z|=922819) — triage REJECT, confirming
   the structural kill (`fisher_triage.py`, `fisher_2stage.log`).
2. `gen_toffoli.py`: Verilog for 1/2/3-stage bipartite AND2. **S0 measured**
   (run_synth.py, ref mul64 103.5u, XCHECK clean):
   - 1-stage: **3.0u** / 64 cells / 192 area (`s0_1stage.log`)
   - 2-stage (E+O): **6.2u** / 224 cells / 512 area (`s0_2stage.log`)
   - 3-stage (E+O+E): **7.9u** / 288 cells / 896 area (`s0_3stage.log`)
     — under 10u, but Fisher-triaged verbatim: LIN FLAG (D=4096/4096),
     DIFF FLAG (worst|z|=876387) — TRIAGE REJECT (`fisher_3stage.log`).
3. `gen_c1c2.py`: Verilog for the C1/C2 NAND4 lead (2-stage). **S0 = 6.8u** /
   221 cells / 790 area (`s0_c1c2.log`) — matches the 6.8u nominal.
4. Verdict → VERDICT_SCOPE.md (**O152**, claimed after re-reading ledger at write
   time; O149–O151 taken by sibling lanes during this work).
