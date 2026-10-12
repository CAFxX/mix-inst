# Design C (bit-Feistel) — Results

**Verdict: TERMINAL — Fisher-catastrophic (O151).** Recorded in
[VERDICT_SCOPE.md](../../VERDICT_SCOPE.md) as **O151** (the task brief said
O150, but O150 was already claimed by the firstprin d2 lane at write time —
claiming it would duplicate a verdict ID).

## 1. The design (as built)

[boolfunc_c.v](boolfunc_c.v) — 64-bit in/out, parameters `A,B,C,D` (defaults
1,3,5,7). Split L=`din[63:32]`, R=`din[31:0]`; F is the 2-level AND-XOR
network `F(L)[i] = (L[(i+A)&31] & L[(i+B)&31]) ^ (L[(i+C)&31] & L[(i+D)&31])`.

**⚠️ Brief contradiction (root-caused, not worked around).** The brief's
*literal* round formulas `(L0,R0) → (R0, R0⊕F(L0))` are **not bijective**:
F's input half L0 never reaches the output (with F=0 the map is
`(L0,R0) → (R0,R0)`, erasing L0). The brief's *prose* ("L'=L, R'=R⊕F(L),
then swap L/R for next round") is the correct Feistel round
`(L,R) → (R⊕F(L), L)`, bijective for arbitrary F by the standard argument
(the F-input half is passed through, so inversion recovers it first).
Built the prose version:

- Round 1: `(L1,R1) = (R0⊕F(L0), L0)`
- Round 2: `(L2,R2) = (R1⊕F(L1), L1) = (L0⊕F(R0⊕F(L0)), R0⊕F(L0))`
- `dout = {L2, R2}`

This also invalidates the brief's ~7.0u estimate, which was computed on the
non-bijective wiring. The bijective 2-round critical path with XOR2 cells
would be AND(1.5)+XOR(2.0)+XOR(2.0)+AND(1.5)+XOR(2.0)+XOR(2.0) = 11.0u —
see §3 for what synthesis actually measured.

## 2. Bijectivity — brute-forced, not assumed

[c_model.py](c_model.py) implements a bit-exact scalar model (half-width
parameterized) and a vectorized numpy model for the 64-bit instance.

- **n=8 (4+4 split), exhaustive over all 256 inputs**: 0 collisions, 256
  distinct outputs — for the three brief offset sets reduced mod 4
  ((1,3,5,7), (1,5,9,13), (3,7,11,15)) **and** two arbitrary sanity sets.
  **BIJECTIVE.**
- The brief's *literal* formulas fail the same check: as few as 16 distinct
  outputs of 256 (offsets where F≡0 mod 4), 28 and 196 for the sanity sets.
  **NOT bijective** — evidence, not opinion.
- Vectorized model vs scalar model: 0/4096 mismatches on random 64-bit
  vectors (all three offset sets).
- Verilog↔model: no simulator on the VM (iverilog absent; yosys `sim` has a
  stimulus-propagation quirk that freezes combinational outputs — confirmed
  on a trivial passthrough, so it's a tool artifact, not a design bug).
  Cross-checked instead by inspecting the yosys-elaborated netlist
  (`elab_c.v`): `L1 = R0^F0`, `R1 = L0`, `L2 = L0^F1`, `R2 = L1`, with F0's
  ANDs tapping `din[63:32]` and F1's tapping `L1` — exactly the Ψ wiring;
  the isolated F function sims correctly (F(0)=0, F(2³²−1)=0 as specified).

## 3. S0 — measured, not estimated

`run_synth.py` ([exploration/run_synth.py](../../run_synth.py), pinned yosys
0.69, `mini.genlib`, dual-analyzer XCHECK) under `nice -n 19`, backoff-gated:

```
RESULT name=boolfunc_c cells=660 area=1632 crit=9.2 delay_ratio=0.089 area_ratio=0.046 ref_crit=103.5 ref_area=35323
XCHECK: analyze.py == analyze2.py (cells/area/crit identical)
```

- **crit = 9.2u ≤ 10u → cost gate PASSED** (not KILLED-COST).
- Why below the 11.0u hand estimate: ABC does not use XOR2 (2.0u) cells —
  the mapped netlist ([s0_work/boolfunc_c/_dut/mapped_boolfunc_c.v](s0_work/boolfunc_c/_dut/mapped_boolfunc_c.v))
  implements the XORs with NAND2/NOR2/AOI21 (1.5u) cells. The 11.0u figure
  assumed XOR2 everywhere; the project's own S0 methodology (ABC-mapped
  topological critical path, cross-checked by two analyzers) says 9.2u.
- Full log: [s0_boolfunc_c.log](s0_boolfunc_c.log); runner
  [run_s0_c.sh](run_s0_c.sh).

## 4. Avalanche proxy (offset selection)

[c_avalanche.py](c_avalanche.py) — 1024 random inputs × all 64 single-bit
flips, mean output bits flipped per input-bit flip:

| offsets | mean flipped / 64 |
|---|---|
| (1,3,5,7) | 4.20 |
| (1,5,9,13) | 4.21 |
| (3,7,11,15) | 4.21 |

The three sets are statistically tied (the 0.8% "win" of (1,5,9,13) is
noise); diffusion is poor in all cases — ≈4 bits vs the ~32 ideal. Two
rounds of a 4-input F cannot spread further. Fisher ran on (1,5,9,13).

## 5. Fisher triage — verbatim screen, REJECT

[c_fisher.py](c_fisher.py) uses `lin_diff.screen_lin_diff` verbatim
([fast_battery/src/lin_diff.py](../../fast_battery/src/lin_diff.py)),
N=2^18 sequential inputs, unkeyed design → single dummy key:

```
[LIN]  key=0x0 D=4096/4096 logp=-inf
[DIFF] key=0x0 worst|z|=1480000.0 fisher_logp=-inf
LIN: FLAG (rej=1)   DIFF: FLAG (rej=1)
TRIAGE: REJECT
```

**Mechanism (structural — holds for ANY F, verified empirically):**
for sequential inputs x < 2^18, L0 ≡ 0, so R2 = R0⊕F(0) = x⊕c:

- **LIN**: output columns 18..31 are constant across every 64-output block
  (x's bits 18..31 are zero for x<2^18) → GF(2)-rank ≤ 50 < 61 in *every*
  block → D=4096/4096. Confirmed: columns 18..31 constant over 64
  sequential outputs in the model.
- **DIFF**: the low-32 output difference for input delta 2^k (k<8) is
  deterministically 2^k (the F terms cancel: (x⊕c)⊕(x⊕2^k⊕c) = 2^k) →
  low-8 chi2 astronomically off. Confirmed: low-8 diff for delta=1 is
  exactly 0x1 on all pairs.

The brief's prescribed remedy ("3rd AND term in F, +1.5u") **cannot help**:
both failures are F-independent — no F, however strong, changes R2=x⊕c on
sequential inputs. It would also break the cost budget (9.2u + ~2–3u for
the extra XOR level in F, twice on the critical path, > 10u).

## 6. Verdict

- **O151 — TERMINAL (Fisher-catastrophic, structural).** The unkeyed 2-round
  bit-Feistel cannot pass the sequential-input LIN/DIFF screens for any F:
  one output half is (input half ⊕ constant) on sequential inputs, and a
  thin F leaves the other half near-static too. A 3rd round would break the
  constant-columns structure but costs ≈14u — the <10u budget and the
  diffusion requirement are jointly unsatisfiable in this construction.
- Re-test triggers (narrow, LOW priority): keyed F with F(L0) non-constant
  over sequential inputs, or ≥3 rounds (both surrender the cost edge), or a
  non-Feistel 6-level form (Design B territory).
- No escalation (Fisher did not pass).

## Artifacts

- [boolfunc_c.v](boolfunc_c.v) — the Verilog (bijective Feistel wiring)
- [c_model.py](c_model.py) — scalar + vectorized Python models, bijectivity
  brute force, self-check
- [c_avalanche.py](c_avalanche.py) — avalanche proxy
- [c_fisher.py](c_fisher.py) — verbatim Fisher triage driver
- [run_s0_c.sh](run_s0_c.sh) / [s0_boolfunc_c.log](s0_boolfunc_c.log) —
  backoff-gated S0 runner and log
- [s0_work/boolfunc_c/](s0_work/boolfunc_c/) — synth workdir (mapped netlist)
- [DESIGN.md](DESIGN.md) — track analysis (unchanged by this lane)
