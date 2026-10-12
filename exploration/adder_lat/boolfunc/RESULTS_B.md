# Design B (bipartite thin-Toffoli, E+O stages) — Results

**Verdict: TERMINAL — Fisher-catastrophic (O153).** Recorded in
[VERDICT_SCOPE.md](../../VERDICT_SCOPE.md) as **O153** (the task brief said
O149, but O149/O150/O151/O152 were all claimed by other lanes by write time —
per the standing rule the ledger is the numbering authority, so the next free
number is O153).

## 1. The design (as built)

[boolfunc_b.v](boolfunc_b.v) — 64-bit in/out, odd offsets `a,b` (defaults 1,3).
Bipartite alternating-parity thin-Toffoli, E+O = 2 stages:

- Stage E (even targets, odd controls frozen):
  `e[2i] = in[2i] XOR (in[(2i+a)%64] AND in[(2i+b)%64])`, `e[2i+1] = in[2i+1]`
- Stage O (odd targets, even controls frozen): mirror image.

Each stage is 32 disjoint Toffolis with frozen controls → each stage is a
genuine involution → the composition is bijective (no brute force needed for
the argument, but §2 checks it anyway).

## 2. Bijectivity — brute-forced, not assumed

[verify_bij.py](verify_bij.py) — scalar bit-array reference vs vectorized
numpy model (`design_b_vec`, the same model the Fisher screen uses):

| offsets | n=8 exhaustive (256 in) | scalar==vec | n=64 sequential 2^18 distinct |
|---|---|---|---|
| (1,3) | 0 collisions | yes | yes |
| (1,7) | 0 collisions | yes | yes |
| (3,11)→(3,3) mod 8 | 0 collisions | yes | yes |

**BIJECTIVITY: PASS.** (Run 2026-10-12, `nice -n 10`.)

## 3. S0 — measured, not estimated

`run_synth.py` ([exploration/run_synth.py](../../run_synth.py), pinned yosys
0.69, `mini.genlib`, dual-analyzer XCHECK), backoff-gated via
[run_all_b.sh](run_all_b.sh) (cleared-flag single-gate pattern):

```
RESULT name=boolfunc_b_13  cells=224 area=512 crit=6.2 delay_ratio=0.060 ref_crit=103.5
RESULT name=boolfunc_b_17  cells=224 area=512 crit=6.2 delay_ratio=0.060 ref_crit=103.5
RESULT name=boolfunc_b_311 cells=224 area=512 crit=6.2 delay_ratio=0.060 ref_crit=103.5
XCHECK: analyze.py == analyze2.py (cells/area/crit identical)  # all three
```

- **crit = 6.2u ≤ 10u → cost gate PASSED** (not KILLED-COST). All three
  offsets synthesize identically (offset is pure wiring).
- Full log: [run_all.log](run_all.log); workdirs
  [synth_boolfunc_b_13/](synth_boolfunc_b_13/),
  [synth_boolfunc_b_17/](synth_boolfunc_b_17/),
  [synth_boolfunc_b_311/](synth_boolfunc_b_311/).

## 4. Avalanche proxy (offset selection)

[screen_b_large.py](screen_b_large.py) — 4096 random 64-bit inputs × all 64
single-bit flips, mean/min output bits flipped per input-bit flip:

| offsets | mean flipped / 64 | min / 64 |
|---|---|---|
| (1,3) | 0.0381 (~2.4 bits) | 0.0308 (~2.0 bits) |
| (1,7) | 0.0381 | 0.0310 |
| (3,11) | 0.0380 | 0.0309 |
| (1,33) | 0.0351 | 0.0308 |
| (3,35) | 0.0351 | 0.0309 |

Diffusion is weak in all cases (~2.4 bits vs the ~32 ideal) and **flat across
offsets** — tap geometry is not the lever (same lesson as O141/O150: the
avalanche count is set by the AND-gate count per bit, not the tap distance).

⚠️ **Bug note (recorded, not worked around):** [screen_b.py](screen_b.py)'s
`popcount_vec` loops `range(6)` despite its "64 bits" comment — it counts
only the low 6 bits of each output difference, so its avalanche numbers are
wrong (understated ~10×). [screen_b_large.py](screen_b_large.py) counts all
64 bits; the table above is the corrected measurement. The bug does not
affect any Fisher result (Fisher never uses the proxy).

## 5. Constant-column diagnostic (the high-bit question)

Output columns constant over the full N=2^18 sequential stream
(`x = V ^ key`, V = 0..2^18−1), first 3 keys — [screen_b_large.py](screen_b_large.py):

| offsets | const cols (keys 0..2) | varying |
|---|---|---|
| (1,3) | 45, 43, 42 | 19, 21, 22 |
| (1,7) | 45, 39, 36 | 19, 25, 28 |
| (3,11) | 42, 34, 30 | 22, 30, 34 |
| (1,33) | 46, 27, 27 | 18, 37, 37 |
| (3,35) | 46, 24, 23 | 18, 40, 41 |

Large offsets do pull more columns into variation over the *full* sequence
(via wrap-around AND paths), but the count is key-dependent (key 0: the AND
gates see constant-0 and contribute nothing) and — critically — the LIN
screen does not test the full sequence. It tests **64-output blocks**, and
within a block only input bits 0..5 vary (see §7).

## 6. Fisher triage — verbatim screen, REJECT on all offsets

`lin_diff.screen_lin_diff` verbatim
([fast_battery/src/lin_diff.py](../../fast_battery/src/lin_diff.py)),
N=2^18 sequential inputs, 10 keys (`KEYS` from
[exploration/screen_lib.py](../../screen_lib.py)):

```
FISHER(1,3):  KILL lin=FLAG diff=FLAG nrej=20
FISHER(1,7):  KILL lin=FLAG diff=FLAG nrej=20
FISHER(3,11): KILL lin=FLAG diff=FLAG nrej=20
FISHER(1,33): KILL lin=FLAG diff=FLAG nrej=20
FISHER(3,35): KILL lin=FLAG diff=FLAG nrej=20
```

nrej=20 = all 10 keys rejected in **both** families. Full log:
[screen_b_large.log](screen_b_large.log) (run under `nice -n 10`).

**Independent cross-check:** the [run_all_b.sh](run_all_b.sh) runner's own
[screen_b.py](screen_b.py) Fisher run on the canonical (1,3) agrees:
`LIN: FLAG (rej=10)  DIFF: FLAG (rej=10)` — see [run_all.log](run_all.log).

## 7. Mechanism — why the large offsets don't save it

The brief's hypothesis was: small offsets fail because high-bit targets use
high-bit controls (constant under sequential inputs), and large odd offsets
(1,33), (3,35) fix this because the wrap-around puts *varying* low bits in
the control positions. **The hypothesis is refuted — and its arithmetic was
wrong in the first place:** for offsets (1,33), even target 60's Stage-E
controls are bits 61 and (60+33)%64=**29**, and bit 29 does *not* vary under
sequential inputs (only bits 0..17 do). The wrap-around does not deliver what
was claimed.

The actual mechanism, worked through the backward cone
([screen_b_large.py](screen_b_large.py) documents the counting argument;
empirical §5/§6 confirm it):

1. The LIN screen computes GF(2) rank per **block of 64 consecutive outputs**
   and needs rank ≥ 61. Within one block only input bits **0..5** vary
   (bits 6..63 are constant across the block).
2. Design B's per-block varying output columns are: the XOR backbone
   (`out[p]` always flips with `in[p]` → 6 columns, p < 6) plus a handful of
   **key-gated** AND wrap-around columns — e.g. for (1,33): even
   {32,34,36} vary iff key bits 33/35/37 = 1, odd {63} iff key bit 33 = 1;
   for (3,35): even {30,32,34,62}, odd {61,63}, each key-gated. Each
   wrap-around AND needs its *constant* input to be key-bit 1 to carry the
   varying signal, and each covers only O(1) outputs.
3. Maximum per-block varying columns ≈ 12 (typically fewer — key 0 gives
   exactly the 6 backbone columns) → GF(2) rank ≤ ~12 << 61 → **LIN FLAG on
   every key, for every offset**. The DIFF screen fails alongside (nrej=20
   includes 10 DIFF rejections per offset).

So [DESIGN.md](DESIGN.md)'s influence-~18 analysis was **not too
pessimistic** — if anything it was optimistic about what wider taps buy.
The binding constraint is not the influence *radius* (large offsets do wrap
around the ring) but the **per-block varying-input bottleneck**: with only
6 input bits varying per LIN block, no offset choice in this 2-stage,
2-level-AND construction can make 61 output columns vary. This is the same
failure class as O149's "LIN affine degeneration" (blocks vary only bits
0..5; measured rank 6–7 across 1–4 MUX2 stages).

## 8. Verdict

- **O153 — TERMINAL (Fisher-catastrophic, structural).** The 2-stage
  bipartite thin-Toffoli passes the cost gate (6.2u) and is genuinely
  bijective, but fails the Fisher LIN+DIFF screens on all 10 keys for all
  five offset sets tested — small (1,3), (1,7), (3,11) and large (1,33),
  (3,35). The kill mechanism (§7) is offset-independent: the per-block
  varying-column ceiling (~12 < 61) holds for any odd (a,b).
- **No escalation** (no offset passed Fisher).
- Re-test triggers (narrow, LOW priority): ≥3 stages (breaks the <10u
  budget — nominal 10.5u, and the per-block bottleneck persists structurally);
  a construction delivering ≥61 varying output columns per 64-block within
  the budget (needs degree/growth the 2-level AND-XOR cannot supply —
  cf. O149's counting bound).
- Note for sibling lanes: the O152 lead (partitioned C1/C2 NAND4-Toffoli)
  should be evaluated against this same per-block column-count bound before
  any Fisher run — if its per-block varying columns can't reach 61 by
  construction, screening it is burning compute.

## Artifacts

- [boolfunc_b.v](boolfunc_b.v) — the Verilog (E+O bipartite thin-Toffoli)
- [verify_bij.py](verify_bij.py) — bijectivity brute force + model self-check
- [screen_b.py](screen_b.py) — original triage (avalanche proxy has the
  6-bit popcount bug noted in §4; its Fisher run is valid and agrees)
- [screen_b_large.py](screen_b_large.py) / [screen_b_large.log](screen_b_large.log) —
  corrected proxy + constant-column diagnostic + full 5-offset Fisher triage
- [run_all_b.sh](run_all_b.sh) / [run_all.log](run_all.log) — backoff-gated
  S0 runner (all three offsets 6.2u) + independent (1,3) Fisher confirmation
- [synth_boolfunc_b_13/](synth_boolfunc_b_13/),
  [synth_boolfunc_b_17/](synth_boolfunc_b_17/),
  [synth_boolfunc_b_311/](synth_boolfunc_b_311/) — synth workdirs
- [DESIGN.md](DESIGN.md) — track analysis (unchanged by this lane)
