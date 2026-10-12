# Direction 1: Input-dependent MUX routing (d1_muxroute)

**Goal**: a sub-10u stage (target <4u/stage, 2 stages <8u) whose MUX *select* bits are
nonlinear functions of the input — routing, not data, carries the nonlinearity.
Fisher-triaged with [`lin_diff.screen_lin_diff`](../../../fast_battery/src/lin_diff.py) verbatim if the delay gate passes.

## 1. Delay model (from [synth/mini.genlib](../../../../synth/mini.genlib); analyzer unit u = PIN delay)

| Gate | genlib delay | u |
|---|---|---|
| INV/BUF | 1 | 0.5 |
| NAND2/NOR2 | 2 | 1.0 |
| AND2/OR2/AOI21/OAI21 | 3 | 1.5 |
| XOR2/XNOR2/**MUX2** | 4 | **2.0** |
| AND4/OR4 | 5 | 2.5 |

Critical fact: **a 4:1 MUX is 2 MUX2 levels = 4.0u on the data path alone**
(ABC: 3× MUX2 tree, or AND3/AND4+OR4 at ~4.5u — the tree wins).
Any *computed* select adds its own delay before the mux resolves, so a 4:1 MUX
with input-dependent select costs **≥ 5.5u/stage** — the task's literal
"64 parallel 4:1 MUXes, <4u/stage" is unachievable as specified
(measured in §5: D1-A). **Correction: the viable base is the 2:1 MUX (2.0u)
with a single-gate select (≤1.5u) → 3.5u/stage.** 8:1 is strictly worse
(3 MUX2 levels = 6.0u data path) and is not built.

Select-complexity ladder (2:1 MUX base, delay = select + 2.0u):

| ID | select s[j] | select delay | stage (predicted) | bias P(s=1) | E[flips]/bit/stage |
|---|---|---|---|---|---|
| D1-A | `(a&b)^c^k` (task's literal formula, 4:1 MUX) | 5.5u | ~9.5u | 1/2 | — (over budget) |
| D1-B | `a^b^(c&k)` (task's fallback, 2:1 MUX) | 4.0u | ~6.0u | 1/2 | — (over budget) |
| D1-C | `(a&b)^c` (2:1) | 3.5u | ~5.5u | 1/2 | — (over budget) |
| D1-D | `a&b` (2:1) | 1.5u | **~3.5u** | 1/4 | 1.500 |
| D1-E | `(a&b)\|(c&d)` = NAND(NAND(a,b),NAND(c,d)) (2:1) | 2.0u | ~4.0u | 7/16 | 1.750 |
| D1-F | `a^b` linear control (2:1) | 2.0u | ~4.0u | 1/2 | 2.000 (linear) |
| D1-G | `a\|b` (2:1) | 1.5u | ~3.5u | 3/4 | 1.500 |
| D1-H | `~((a&b)\|c)` AOI21 (2:1) | 1.5u | **~3.5u** | 3/8 | **1.625** |

Only D1-D / D1-G / D1-H are predicted **<4u** (D1-H has the best confusion growth
of the three: 1.625×/stage, verified by exhaustive truth-table over all
single-gate selects — AND2/OR2/NAND2/NOR2 all 1.500, AND3 1.375, XOR2 2.000 but
linear). Every balanced nonlinear select needs an XOR (2.0u) on top of an AND
(1.5u) = 3.5u select → ≥5.5u stage. The genlib proves it: single-gate selects are
exactly {biased nonlinear} ∪ {linear}; balanced + nonlinear needs ≥2 gates.

## 2. Wiring (D1-D, the <4u candidate)

Stage: 64 × MUX2. `y[j] = s[j] ? d0[j] : d1[j]`, all taps shift-wirings:

- Stage 1: `d0[j]=x[(j+5)%64]`, `d1[j]=x[(j+37)%64]`,
  `s[j]=x[(j+13)%64] & x[(j+51)%64]`
- Stage 2: `d0[j]=x[(j+11)%64]`, `d1[j]=x[(j+29)%64]`,
  `s[j]=x[(j+3)%64] & x[(j+43)%64]`

Tap sets {5,37,13,51} / {11,29,3,43} are pairwise distinct mod 64 and spread across
word quarters — select inputs live in different regions than data inputs, per the
task's "different input regions" requirement. Keying for Fisher follows the
v3 convention (`x = V^K` in, `S = x ^ rotl(K,13)` out); the pure stage carries no
key XOR because a 2.0u key XOR would break the 4u budget on its own.

## 3. Influence propagation trace: how do 6 bits reach 32 outputs?

Take 6 consecutive input bits B = {0,…,5}.

**Stage 1 — topological.** Each MUX has 4 input slots (2 data + 2 select).
Bit *i* touches: MUX `i−5` (as d0), MUX `i−37` (as d1), MUX `i−13` and `i−51`
(as the two AND inputs of s). The four shifts are distinct mod 64, so the 6 bits
touch 4 disjoint sets of 6 MUXes = **24 distinct stage-1 outputs**. (24 < 32:
one stage provably cannot do 6→32 — max distinct outputs is 24.)

**Stage 2 — topological.** Each of the 24 touched stage-1 bits feeds 4 stage-2
slots → up to 96 distinct stage-2 outputs. 6→32 is topologically reachable in
2 stages.

**LIN-kill mechanism (measured, bit-exact model).** Fisher LIN builds 64×64 matrices
from 64 *consecutive* outputs and flags rank ≤ 61 (null P=0.005285). Consecutive
inputs V..V+63 vary only input bits 0..6, so an output bit varies across the block
only if its dependency cone hits those bits. Measured fraction of output bits
CONSTANT across a 64-block (200 blocks): **D: 0.906, H: 0.794**. ~51–58 constant
columns → matrix rank ≤ ~13 ≪ 61 on essentially every block → LIN D≈4096/4096,
FLAG. This is the same structural disease as O148's V3 (54/64 constant there) —
narrow per-output cones, now quantified for input-dependent selects.

**Avalanche counting bound (predicted, then measured).** Per input bit per stage
(D1-D, P(s=1)=1/4). Not every touch flips the output:

- d0 slot: output flips iff select currently chooses d0 → w.p. **1/4**
- d1 slot: output flips iff select chooses d1 → w.p. **3/4**
- each select-AND slot: s flips iff the *other* AND input is 1 (w.p. 1/2), then
  the MUX output flips iff d0≠d1 (w.p. 1/2) → **1/4** per slot × 2 slots

E[flipped stage-1 outputs per flipped input bit] = 1/4 + 3/4 + 1/4 + 1/4 = **1.5×**.
Two stages: 1.5² = **2.25×** per input bit (measured 2.053 — slight
sub-multiplicativity from cone overlap). The strongest <4u select (D1-H, AOI21)
reaches 1.625×/stage → 2.64× over two stages (measured 2.514). Fisher LIN feeds 64
consecutive input pairs; an increment flips ~2 input bits on average →
E[output flips] ≈ **5** against **32** needed for bit-balance. Single-bit deltas:
2.5 vs 32 — a ~13× structural shortfall even in the best case. **No wiring
pattern changes this: 4–5 slots/bit is the maximum for a 2:1-MUX stage (slot
conservation), and the propagation probabilities are forced by the select's
truth table.** A third stage gives ~4× but costs 3×3.5 = 10.5u > 10u.
The bound is tight and budget-incompatible.

**The sharing fallacy (task's §"Influence analysis" corrected).** The task suggests
"one input bit changing s0 for 8 MUXes = 8 outputs affected" via *shared* selects.
Sharing concentrates slots, it does not create them: 8 shared selects = 16 select
slots + 128 data slots = 144 total vs 256 unshared; E[flips] = (16×2 + 48×1)/64
= **1.25×/stage — worse** than unshared 1.5×. Fanout via sharing is an illusion;
what matters is total input slots per stage.

**Ceiling over the whole ladder** (truth-table-exhaustive over single-gate selects).
The best confusion growth in the table is D1-F (linear XOR select): **2.0×/stage**
(XOR select always flips s, then data differ w.p. 1/2) → 4× over 2 stages, still
≪32, and the stage is linear-select (degree-2 overall — O148's V3 showed
linear-select MUX networks fail LIN catastrophically). Best *nonlinear* at ≤4u:
D1-E (NAND-NAND, 1.750×, but the stage is 4.0u — exactly at target, not under);
best nonlinear *<4u*: D1-H (AOI21, 1.625× @ 3.5u). Measured 2-stage avalanches:
D 2.053, H 2.514 bits/delta vs ~32 needed.

## 4. What would falsify this

- A ≤2u nonlinear gate with >2×/stage confusion growth (O148's re-test trigger —
  the genlib says single-gate selects cap at 1.625× (AOI21), XOR-select at 2.0× but linear).
- A feedthrough mechanism costing <1u (O148's other trigger).
- A sub-4u stage with >4 input slots per output (wider-than-MUX2 nonlinear gate
  at MUX2-like delay — not in the genlib).

## 5. Build & measurement plan

1. [gen_d1.py](gen_d1.py) emits one Verilog per ladder ID (single stage) + 2-stage D1-D/D1-H.
2. [run_synth.py](../../../run_synth.py) per variant (nice -n 19) — never invent S0 numbers.
3. If best <4u: 2-stage S0 (target <8u). If total <10u: [d1_fisher.py](d1_fisher.py)
   (`screen_lin_diff` verbatim, 10 keys, N=2^18) + mean-avalanche diagnostic.
4. Verdict → [VERDICT_SCOPE.md](../../../VERDICT_SCOPE.md) as O154 (claimed at write
   time after re-reading the ledger; O153 was max).
