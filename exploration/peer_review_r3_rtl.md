# Peer review: `r3_xorlin_qm` RTL (round 3, lever a)

**Reviewer:** independent RTL/functional reviewer (peer, not the designer)
**Date:** 2026-10-01
**Scope:** [`rtl/r3/r3_xorlin_qm.v`](rtl/r3/r3_xorlin_qm.v), [`qm_sbox.py`](qm_sbox.py), [`gen_r3.py`](gen_r3.py) (emitter for this variant),
[`check_pipe2.py`](check_pipe2.py), [`gen_pipe2.py`](gen_pipe2.py), [`rtl/r3/mix_pipe2_base.v`](rtl/r3/mix_pipe2_base.v), `results/r3/`
(equivalence outputs). [`round4/`](round4/) untouched. The `r3_xorlin_qm_b` / `_bd` lever
variants were not in scope (same emitter, noted where relevant).

**Method:** everything below was re-derived independently — own Python PRESENT
model, own Verilog-expression parser/evaluator, own QM brute-force, own GF(2)
rank computation, and fresh iverilog/vvp runs of [`check_rtl.py`](check_rtl.py) (500 vectors)
and [`check_pipe2.py`](check_pipe2.py), plus an adversarial 2-cycle-latency variant. No designer
script was trusted for any conclusion.

## Verdict: PASS (functional correctness)

No functional discrepancies found. The RTL is bit-identical to the claimed
spec and to the screened model [`models/spn4_xorlin_1137.py`](models/spn4_xorlin_1137.py); the QM S-box is
exactly correct and exactly minimal; the 1-cycle-latency claim for
`mix_pipe2_base` is accurate and the test is not vacuous.

## Findings

### 1. QM S-box logic — PASS, 0/64 mismatches (exhaustive)

- Wrote an independent parser for all 256 `assign sb{r}_{i}[{b}] = ...;`
  statements in [`rtl/r3/r3_xorlin_qm.v`](rtl/r3/r3_xorlin_qm.v), converted each to a Python Boolean
  function, and evaluated all 16 inputs × 4 output bits × 64 instances
  (4 rounds × 16 nibbles) against the claimed PRESENT table
  `[C,5,6,B,9,0,A,D,3,E,F,8,4,7,1,2]`: **0 mismatches**.
- All 64 instances are textually identical per output bit (1 distinct
  normalized expression per bit across all 64 copies), so there is no
  per-nibble/per-round transcription error.
- Nibble wiring confirmed: `sl{r}_{i} = sx{r}[4i+3:4i]`
  (e.g. `sl0_0 = sx0[3:0]` … `sl0_15 = sx0[63:60]`) and
  `sy{r} = {sb{r}_15, …, sb{r}_0}`, i.e. nibble *i* occupies bits `[4i+3:4i]`
  on both sides; within a nibble `sb[0]` is the LSB, matching integer
  indexing of the table (a bit-reversal would have shown up as mismatches).

### 2. Round structure — PASS

Verified from [`rtl/r3/r3_xorlin_qm.v`](rtl/r3/r3_xorlin_qm.v):
- `s0 = val ^ key` (line 5); each round `sx{i} = s{i} ^ rk{i}` **before** the
  S-box layer (lines 6, 105, 204, 303); linear layer
  `s{i+1} = sy{i} ^ ROTL(sy{i},11) ^ ROTL(sy{i},37)` (lines 104, 203, 302, 401);
  final `out = s4 ^ rk[4]` (line 402). Exactly 4 rounds, key-XOR-then-S-box
  ordering as specified.
- Rotation directions: `{key[50:0],key[63:51]}` = ROTL(key,13),
  `{key[37:0],key[63:38]}` = ROTL(key,26), `{key[24:0],key[63:25]}` =
  ROTL(key,39), `{key[11:0],key[63:12]}` = ROTL(key,52),
  `{key[62:0],key[63:63]}` = ROTL(key,65)=ROTL(key,1) — all left rotates,
  no `(j+1)`/`(j-1)`-class direction bug.
- Linear layer concats `{sy[52:0],sy[63:53]}` = ROTL(·,11),
  `{sy[26:0],sy[63:27]}` = ROTL(·,37) — correct amounts and direction.

### 3. Round-key constants — PASS

All five emitted constants equal `(i+1)·0x9E3779B97F4A7C15 mod 2^64`
(recomputed independently):
`9e3779b97f4a7c15`, `3c6ef372fe94f82a`, `daa66d2c7ddf743f`, `78dde6e5fd29f054`,
`1715609f7c746c69` — lines 6, 105, 204, 303, 402 match exactly.

### 4. [`qm_sbox.py`](qm_sbox.py) bug fix — PASS (fix present, correct, and exactly minimal)

- The reported bug (combine() not checking mask equality → 5/64 invalid
  primes) is fixed: both [`qm_sbox.py`](qm_sbox.py) (`if a[0] != b[0]: return None`) and the
  copy in [`gen_r3.py`](gen_r3.py) carry the mask-equality guard, plus the don't-care
  overlap guard (`if a[0] & diff`). The `covers()` predicate
  `(m & ~p[0]) == p[1]` is correct.
- Independent cross-check: brute-forced the exact minimum SOP per output bit
  by a different method (enumerate all 81 implicants → prime implicants →
  exact set cover minimizing cubes then literals). Result: bit0 = 6 cubes /
  20 lits, bit1 = 5/15, bit2 = 5/16, bit3 = 5/15 — **identical** to what
  [`qm_sbox.py`](qm_sbox.py) prints and to what is emitted in the RTL. The "QM-minimal"
  claim is true, and the exhaustive 0/64 table check (§1) proves the emitted
  cubes implement the right function (minimality alone wouldn't).
- [`gen_r3.py`](gen_r3.py)'s emitter reproduces [`rtl/r3/r3_xorlin_qm.v`](rtl/r3/r3_xorlin_qm.v) **byte-for-byte**
  (re-ran `build_variant("r3_xorlin_qm", set())` with EXP redirected to
  /tmp; `diff` clean), so the file under review is exactly what the reviewed
  generator produces — no hand edits in between.

### 5. Bijectivity (fixed key) — PASS, verified by rank computation

- Linear layer: built the 64×64 GF(2) matrix for
  `L(x) = x ^ ROTL(x,11) ^ ROTL(x,37)` (row *i* =
  `(1<<i)|(1<<((i-11)%64))|(1<<((i-37)%64))`) and computed its rank by
  Gaussian elimination: **rank = 64 → invertible**. (Consistent with the
  model's docstring argument: `1+x^11+x^37` evaluates to 1 at `x=1`, and
  `x^64+1 = (x+1)^64` over GF(2), so the polynomial is coprime to
  `x^64+1`.)
- S-box table has 16 distinct outputs → permutation of 4 bits; 16 parallel
  copies → permutation of 64 bits. XOR with `val^key`/round keys → bijections.
- Composition of bijections ⇒ `val → out` is a permutation of 2^64 for every
  fixed key. The bijectivity claim holds.

### 6. Pipeline 1-cycle-latency claim — PASS, and the test is not vacuous

- Read [`check_pipe2.py`](check_pipe2.py) and [`rtl/r3/mix_pipe2_base.v`](rtl/r3/mix_pipe2_base.v) in full. Structure:
  stage 1 = `val^key` + rounds 0,1 → registers `s2_q/key_q/valid_q` →
  stage 2 = rounds 2,3 + whitening with `key_q` → `out = st2_s2 ^ rk[4]`,
  `valid_out = valid_q`. Exactly one register level ⇒ input presented before
  posedge *i* yields `out == expected` after posedge *i*: **1 clock cycle of
  latency**, 1/cycle throughput. The testbench's per-cycle
  `out !== TEXP[i]` / `valid_out` checks, drain checks, and intermittent-valid
  (gap every 3rd) phase are all correctly aligned to this timing.
- Adversarial test (run for this review): wrapped the DUT with one extra
  output register (true 2-cycle latency) and ran the unmodified generated
  testbench — it **fails** with the textbook one-cycle-shifted signature
  (`MISMATCH i=1: got <exp[0]> …`, plus `THROUGHPUT-FAIL` at i=0). With 64
  random 64-bit vectors a false pass is a 2^-64 event per vector, so the
  reported `PIPECHECK PASS` (reproduced in this review: `PIPE-OK
  mix_pipe2_base`) genuinely establishes 1-cycle latency. Not off-by-one,
  not vacuous.

### 7. Screening-model vs emitted-RTL consistency — PASS

Trust chain verified link by link, each with an independent run:
- My from-scratch scalar spec == [`models/spn4_xorlin_1137.py`](models/spn4_xorlin_1137.py) (both the numpy
  `mix_spn4_xorlin_1137_np` used for screening and the scalar reference):
  300 random vectors, 0 mismatches.
- [`models/spn4_xorlin_1137.py`](models/spn4_xorlin_1137.py) == [`rtl/r3/r3_xorlin_qm.v`](rtl/r3/r3_xorlin_qm.v): re-ran
  [`check_rtl.py`](check_rtl.py) with **500** vectors (fresh seed path in /tmp):
  `RTLCHECK: 500/500 vectors match -> PASS`. The testbench uses `!==`,
  so X-propagation would also have been caught.
- [`gen_r3.py`](gen_r3.py) emitter == file on disk: byte-identical (see §4).
- Hence the statistical screening (run on the model) applied to the exact
  function in the RTL. No discrepancy.

## Minor observations (info only, no action required)

- **(info)** `results/r3/_r3_xorlin_qm/` keeps the compiled `tb_check` binary
  and `vectors.txt` but no saved PASS log; the only record of the original
  equivalence run is [`gen_r3.py`](gen_r3.py)'s stdout (`EQUIV-OK`). This review re-ran it
  (500 vectors, PASS), but future runs should tee the PASS line to a file.
- **(info)** Cosmetic: a few S-box `assign` lines have inconsistent extra
  parentheses (e.g. around single product terms). Harmless — iverilog
  compiles cleanly and all 256 assigns evaluate to the correct table — but
  the emitter could normalize them.
- **(info)** Out of scope but noted: [`r3_xorlin_qm_b.v`](rtl/r3/r3_xorlin_qm_b.v) / `_bd.v` (levers b/d)
  exist in [`rtl/r3/`](rtl/r3/) and share the same emitter/QM code; they were not
  reviewed here.
- **(info)** This review created and then deleted one scratch testbench
  (`results/r3/tb_mix_pipe2_base_2cyc.v`); workspace left as found.

## Severity summary

- Critical: none. Major: none. Minor: none. Info: 4 (all above).
- **Verdict: PASS** — `r3_xorlin_qm` is functionally correct per the claimed
  specification; recommend proceeding to the pending round-3 peer reviews of
  the other (non-functional) aspects.
