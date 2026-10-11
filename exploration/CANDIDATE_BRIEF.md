# Design-space exploration — candidate brief (v3, 2026-10-01)

## The hard constraint

Pipeline **latency** ≤ one 64×64 multiplier delay, 1/cycle throughput, **2–4 stages**.
Since pipelining can't beat combinational critical path + register overhead:

- **Combinational critical path ≤ 0.90 × D_mult**, D_mult = **49.2 unit-delays**
  (reference `mul64.v`, measured twice — stable). **Bar: crit ≤ 44.3.** Anything
  above is OUT regardless of statistics. No exceptions.
- **2–4 pipeline stages** at natural block boundaries; S × T_clk ≤ 49.2 with
  T_clk = max_stage × 1.10 (10% clk-to-q+setup+skew **assumption**, always labeled).

## Measured primitive delays (exploration/prim/, same -fast flow, ratio to 49.2)

| primitive | crit | ratio | verdict for critical-path use |
|---|---|---|---|
| 64×64→64 variable mult (reference) | 49.2 | 1.000 | FORBIDDEN (is the bar) |
| 64-bit × dense **constant** mult | 46.2 | 0.939 | FORBIDDEN alone (0.94× before any surrounding logic) |
| 32×32→32 variable mult | 39.6 | 0.805 | 1 use max, barely |
| 32-bit × constant mult | 35.7 | 0.726 | 1 use + light logic OK |
| 16×16→16 variable mult | 30.2 | 0.614 | OK |
| 16-bit × constant mult | 27.7 | 0.563 | OK |
| 32-bit add | 16.0 | 0.325 | expensive; ≤2 sequential |
| 64-bit xorshift | 2.0 | 0.041 | free-ish |
| PRESENT SPN round (sbox+perm+keyxor) | ~6.1 | 0.124 | ≤7 rounds |

**Caveat (write this in the report):** ABC `-fast` does no Booth/CSD recoding, so it
systematically overprices constant multipliers vs a production flow. Probed:
CSD(23 nonzero digits) + balanced CPA adder tree = 67.1 (1.36×) — WORSE than
behavioral, because ABC maps each tree adder as a full carry-propagate adder.
A hand-built Wallace/CSA tree was not attempted (beyond screening scope; and a
64-bit multiply's inherent depth is ~6 FA levels + CPA ≈ 40–45 for the multiply
ALONE, leaving no budget for surrounding logic). Conclusion: no 64-bit multiply
of any kind fits in 0.9× in this flow. In a production flow with Booth/CSD this
family would price ~0.6–0.7× — note it as a P&R-stage caveat, not a screen input.

## What this kills (do not re-litigate without new measurements)

- 12-round PRESENT SPN (73.6, 1.50×): rejected definitively, statistical reference only.
- Keyed SplitMix/Murmur ARX with 64-bit mults (~2×): out on delay.
- 2-stage 32-bit multi-lane (2×39.6+…): out — but D1 measures one instance to
  document it instead of asserting it.
- 64-bit const-mult hybrids: out (46.2 alone).

## The actual frontier (what can fit in 44.3 units)

1. 6–7 round SPN, PRESENT-class round (~6.1/round) → 36–43.
2. 4-round SPN with stronger xor-linear layer (~10/round) → ~40.
3. 2-round add + xor-linear (~22/round) → ~44, boundary.
4. Single 32-bit const mult + xor cross-mix → ~40.
5. 6–7 round Feistel, S-box F (~5/round) → 30–40.
6. 8-round Feistel, xor-only F (~4/round) → ~32 (crypto-weak by construction).

## Proven bijective building blocks (use only these; no unproven structures)

- `x ^= k`, `x += k` (mod 2^n), `x *= C` with **C odd** (assert in model),
  `x ^= x>>s`, rotl/rotr, bit-permutations, bijective S-boxes (assert distinct).
- **3-term xor-linear:** `L(x) = x ^ ROTL(x,r) ^ ROTL(x,s)` is bijective for ALL
  distinct nonzero r,s. Proof: over GF(2), L ↔ polynomial 1+x^r+x^s;
  (1+x^r+x^s)(1) = 1 ≠ 0 so x+1 ∤ it, and x^64+1 = (x+1)^64 has no other factor.
  **2-term `x ^ ROTL(x,r)` is NOT bijective** (all-ones → 0) — NEVER use it.
- Feistel round `(L,R)->(R, L^F(R,rk))`: bijective for ANY F (fixed rk).
- Multi-lane cross-mix must be Feistel-structured (sequential half-steps), never
  simultaneous `(a,b)->(a^f(b), b^g(a))`.
- One-line construction argument required per candidate (see RESULT format).

## Directories and shared tools (`~/workspace/mix/exploration/`)

- `screen_lib.py` — **read before writing any model.** `screen(fn, name)` is the
  identical protocol (10 keys, N=2^18; scenarios: SEQ, PTR-j8/j16, MPOW2 12 cfgs,
  HIGH-ONLY, DESC ×2, POW2 11 cfgs, STRIDE-3, STRIDE-FIB, SINGLE-BIT 64-set,
  KEY-SWEEP 128×64; reductions Lemire X∈{10,1000,2^32} exact / mask m∈{8,32} /
  mod y∈{7,1000} exact-preimage on SEQ and PTR-j8).
  **PASS iff every scenario's worst per-bit |z|<4.0 AND every reduction |z|<4.5**,
  else FLAG (record numbers + WHICH scenarios flagged — a flag is a screen
  signal, not a verdict). Result dict carries `per_scenario_pb`,
  `per_scenario_red`, `flagged_pb_scenarios`, `flagged_red_scenarios`.
  Notes: k=63 skipped (period-2, degenerate for any function); strided configs
  deduplicated to their period; mask-32 = max(chi2 lo16, chi2 hi16, collision z)
  (2^32-bin chi2 infeasible + degenerate — documented substitution).
  Multiplicity note: ~27k per-bit cells ⇒ an isolated |z|∈[4.0,4.5) in one
  scenario may be null noise; a real weakness shows multiple scenarios/keys or
  large |z|. Report the numbers; do not "adjust" the bar.
- `check_model_equiv(scalar, np_fn, name)` and `bijectivity_spotcheck(fn, name)`
  (3 keys × 200k, zero collisions tolerated): **required for every candidate**.
- `present_perm_np` (fast PRESENT pLayer, verified), `sbox16_np(x, table)` provided.
- `run_synth.py <verilog> <top> <workdir>`: EXACT -fast flow mirror (yosys →
  `abc -fast -genlib mini.genlib`), then BOTH `analyze.py` and hardened
  `analyze2.py` (resolves `assign` incl. vector slices, ERRORS on unknown cells,
  topological crit path). Must agree or the number is untrusted. Re-measures the
  mul64 reference each run; prints `RESULT ... delay_ratio=...`.
- `check_rtl.py <dotted.model.fn> <rtl.v> <top> <workdir> [nvec=64]`: iverilog
  model-vs-RTL. vvp ≈ 0.5 s/vector on SPN-class netlists (measured, inherent) —
  64 vectors ≈ 30–60 s; don't raise nvec casually.
- `prim/`: primitive delay survey. `CANDIDATE_BRIEF.md`: this file.

## Per-candidate deliverables

1. `models/<name>.py` with `mix_<name>_np(val, key)` (+ scalar for equiv check).
2. `rtl/<name>.v`, top `<name>`: EXACTLY
   `module <name>(input wire [63:0] val, input wire [63:0] key, output wire [63:0] out);`
   combinational. S-boxes via `case` (ABC optimizes) or minimized SOP — note which.
3. `results/<name>/` work dirs.
4. RESULT block (format below) pasted into your final report to me.

## Pipeline partition (ONLY if delay_ratio ≤ 0.90 AND screen PASS)

1. 2–4 stages at natural block boundaries; state cut points.
2. Synthesize EACH stage standalone (`run_synth.py`) → per-stage crits.
3. T_clk = max_stage × 1.10 (labeled ASSUMPTION); latency = S × T_clk ≤ 49.2.
4. Report stages, per-stage crits, T_clk, latency, margin.

## RESULT block format

```
CANDIDATE <name>
  construction: <one paragraph: ops, key schedule, stage count>
  bijectivity: <one-line argument using only the proven blocks above>
  model: exploration/models/<f>.py::mix_<name>_np  (scalar==vectorized: OK)
  rtl: exploration/rtl/<f>.v top=<name>  (rtlcheck: 64/64 PASS)
  spotcheck: OK (3x200k, no collisions)
  screen: worst_perbit_z=<z> @ scen=<s> key=<hex> bit=<b> | worst_red_z=<z> @ scen=<s>
          flagged_pb=<scenarios or none> flagged_red=<scenarios or none> verdict=<PASS|FLAG>
  synth: cells=<c> area=<a> crit=<d> delay_ratio=<r> area_ratio=<ra> (ref 49.2)
  pipeline: <OUT-on-delay> | S=<s> cuts=<...> stage_crits=[..] T_clk=<t> latency=<l> margin=<m>
```

## Candidate grid

### Batch A — SPN (agent A, 8 candidates)
Default key schedule: `rk[i] = ROTL64(key, 13*(i+1)) ^ RC[i]`, `RC[i]=(i+1)*0x9E3779B97F4A7C15`;
`x = val ^ key`; final whitening `out = x ^ rk[R]`.
- A1 `spn7_present`: 7-round PRESENT S-box + PRESENT pLayer. (~43, boundary probe)
- A2 `spn6_present`: 6-round PRESENT. (control — expect statistical FLAG)
- A3 `spn7_gift`: GIFT S-box + PRESENT pLayer, 7 rounds.
- A4 `spn6_gift`: GIFT S-box + PRESENT pLayer, 6 rounds.
- A5 `spn7_skinny`: SKINNY 4-bit S-box + PRESENT pLayer, 7 rounds.
- A6 `spn7_present_ks2`: 7-round PRESENT, `rk[i]=ROTL64(key,13*(i+1))^ROTL64(key,29*(i+1))^RC[i]`.
- A7 `spn2_aes8`: 2 rounds: `x^=rk[i]; x=AES8(x); x^=L(x)` with `L(x)=x^ROTL64(x,13)^ROTL64(x,41)`;
  whitening. AES S-box = FIPS-197 table (look up; assert 256 distinct).
- A8 `spn4_xorlin`: 4 rounds: `x^=rk[i]; x=PRESENT16(x); x^=L(x)`, same L; whitening.
S-box tables: PRESENT `C 5 6 B 9 0 A D 3 E F 8 4 7 1 2` (trusted).
GIFT `1 A 4 C 6 F 3 9 2 D B 7 5 0 8 E`, SKINNY `C 6 9 0 1 A 7 B 3 E F 8 D 4 5 2`:
VERIFY against a primary source (web search) and assert 16 distinct. We borrow
the tables applied to contiguous nibbles — NOT the full ciphers; their published
bounds do not transfer. Say so in the construction line.

### Batch B — 64-bit ARX / single-mult (agent B, 4 candidates)
- B1 `add2r_a`: `x=val^key;` 2× { `t=x+rk[i]; x=t^ROTL64(t,13)^ROTL64(t,41)` };
  `out=x^rk[2]`; `rk[i]=ROTL64(key,17*(i+1))^RC[i]`. (~46, boundary probe)
- B2 `add2r_b`: same, rotations (29,53), rk rotation 23.
- B3 `m32_1stage_a`: `a=val[31:0]^key[31:0]; b=val[63:32]^key[63:32];`
  `a1=a*32'h9E3779B1; b1=b^a1; a2=a1^ROTL32(b1,11); b2=b1^ROTL32(a2,17)^key[31:0];`
  `out={b2,a2}`. (~40)
- B4 `m32_1stage_b`: same, C=`32'h85EBCA77`, rotations (7,19), final xor `key[63:32]`.
Bijectivity: B1/B2 = add (bij) + 3-term L (bij, proven above); B3/B4 = odd const
mult (bij) + Feistel-structured xor steps (bij). Assert C odd in the model.

### Batch C — short Feistel, 32-bit halves (agent C, 4 candidates)
`L=val[31:0], R=val[63:32]`; `L0=L^key[31:0], R0=R^key[63:32]`;
round `(L,R)->(R, L^F(R,rk[i]))`;
`rk[i]=ROTL32(key[31:0],3*(i+1))^ROTL32(key[63:32],5*(i+1))^((i+1)*0x9E3779B9 mod 2^32)`;
no final swap; `out={Rn^ROTL32(key[63:32],7), Ln^ROTL32(key[31:0],7)}`.
- C1 `feistel6_sbox`: 6 rounds, `F(x,rk)=P32(SBOX8(x^rk))`, 8× PRESENT S-box,
  `P32(i)=8*i mod 31 (i<31), P32(31)=31` (assert 32 distinct).
- C2 `feistel7_sbox`: 7 rounds, same F. (boundary)
- C3 `feistel8_xor`: 8 rounds, `F(x,rk)=(x^rk)^ROTL32(x,7)^ROTL32(x,19)`.
  Near-affine F — cryptographically weak BY CONSTRUCTION; included to map the
  boundary. Say so in the construction line.
- C4 `feistel6_giftsbox`: 6 rounds, F with GIFT S-box.

### Batch D — multi-lane residual probes (agent D, 3 candidates)
- D1 `lane2_s2_const`: 2 stages; per stage `a*=32'h9E3779B1, b*=32'h85EBCA77`
  (parallel const mults) then Feistel cross `t=a^ROTL32(b,11); b^=ROTL32(t,17); a=t`
  then `a^=RCa[i]; b^=RCb[i]`. Expect ~1.6× → OUT; run once to DOCUMENT, not assert.
- D2 `lane2_s1_const`: single stage (mults + TWO sequential Feistel crosses,
  rotations (11,17) then (7,19)). (~44, boundary)
- D3 `lane4_s1_const`: single stage, four 16-bit lanes `*= 16'h9E37/7F4B/85EB/C2B9`
  (all odd — assert; 0x7F4B = brief's original 0x7F4A corrected, 0x7F4A is even), Feistel cross on pairs (a,b),(c,d), free lane rotate.
  (~32)

## Rules

- Read-only outside `exploration/`. Do not touch `rtl/`, `synth/`, or test files.
- Do not modify `screen_lib.py`, `run_synth.py`, `analyze2.py`, `check_rtl.py`.
  Bug reports with reproductions go to me; I fix centrally.
- Do not invent tables/permutations from memory — verify GIFT/SKINNY/AES tables
  and every permutation against a primary source; assert bijectivity in the model.
- Use `screen()` as-is (do not sub-sample scenarios or keys). Do not declare winners.
  If delay_ratio > 0.90, mark OUT and move on — no rescue attempts.
- Full scenario catalog is at `~/workspace/mix/scenarios.md` (your screen covers
  the triage subset; SMALL-N, GRAY, UPSTREAM, BYTE-REP, SPARSE-HD and the full
  reduction grid run in the FINAL battery on finalists only — not your stage).
