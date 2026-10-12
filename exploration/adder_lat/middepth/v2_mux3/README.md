# V2: 3-stage MUXD (fresh rotations) — COST-CLOSED (O145)

**Verdict: KILL on cost.** No MUXD stage form fits ≤3.3u/stage; best-case full 3-stage = 11.8u S0 (>10u strict).
Killed before Fisher screening per DESIGN.md escalation rule 2.

## S0 measurements (run_synth.py, ref mul64 = 103.5u, analyze.py == analyze2.py XCHECK)

| Design | File | crit | cells | area |
|---|---|---|---|---|
| 1× MUXD stage `y = x^g^rotl(x,d)` | [muxd1_stage.v](muxd1_stage.v) | **4.0u** | 192 | 768 |
| 1× compressed stage `y = x^g` (no d) | [muxd1_stage_nod.v](muxd1_stage_nod.v) | **4.0u** | 128 | 512 |
| 3-stage, compressed, fresh rots | [muxd3_nod.v](muxd3_nod.v) | **11.8u** | 2012 | 5589 |

Logs: [s0_stage.log](s0_stage.log), [s0_nod.log](s0_nod.log), [s0_3stage.log](s0_3stage.log).
Mapped netlists: `s0_stage/_dut/`, `s0_nod/_dut/`, `s0_3stage/_dut/`.

## Root cause (netlist-verified)

Per output bit the stage maps to **MUX2 (2.0u) → XOR2 (2.0u) = 4.0u**.
In the full form abc balances `y = XNOR(XNOR(x, rotl(x,d)), g)` — both the linear
`(x^xd)` path and the mux path are 4.0u, so the d-term is delay-free AND its removal
cannot beat the floor. **4.0u is a hard floor for any mux+xor series stage** in
`synth/mini.genlib`. Rotations are pure wiring → delay is rotation-independent, so
no (s,a,b,d) choice can fix it. DESIGN.md's 3.7u/stage estimate (from the 5-round
family average) was optimistic vs the measured 4.0u isolated stage.

## What was tried

1. Full stage as specified → 4.0u (>3.3u budget).
2. Instructed compression (remove final `^ rotl(x,d)`) → 4.0u, no improvement.
3. "Fusing": analyzed — no gate-level fusion below MUX2+XOR2 exists for the
   `x ^ mux(...)` function in this library (XOR2 2.0u is already the optimal XOR).
4. Full 3-stage with best-case compressed form → 11.8u, confirming >10u strict.

Dropping the x-bypass XOR as well (pure MUX2, 2.0u/stage) would fit the budget but
ceases to be MUXD — that design space is V3's lane (4-stage MUX2 network), not V2.

## Model

[model_muxd3.py](model_muxd3.py): bit-exact vectorized 3-stage MUXD model.
Self-check: 200/200 vectors match the scalar reference. Never Fisher-screened
(cost gate hit first, per process order).

## Scope of the kill (O145)

Kills ONLY the 3-stage MUXD variant under the <10u goal. NOT a claim about 3-stage
MUXD quality (never screened), V3, or a future sub-4u MUXD-like stage.
