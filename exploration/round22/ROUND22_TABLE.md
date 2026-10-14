# Round 22 — Analytical designs (wide SPN / EM-χχ / keyed SPN / Lai–Massey / Beneš)

Date: 2026-10-03. Coordinator: r22 subagent. Design note: [`../sota_analytical_designs.md`](../sota_analytical_designs.md)
(§3 specs, §4 build order). Method: [`../round20/ROUND20_TABLE.md`](../round20/ROUND20_TABLE.md) (S0→S4 + Q1).

**ROUND VERDICT: all 6 candidates S2-killed. Frontier UNCHANGED.**
(Frontier S: r20 chioff13all 37.0u / r19 chioff13 37.4u / r20 chioff31 37.5u;
Frontier Q: r19 fm07/fm11/fm311, r15 parsplit, r9, r8 — see [`../PARETO.md`](../PARETO.md).)

The delays were spectacular (16.9–29.3u, all far below the 37.0u frontier) but
every construction failed differential screening. The analytical value is in
the failure mechanisms: (1) χχ_64 needs many more rounds than the 4–6 tested
(O32/O33); (2) the transpose P-box has fixed points — a broken linear layer
(O34, HIGH re-test trigger with a fixed permutation); (3) Beneš MUX stages are
cryptographically inert (O36); (4) input-dependent differentials (S1, χ) become
deterministic for sequential low inputs, and 4–5 rounds cannot recover
(O31/O32/O35).

## Candidates

| # | Name | Construction (§3) | Predicted |
|---|------|-------------------|-----------|
| A | `r22_wide_spn4_nw` | 4-round wide SPN: `x_{i+1} = L(S16(x_i ⊕ rk_i))`; S1 + (3,11) linear | ~30–32u |
| B | `r22_em_chichi4_nw` | Even-Mansour `P(m⊕k)⊕k`, P = 4× `L(χχ_64(x))`; zero key-schedule cost | ~30u |
| B2 | `r22_em_chichi6_rot_nw` | EM variant: 6× `rotl64(χχ_64(x), r_i)`, `r_i = 13(i+1)%64`; aggressive probe | ~22u |
| C | `r22_keyed_spn6_nw` | 6-round keyed SPN: `x_{i+1} = Π(S16(x_i ⊕ rk_i))`; transpose nibble perm, no linear | ~34u |
| D | `r22_lm5_chi_nw` | 5-round correct Lai–Massey, `d_i = L_i⊕R_i`, `t_i = χ32(d_i⊕rk32_i)`, `(R_i⊕t_i, d_i)` | ~26u |
| E | `r22_benes_chichi_nw` | 11 Beneš keyed-MUX stages + χχ_64 every 3rd stage | ~31u |

Key schedule (all): `rk_i = rotl64(k, 13·(i+1)) ⊕ ((i+1)·0x9E3779B97F4A7C15)`, 0-based `i`.
χχ_64 is the EXACT ChiChi (Belkheyar et al., EUROCRYPT 2025, Def. 2/Thm. 4):
χ_31(bits 0–30) ∥ χ_33(bits 31–63) + λ corrections at indices 29–32.
Bijectivity: GF(2)-rank 64 for L(3,11), transpose perm, Beneš stages (fixed key);
LM5 inverse round-trip 2000/2000 (note: the design note's stated LM inverse
`L = R'⊕t` does NOT left-invert; corrected to `L_i = R_{i+1} ⊕ L_{i+1} ⊕ t_i`,
`R_i = L_{i+1} ⊕ t_i` — recorded here).

## Results

| Cand | S0 delay | S0 cells/area | xcheck 10k | RTL 300 | S2 (N=2^22, 115 deltas) | S1 | S3 | S4 | Q1 (sac_z5 / bic) | Verdict |
|------|----------|---------------|------------|---------|--------------------------|----|----|----|--------------------|---------|
| A | 27.1 | 5387 / 14391 | PASS | PASS 300/300 | KILL bit26, 147031 repeats, max\|z\|=2048 | — | — | — | — | S2-KILLED |
| B | 23.2 | 5750 / 17155 | PASS | PASS 300/300 | KILL bit26, 14521 repeats, max\|z\|=2048 | — | — | — | — | S2-KILLED |
| B2 | 16.9 | 1698 / 4934 | PASS | PASS 300/300 | KILL bit10, 2096880 repeats | — | — | — | — | S2-KILLED |
| C | 29.3 | 3796 / 10503 | PASS | PASS 300/300 | KILL bit10, 2097144 repeats | — | — | — | — | S2-KILLED |
| D | 21.7 | 2674 / 7401 | PASS | PASS 300/300 | KILL bit10, 2095350 repeats | — | — | — | — | S2-KILLED |
| E | 22.2 | 3810 / 10619 | PASS | PASS 300/300 | KILL bit10, 2096184 repeats | — | — | — | — | S2-KILLED |

## Failure analyses

(Every kill: (a) precise failing signal, (b) mechanistic hypothesis traced to the
construction, (c) targeted follow-up. Kills scoped to the tested construction;
recorded in [`../VERDICT_SCOPE.md`](../VERDICT_SCOPE.md).)

**Note on S2 inputs:** [`s2_diffprof.c`](../fast_battery/src/s2_diffprof.c) uses SEQUENTIAL x = 0..2^22-1 (not random).
This is realistic for a hash mixer (hashing 0,1,2,...) and the Feistel candidates
passed it, so the bar is achievable. The kills below are real, not harness artifacts.

### A — r22_wide_spn4_nw (4-round wide SPN): S2 KILL
(a) Signal: delta bit 26 (0x4000000), 147031 repeats (threshold 10), max|z|=2048.
    Output diff bit 0 is ALWAYS 0 (deterministic, probability-1 differential).
(b) Mechanism: S1's DDT is input-dependent. For sequential x < 2^22, high bits
    are zero, fixing the DDT controlling bits and making the S-box differential
    deterministic. 4 rounds of S-box + L(3,11) cannot avalanche from such
    structured inputs. With random 64-bit inputs the bias persists (|z|=128),
    confirming a real (not purely artifactual) weakness.
(c) Follow-up: 5-6 round SPN-5/6 (likely over the 37u budget), or add input
    whitening to break the sequential-input structure. The 27.1u delay is
    attractive but the differential structure needs more rounds.

### B — r22_em_chichi4_nw (EM over χχ+linear): S2 KILL
(a) Signal: delta bit 26, 14521 repeats, max|z|=2048. Output diff bit 6 is
    ALWAYS 1 (key-independent deterministic).
(b) Mechanism: Single-round χχ_64 has a deterministic differential for bit 26
    (→ 0x5000000) when input bits 25,27 are zero (true for x < 2^22). The χ
    nonlinear terms (~x_{i+1} & x_{i+2}) become linear when controlling bits are
    fixed. In EM mode the key cancels in differentials, so P's weakness is
    exposed directly. 4 rounds insufficient.
(c) Follow-up: More χχ rounds (8-10) or a stronger linear layer than L(3,11).
    The 23.2u delay leaves headroom, but χχ's input-dependent differentials are
    a fundamental concern for sequential inputs.

### B2 — r22_em_chichi6_rot_nw (EM, 6× rotl(χχ)): S2 KILL
(a) Signal: delta bit 10 (0x400), 2096880 repeats (~50% of samples). Input bit 10
    → output bit 27 with 42% probability after 6 rounds.
(b) Mechanism: 6 rounds of χχ + rotation is FUNDAMENTALLY insufficient.
    The max differential probability does not decay (0.26 → 0.43 → 0.23 →
    0.76 → 0.23 → 0.42 round-by-round). Random rotation schedules are equally
    bad (0.42), proving it's the primitive, not the schedule. χ's quadratic
    structure persists; Keccak uses 24 rounds for a reason.
(c) Follow-up: NOT VIABLE. Would need 12+ rounds (losing the 16.9u advantage).
    The "aggressive probe" hypothesis is falsified: χχ needs many more rounds.

### C — r22_keyed_spn6_nw (keyed SPN-6, transpose): S2 KILL
(a) Signal: delta bit 10, 2097144 repeats. Only 8 distinct 64-bit output diffs
    for 262144 sequential inputs (each appearing 32768×).
(b) Mechanism: The transpose permutation `(j+4b)%16` has 16 FIXED POINTS
    (bit 0 of every nibble never moves) and many 2-cycles (e.g., [10,42]).
    Differences get trapped in tiny orbits and never diffuse across the state.
    The "free" linear layer is fundamentally broken — not just weak, but
    non-diffusing for fixed-point bits. S1's DDT is normal; the linear layer
    is the culprit.
(c) Follow-up: Replace transpose with a validated P-box (no fixed points, long
    cycles) OR add a real linear diffusion layer. The 29.3u/6-round structure
    is sound; only the permutation is broken. Retest with fixed permutation.

### D — r22_lm5_chi_nw (5-round Lai–Massey): S2 KILL
(a) Signal: delta bit 10, 2095350 repeats. Only 1708 distinct diffs in 65536
    samples (top 2.7%).
(b) Mechanism: 5-round LM with chi32 F. The LM structure `(R^t, d)` where
    `d = L^R` provides limited diffusion per round. Combined with chi32's
    input-dependent differentials (deterministic for low inputs), 5 rounds
    cannot achieve avalanche. The design note flagged "high S2 risk" —
    confirmed.
(c) Follow-up: Stronger F (not just chi32) or more rounds. LM may be
    fundamentally unsuitable at this delay budget (21.7u is attractive but
    the structure doesn't diffuse). Consider Feistel instead.

### E — r22_benes_chichi_nw (Beneš-MUX + χχ): S2 KILL
(a) Signal: delta bit 10, 2096184 repeats. Only 48 distinct diffs in 65536
    samples (top 6.25%).
(b) Mechanism: The 11 Beneš MUX stages are DATA-LINEAR (just key-controlled
    wiring, a permutation). The only nonlinearity is 3 χχ applications.
    A permutation provides zero diffusion by itself; 3 χχ rounds are
    insufficient (see B2 analysis). The design note predicted "likely
    S2-failing" — confirmed. The MUX stages are cryptographically useless.
(c) Follow-up: NOT VIABLE as designed. Would need χχ after every stage
    (11 χχ, not 3), losing the delay advantage. The Beneš network adds
    complexity without security.

## Evidence locations

- Models: `round22/models/r22.py` (numpy reference; self-tests: chi_5/chi_7
  bijectivity, χχ_64 1M-sample, LM5 inverse 2000/2000, GF(2) ranks)
- Generator: `round22/gen_r22.py` (self-tests: DNF, S-box emission, lin(3,11) emission)
- Candidates: `fast_battery/candidates/r22_*/` (impl.c, rtl.v, model.py, meta.json)
- xcheck: `round22/xcheck/`; RTL checks: `round22/rtlcheck/`
- S0: `round22/s0/`; S1: `round22/s1/`; S2: `round22/s2_*.log`; Q1: `round22/q1/`

## O34 — r22b_keyed_spn6_pbox_nw (follow-up, HIGH re-test trigger): S2 KILL

**Candidate:** 6-round keyed SPN `x_{i+1} = P(S16(x_i ^ rk_i))`, S1 S-boxes, P-box
`P(i) = (5i+27) % 64` replacing the transpose. P-box validated by
`r22._selftest_pbox_o34`: permutation, zero fixed points, single 64-cycle,
per-nibble spread both directions, 2-round dep 16 bits/4 nibbles, 4-round full
64-bit diffusion, GF(2) rank 64. Chosen by exhaustive search over 2048 affine
maps (1080 satisfied spread + no-fixed-points + min-cycle ≥ 4; a=5/odd-b gives
the maximal single 64-cycle).

**Pipeline:** xcheck 10000/10000 PASS · RTL 300/300 PASS ·
S0 **27.7u** / 4174 cells / 11632 area (dual-analyzer agreement; below the
29.3u estimate — P-box is free wiring) · **S2 KILL** (delta bit 10 `0x400`,
140889 repeats > 10, max|z| = 705.0, low8_chi2 = 1232009.4). S1/S3/S4/Q1
skipped (no survivors). Evidence: [`s2_r22b_keyed_spn6_pbox_nw.log`](s2_r22b_keyed_spn6_pbox_nw.log),
[`xcheck/r22b_keyed_spn6_pbox_nw.log`](xcheck/r22b_keyed_spn6_pbox_nw.log), [`rtlcheck/r22b_keyed_spn6_pbox_nw.log`](rtlcheck/r22b_keyed_spn6_pbox_nw.log),
[`s0/r22b_keyed_spn6_pbox_nw.log`](s0/r22b_keyed_spn6_pbox_nw.log).

### Failure analysis
(a) **Signal:** S2 delta bit 10, 140889 repeats (threshold 10). max|z| = 705
(several output diff bits ~0.24–0.29 vs 0.5 null). **Control:** the same
cipher on random 64-bit inputs gives 3 repeats / 131k pairs (birthday-level) —
the cipher is sound; the pathology is specific to sequential inputs
`x = 0..2^22-1` (the S2 harness input, realistic for a hash mixer).

(b) **Mechanism — differential freezing (proven by instrumentation):**
For sequential x the high 42 bits are constant 0, so round-1 S-box nibbles 6–15
see constant inputs and produce constant outputs; the bit-permutation P
*relocates but does not mix* these constant bits across the state. The input
difference (bit 10, nibble 2) yields only 8 distinct round-1 differences
Δ1 = S1(v)^S1(v^4) (v = 16 values). At round 2 the 4 active S-boxes see
(din, w) *frozen* within each Δ1-group: din is fixed by Δ1, and the S-box
input value w is constant because P routes only frozen bits into w —
constant high-nibble bits, plus nibble-2 bits that coincide for v,v^4
(e.g. S1(14)[0] = S1(10)[0] = 1). Measured: **dx_2 takes exactly 1 distinct
value per 16384-pair Δ1-group** (8 values for 131072 pairs — a 14-bit entropy
collapse at round 2). Rounds 3–6 partially recover (114/1729/10829/15577
distinct per group) but 19% of pairs still collide at dx_6. 1997/2000 sampled
colliding groups already agree at round 1. **P-box search:** 60 affine + 15
random permutations (all with no fixed points / long cycles / spread) ALL
exhibit the freezing (min-distinct-dx_2 ∈ {1,2}, proxy repeats 871–130560).
The freezing is structural to the construction, not the P-box choice.

(c) **Follow-up / re-test trigger:** The bit-permutation cannot *create*
entropy, only relocate it; 4-bit S-boxes are too narrow to re-mix the
frozen/varying partition for sequential inputs. A fix requires a **bit-mixing**
(not just permuting) layer between S-box stages so S-box input values cannot
freeze — but it must cost < ~7u over 6 rounds to stay under the 37.0u
frontier, and must avoid candidate A's probability-1 differential flaw
(A died with random inputs too; O34 does not). Concrete hypothesis (untested):
`x_{i+1} = L(P(S(x_i ^ rk_i)))` with a cheap L (e.g. single-rotation XOR).
**Scoped verdict:** kills "6-round keyed SPN with 4-bit S1 S-boxes +
bit-permutation P-box" for the S2 sequential-input requirement. Does NOT kill:
SPNs with mixing linear layers, other S-boxes, Feistel constructions, or the
P-box primitive elsewhere. (Compare: candidate A failed S2 with a *real*
probability-1 differential persisting on random inputs; O34's cipher is
sound on random inputs — different failure class.)

## O38 — SPN with bit-mixing layer (follow-up, HIGH re-test trigger from O37): 2/4 S2-PASS

**Hypothesis:** O37's differential freezing (permutation relocates but never mixes)
requires a bit-*mixing* layer between S-box stages: `x_{i+1} = MIX(P(S16(x_i ^ rk_i)))`.

**Analytical kill (before synthesis):** the brief's proposed `MIX(x) = x ^ rotl64(x,R)`
is GF(2)-SINGULAR — rank 63, kernel `{0, 0xFFFF...F}` (any `x^P(x)` has the
all-ones vector in its kernel since a permutation fixes the all-ones vector).
It gives a probability-1 differential on delta `0xFFFF...F` and violates the
bijectivity hard gate. **Killed analytically, never synthesized.**
Proven by `r22._selftest_o38_singularity` (asserts rank 63). The cheapest
bijective mixers are then: (a) 3-term rotation XOR (~4u/round, = lin(3,11));
(b) triangular shift-XOR `y = x ^ ((x >> r) & MASK)` — bijective for any mask
by back-substitution, single XOR2 ~= 2u/round, alternate directions per round.

**Candidates** (P = O37 validated P-box; [`r22.py`](models/r22.py): `r22c_*`; generator: [`gen_r22.py`](gen_r22.py)):

| Cand | Construction | S0 | xcheck | RTL | S2 (N=2^22, 115 deltas) | Verdict |
|------|--------------|----|--------|-----|--------------------------|---------|
| V0 `r22c_spn_mix4r_lp_nw` | 4r, `L(P(S(x^rk)))`, L=lin(3,11) | 28.3u / 4656 / 12949 | PASS 10k | PASS 300/300 | PASS, max\|z\|=13.6, 0 repeats | **FULL BATTERY PASS** |
| V1 `r22c_spn_mix5r_lp_nw` | 5r, `L(P(S(x^rk)))`, L=lin(3,11) | 34.5u / 7144 / 19253 | PASS 10k | PASS 300/300 | PASS, max\|z\|=4.3, 0 repeats | S2-PASS, S1 CAL_PASS (dominated by V0; S3/S4/Q1 not run) |
| V2 `r22c_spn_mix6r_lp_nw` | 6r, `L(P(S(x^rk)))` | 40.5u / 9187 / 24483 | PASS 10k | PASS 300/300 | TERMINATED by coordinator (load; 40.5u delay-dominated) | — |
| V3 `r22c_spn_mix5r_shx_nw` | 5r, `SHX(P(S(x^rk)))`, SHX=triangular shift-XOR alt. dir. | 29.0u / 4637 / 12890 | PASS 10k | PASS 300/300 | KILL bit7 (0x80), 190 repeats, max\|z\|=183 | S2-KILLED |

### Failure analyses
(a) **V3 signal:** S2 delta bit 7, 190 repeats (threshold 10); max|z| = 183, with
|z| = 79–183 elevated across MANY deltas (systematic, not one bad trail).
(b) **Mechanism:** the triangular shift-XOR mixes each bit with only ONE other
bit per round, and the triangular structure leaves r bits unmixed per round
(top r pass through on right-shifts). Even alternating directions, 5 rounds
cannot avalanche differentials — systematic under-diffusion. The ~2u/round
"cheap bijective mixer" is too weak; dense mixing (lin 3,11) is required.
**Scoped verdict:** kills "triangular shift-XOR as SPN mixing layer at 5r".
Does NOT kill: shift-XOR in other roles (e.g. inside Feistel F where
bijectivity is not required and weakness is tolerable).
(c) **V0/V1 positive analysis:** the P-box is LOAD-BEARING at 4r. Candidate A
(identical S-box + lin(3,11) + key schedule + 4 rounds, WITHOUT the P-box) died
at S2 with a deterministic differential (bit26, 147031 repeats, |z|=2048).
V0 adds only the (free-wiring) P-box and passes cleanly (max|z|=13.6).
Mechanism: L∘P is a different linear layer than L; the P-box breaks the
specific deterministic trail that killed A. V1 (5r) is cleaner still
(max|z|=4.3) — monotonic improvement with rounds, as expected.
**Both V0 (28.3u) and V1 (34.5u) are below the 37.0u Frontier-S speed point.**
### V0 full battery — PASS (all gates)
- S1: CAL_PASS (LIN rej=0, DIFF rej=0, marginal PB rej=0 RD rej=0)
- S2: PASS (115/115 deltas, max|z|=13.6, max repeats=1)
- S3: PASS PractRand 1GB x2 configs (standard key=0x123456789abcdef0 stride=1;
  strided key=0x0 stride=0x9E3779B97F4A7C15) — no FAIL at any stage
- S4: PASS SmallCrush (all 15 tests)
- Q1: sac_z5=0, bic_maxcorr=0.00865, avalanche_mean=31.9998 (no BIC blemish —
  the SPN's final mixing layer leaves no unmixed chi)
**V0 at 28.3u is 8.4u under the current Frontier-S speed point (36.7u).**
[PARETO.md](../PARETO.md) NOT edited (parent verifies from raw logs first).

### Bugs caught
- `_v_shxor_stmts` emitted `x = t ^ ({13{1'b0}}, t[63:13])` (parens, not a
concatenation) — iverilog syntax error. Fixed to `{{13{1'b0}}, t[63:13]}` (double
braces: outer concatenation + inner replication). `_selftest_shxor_emission`
now asserts brace balance + concatenation shape (the arithmetic self-test
alone was insufficient — same escape class as the round-22 DNF bug).
- The O38 no-freeze proxy's first threshold (>1000 distinct dx_2) was
miscalibrated: healthy S2 behavior gives ~16 DDT-groups × 4–8 DDT-row values
≈ 76, not thousands. Recalibrated to a per-D1-group test (frozen ⟺ exactly 1
distinct dx_2 per group; r22b/O37 gives all-1s → fires; LP gives 4–16, SHX
2–8 → pass). Lesson: calibrate a proxy against a KNOWN-BAD reference (r22b)
before trusting its threshold.

### Evidence
- Models: `round22/models/r22.py` (`r22c_*`, `_selftest_o38_*`; `__main__`
fixed — it called nonexistent `_selftest_chichi4_bijection`)
- Generator: `round22/gen_r22.py` (SPECS/C_BODIES/`_v_shxor_stmts`/branches)
- Candidates: `fast_battery/candidates/r22c_*/`
- Logs: `round22/xcheck/`, `round22/rtlcheck/`, `round22/s0/`,
`s2_r22c_*.log`, [`s1_r22c_spn_mix4r_lp_nw.log`](s1_r22c_spn_mix4r_lp_nw.log), `round22/run_o38.sh`,
`round22/progress_o38.log`
